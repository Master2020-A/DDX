from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from collections import defaultdict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from app.core.config import settings
from app.core.database import engine, AsyncSessionLocal

# ✅ registra mappers (Institucion/Workflow/etc) para evitar errores de relationship()
import app.models  # noqa: F401

# Routers "legacy/manuales" (app.routers.*)
from app.routers.catalogos_cp import router as catalogos_cp_router
from app.routers import interoperabilidad_metricas
from app.websocket.endpoints import websocket_telemedicina_endpoint


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando DDX Medical API...")

    # Cargar módulos generados por DDX Studio
    try:
        from app.services.module_deployer import ModuleDeployer

        deployer = ModuleDeployer()
        loaded = deployer.load_generated_routes(app)
        if loaded:
            logger.info(f"✅ Cargados {len(loaded)} módulos generados por DDX Studio")
    except Exception as e:
        logger.warning(f"⚠️ No se pudieron cargar módulos generados: {e}")

    yield
    logger.info("👋 Cerrando DDX Medical API...")
    await engine.dispose()


app = FastAPI(
    title="DDX Medical API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ✅ CORS correcto: lista de orígenes, NO string
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    ms = (datetime.now() - start_time).total_seconds() * 1000
    response.headers["X-Process-Time"] = f"{ms:.2f}ms"

    if response.status_code >= 400 or settings.DEBUG:
        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} ({ms:.2f}ms)"
        )
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({"field": field, "message": error["msg"], "type": error["type"]})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Error de validación", "errors": errors},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error no manejado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500, content={"detail": "Error interno del servidor"}
    )


# ============================================================
# Carga segura de routers (evita cargar el mismo módulo 2 veces)
# ============================================================

loaded_routers: list[str] = []
_loaded_set: set[str] = set()


def safe_include(module_path: str, prefix: str, tag: str):
    """
    Carga módulos app.api.<name> que exportan variable `router`.
    Si falla, NO tumba toda la API, pero sí imprime traceback completo.
    Evita cargar el mismo módulo dos veces.
    """
    if module_path in _loaded_set:
        logger.warning(f" Router ya cargado: {module_path} (skip)")
        return

    try:
        logger.debug(f"Intentando cargar: {module_path}")
        module = __import__(module_path, fromlist=["router"])
        logger.debug(f"Módulo importado: {module_path}")

        router = getattr(module, "router", None)
        if router is None:
            logger.warning(f"  {module_path} no exporta `router`")
            logger.info(f" Atributos del módulo: {dir(module)}")
            return

        logger.debug("Router obtenido, agregando a app...")

        app.include_router(router, prefix=prefix, tags=[tag])

        _loaded_set.add(module_path)
        loaded_routers.append(module_path)
        logger.debug(f"Router '{module_path}' cargado en {prefix}")

    except Exception as e:
        logger.error(f"⚠️  Error cargando router '{module_path}': {e}")
        logger.exception(f"⚠️  Traceback completo:")


# ============================================================
# Routers manuales/legacy (app.routers.*)
# IMPORTANTE: se montan con prefijos exclusivos para NO colisionar
# ============================================================

try:
    # Evita colisión con app.api.interoperabilidad (/api/interoperabilidad)
    app.include_router(
        interoperabilidad_metricas.router,
        prefix="/api/interoperabilidad-metricas",
        tags=["📊 Interoperabilidad Métricas (Legacy)"],
    )
    loaded_routers.append("app.routers.interoperabilidad_metricas")
    logger.debug(
        "Router interoperabilidad_metricas cargado en /api/interoperabilidad-metricas"
    )

except Exception:
    logger.exception("⚠️  Error cargando interoperabilidad_metricas")

try:
    # Evita colisión con app.api.catalogos (/api/catalogos)
    app.include_router(
        catalogos_cp_router, prefix="/api/catalogos", tags=["📚 Catálogos CP (Legacy)"]
    )

    loaded_routers.append("app.routers.catalogos_cp")
    logger.debug("Router catalogos_cp cargado en /api/catalogos")

except Exception:
    logger.exception("⚠️  Error cargando catalogos_cp")


# ============================================================
# Routers clave
# ============================================================

# ✅ Auth (usa SOLO uno para evitar duplicados en /api/auth)
safe_include("app.api.auth_minimal", "/api/auth", "🔐 Autenticación")

# DDX Studio
safe_include("app.api.ddx_studio", "/api/studio", "🎨 DDX Studio")

# Workflows: tu router debe traer prefix="/workflows", aquí se monta con "/api"
try:
    from app.api.workflows import router as workflows_router

    app.include_router(
        workflows_router,
        prefix="/api",
        tags=["🤖 Workflows & AI Agents"],
    )
    _loaded_set.add("app.api.workflows")
    loaded_routers.append("app.api.workflows")
    logger.debug("Router workflows cargado en /api (esperado /api/workflows)")

except Exception:
    logger.exception("⚠️  Error cargando workflows")

# Workflows Advanced (Versioning, A/B Testing, Loops, Subworkflows)
try:
    from app.api.workflow_advanced import router as workflow_advanced_router

    app.include_router(
        workflow_advanced_router,
        prefix="",
        tags=["🚀 Workflows Advanced"],
    )
    _loaded_set.add("app.api.workflow_advanced")
    loaded_routers.append("app.api.workflow_advanced")
    logger.debug("Router workflow_advanced cargado")

except Exception:
    logger.exception("⚠️  Error cargando workflow_advanced")


# ============================================================
# Carga dinámica del resto de routers
# ============================================================

routers_config = [
    # N8N Integration - Cargar primero para evitar timeout
    ("n8n", "/api/n8n", "🔄 N8N Integration"),
    ("n8n_workflows", "/api/n8n/workflows", "⚡ N8N Workflows"),
    # Routers principales
    ("pacientes", "/api/pacientes", "🏥 Pacientes"),
    ("consultas", "/api/consultas", "📋 Consultas"),
    ("telemedicina", "/api/telemedicina", "📹 Telemedicina"),
    ("diagnosticos", "/api/diagnosticos", "📊 Diagnósticos"),
    ("historias_clinicas", "/api/historiales", "📁 Historiales"),
    ("laboratorio", "/api/laboratorio", "🔬 Laboratorio"),
    ("tratamientos", "/api/tratamientos", "💊 Tratamientos"),
    ("imagenes", "/api/imagenes", "🖼️ Imágenes"),
    ("interconsultas", "/api/interconsultas", "🔄 Interconsultas"),
    ("hospitalizacion", "/api/hospitalizacion", "🏥 Hospitalización"),
    ("prediagnostico", "/api/prediagnostico", "🤖 Pre-diagnóstico"),
    ("analytics", "/api/analytics", "📈 Analytics"),
    ("search", "/api/search", "🔍 Búsqueda"),
    ("expedientes", "/api/expedientes", "📂 Expedientes"),
    ("notas_medicas", "/api/notas-medicas", "📝 Notas Médicas"),
    ("catalogos", "/api/catalogos", "📚 Catálogos"),
    ("security", "/api/security", "🔒 Seguridad"),
    ("backups", "/api/backups", "💾 Backups"),
    ("cumplimiento", "/api/cumplimiento", "✅ Cumplimiento"),
    ("integraciones", "/api/integraciones", "🔗 Integraciones"),
    ("portal_paciente", "/api/portal-paciente", "🏥 Portal del Paciente"),
    # IA Médica - el router ya trae prefix "/ia-medica", aquí solo "/api"
    ("ia_medica", "/api", "🧠 IA Médica"),
    ("estudios_especiales", "/api/estudios-especiales", "📋 Estudios Especiales"),
    ("app_movil", "/api/movil", "📱 App Móvil"),
    ("api_publica", "/api/publica", "🌐 API Pública"),
    ("instituciones", "/api/instituciones", "🏢 Multi-Tenancy"),
    ("interoperabilidad", "/api/interoperabilidad", "🔄 Interoperabilidad"),
    # Funcionalidades avanzadas de workflows
    ("marketplace", "/api/marketplace", "🛒 Marketplace"),
    ("collaboration", "/api/collaboration", "🤝 Colaboración"),
    ("llm", "/api/llm", "🤖 LLM"),
]

for mod, pref, tag in routers_config:
    safe_include(f"app.api.{mod}", pref, tag)

# ============================================================
# WebSocket Routes
# ============================================================
app.add_api_websocket_route(
    "/ws/telemedicina",
    websocket_telemedicina_endpoint,
)

# ============================================================
# Detección de endpoints duplicados (METHOD + PATH)
# ============================================================


def log_duplicate_routes():
    seen = defaultdict(list)

    for r in app.routes:
        if isinstance(r, APIRoute):
            for m in sorted(r.methods or []):
                seen[(m, r.path)].append(r)

    dups = {k: v for k, v in seen.items() if len(v) > 1}
    if not dups:
        logger.info("✅ No hay endpoints duplicados (METHOD+PATH).")
        return

    logger.warning("⚠️ Endpoints duplicados detectados (METHOD+PATH):")
    for (m, path), routes in sorted(dups.items()):
        logger.warning(f"  {m:6} {path}")
        for rr in routes:
            logger.warning(f"    - {rr.endpoint.__module__}.{rr.name}")


log_duplicate_routes()

logger.info(f"📦 {len(loaded_routers)} módulos cargados.")


@app.get("/", tags=["🏠 Sistema"])
async def root():
    return {
        "name": "DDX Medical API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "modules_loaded": loaded_routers,
    }


@app.get("/health", tags=["🏠 Sistema"])
async def health_check():
    db_status = "unknown"
    try:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text

            await session.execute(text("SELECT 1"))
            db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    return {"status": "ok", "db": db_status, "modules": loaded_routers}


if __name__ == "__main__":
    import uvicorn

    # Desactivar reload temporalmente para evitar reinicios constantes
    # Cambia a True si necesitas desarrollo con auto-reload
    ENABLE_RELOAD = False

    if ENABLE_RELOAD:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8612,
            reload=True,
            reload_excludes=[
                "*/generated/*",
                "*/app/models/generated/*",
                "*/app/api/generated/*",
                "*/__pycache__/*",
                "*.pyc",
            ],
            log_level="info",
        )
    else:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8612,
            reload=False,
            log_level="info",
        )
