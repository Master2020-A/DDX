"""
Endpoints para API Pública y Marketplace
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from typing import List, Optional
from datetime import datetime, timedelta
import secrets
import hashlib
import hmac
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.usuario import Usuario
from app.models.api_publica import (
    APIKey,
    LogAPIPublica,
    Webhook,
    EntregaWebhook,
    Plugin,
    InstalacionPlugin,
    ResenaPlugin,
    TipoEvento,
    EstadoPlugin,
)
from app.schemas.api_publica import (
    APIKeyCreate,
    APIKeyResponse,
    APIKeyUpdate,
    WebhookCreate,
    WebhookResponse,
    WebhookUpdate,
    EntregaWebhookResponse,
    PluginCreate,
    PluginResponse,
    PluginUpdate,
    InstalacionPluginCreate,
    InstalacionPluginResponse,
    ResenaPluginCreate,
    ResenaPluginResponse,
    LogAPIPublicaResponse,
    EstadisticasAPI,
    EstadisticasMarketplace,
)

router = APIRouter(prefix="/api-publica", tags=["API Pública"])


# ============================================================================
# Utilidades
# ============================================================================


def generar_api_key() -> str:
    """Genera una API key única"""
    return f"ddx_{secrets.token_urlsafe(32)}"


def generar_secret() -> str:
    """Genera un secret para API key"""
    return secrets.token_urlsafe(48)


def hash_secret(secret: str) -> str:
    """Hashea el secret para almacenamiento"""
    return hashlib.sha256(secret.encode()).hexdigest()


def verificar_secret(secret: str, hash_almacenado: str) -> bool:
    """Verifica un secret contra su hash"""
    return hash_secret(secret) == hash_almacenado


async def verificar_api_key(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: AsyncSession = Depends(get_db),
) -> APIKey:
    """Verifica y retorna la API key"""
    result = await db.execute(
        select(APIKey).where(and_(APIKey.key == x_api_key, APIKey.activa == True))
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="API key inválida"
        )

    if not verificar_secret(x_api_secret, api_key.secret_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Secret inválido"
        )

    if api_key.expira_en and api_key.expira_en < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="API key expirada"
        )

    # Actualizar último uso
    api_key.ultimo_uso = datetime.utcnow()
    api_key.total_requests += 1
    await db.commit()

    return api_key


async def registrar_log_api(
    db: AsyncSession,
    api_key: APIKey,
    request: Request,
    metodo: str,
    endpoint: str,
    status_code: int,
    tiempo_ms: int,
    error: Optional[str] = None,
):
    """Registra un log de uso de la API"""
    log = LogAPIPublica(
        api_key_id=api_key.id,
        metodo=metodo,
        endpoint=endpoint,
        ip_origen=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        status_code=status_code,
        tiempo_respuesta_ms=tiempo_ms,
        error=error,
    )
    db.add(log)
    await db.commit()


# ============================================================================
# API Keys
# ============================================================================


@router.post("/keys", response_model=APIKeyResponse)
async def crear_api_key(
    data: APIKeyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crear nueva API key"""
    key = generar_api_key()
    secret = generar_secret()

    nueva_key = APIKey(
        nombre=data.nombre,
        descripcion=data.descripcion,
        key=key,
        secret_hash=hash_secret(secret),
        permisos=data.permisos,
        scopes=data.scopes,
        rate_limit_por_minuto=data.rate_limit_por_minuto,
        rate_limit_por_dia=data.rate_limit_por_dia,
        webhook_url=data.webhook_url,
        eventos_suscritos=data.eventos_suscritos,
        expira_en=data.expira_en,
        ip_whitelist=data.ip_whitelist,
        entorno=data.entorno,
    )

    db.add(nueva_key)
    await db.commit()
    await db.refresh(nueva_key)

    # Retornar con el secret (solo esta vez)
    response = APIKeyResponse.from_orm(nueva_key)
    response.secret = secret
    return response


@router.get("/keys", response_model=List[APIKeyResponse])
async def listar_api_keys(
    activa: Optional[bool] = None,
    entorno: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar API keys"""
    query = select(APIKey)

    if activa is not None:
        query = query.where(APIKey.activa == activa)
    if entorno:
        query = query.where(APIKey.entorno == entorno)

    query = query.order_by(desc(APIKey.created_at))
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/keys/{key_id}", response_model=APIKeyResponse)
async def obtener_api_key(
    key_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener detalles de una API key"""
    result = await db.execute(select(APIKey).where(APIKey.id == key_id))
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API key no encontrada"
        )

    return api_key


@router.put("/keys/{key_id}", response_model=APIKeyResponse)
async def actualizar_api_key(
    key_id: UUID,
    data: APIKeyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualizar API key"""
    result = await db.execute(select(APIKey).where(APIKey.id == key_id))
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API key no encontrada"
        )

    for field, value in data.dict(exclude_unset=True).items():
        setattr(api_key, field, value)

    await db.commit()
    await db.refresh(api_key)
    return api_key


@router.delete("/keys/{key_id}")
async def eliminar_api_key(
    key_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Eliminar API key"""
    result = await db.execute(select(APIKey).where(APIKey.id == key_id))
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API key no encontrada"
        )

    await db.delete(api_key)
    await db.commit()
    return {"message": "API key eliminada"}


@router.post("/keys/{key_id}/regenerar-secret", response_model=APIKeyResponse)
async def regenerar_secret(
    key_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Regenerar secret de una API key"""
    result = await db.execute(select(APIKey).where(APIKey.id == key_id))
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API key no encontrada"
        )

    nuevo_secret = generar_secret()
    api_key.secret_hash = hash_secret(nuevo_secret)

    await db.commit()
    await db.refresh(api_key)

    response = APIKeyResponse.from_orm(api_key)
    response.secret = nuevo_secret
    return response


# ============================================================================
# Webhooks
# ============================================================================


@router.post("/webhooks", response_model=WebhookResponse)
async def crear_webhook(
    data: WebhookCreate,
    api_key: APIKey = Depends(verificar_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Crear nuevo webhook"""
    webhook_secret = secrets.token_urlsafe(32)

    nuevo_webhook = Webhook(
        api_key_id=api_key.id,
        nombre=data.nombre,
        url=data.url,
        secret=webhook_secret,
        eventos=data.eventos,
        max_reintentos=data.max_reintentos,
        timeout_segundos=data.timeout_segundos,
        headers_personalizados=data.headers_personalizados,
    )

    db.add(nuevo_webhook)
    await db.commit()
    await db.refresh(nuevo_webhook)
    return nuevo_webhook


@router.get("/webhooks", response_model=List[WebhookResponse])
async def listar_webhooks(
    activo: Optional[bool] = None,
    api_key: APIKey = Depends(verificar_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Listar webhooks"""
    query = select(Webhook).where(Webhook.api_key_id == api_key.id)

    if activo is not None:
        query = query.where(Webhook.activo == activo)

    result = await db.execute(query)
    return result.scalars().all()


@router.get(
    "/webhooks/{webhook_id}/entregas", response_model=List[EntregaWebhookResponse]
)
async def listar_entregas_webhook(
    webhook_id: UUID,
    limite: int = 50,
    api_key: APIKey = Depends(verificar_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Listar entregas de un webhook"""
    result = await db.execute(
        select(EntregaWebhook)
        .where(EntregaWebhook.webhook_id == webhook_id)
        .order_by(desc(EntregaWebhook.timestamp))
        .limit(limite)
    )
    return result.scalars().all()


# ============================================================================
# Marketplace - Plugins
# ============================================================================


@router.post("/marketplace/plugins", response_model=PluginResponse)
async def publicar_plugin(
    data: PluginCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Publicar nuevo plugin en marketplace"""
    # Verificar que el slug no exista
    result = await db.execute(select(Plugin).where(Plugin.slug == data.slug))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un plugin con ese slug",
        )

    nuevo_plugin = Plugin(**data.dict())
    db.add(nuevo_plugin)
    await db.commit()
    await db.refresh(nuevo_plugin)
    return nuevo_plugin


@router.get("/marketplace/plugins", response_model=List[PluginResponse])
async def listar_plugins(
    categoria: Optional[str] = None,
    tag: Optional[str] = None,
    verificado: Optional[bool] = None,
    busqueda: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """Listar plugins del marketplace"""
    query = select(Plugin).where(Plugin.estado == "aprobado")

    if categoria:
        query = query.where(Plugin.categoria == categoria)
    if tag:
        query = query.where(Plugin.tags.contains([tag]))
    if verificado is not None:
        query = query.where(Plugin.verificado == verificado)
    if busqueda:
        query = query.where(
            or_(
                Plugin.nombre.ilike(f"%{busqueda}%"),
                Plugin.descripcion.ilike(f"%{busqueda}%"),
            )
        )

    query = query.order_by(desc(Plugin.descargas)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/marketplace/plugins/{slug}", response_model=PluginResponse)
async def obtener_plugin(slug: str, db: AsyncSession = Depends(get_db)):
    """Obtener detalles de un plugin"""
    result = await db.execute(select(Plugin).where(Plugin.slug == slug))
    plugin = result.scalar_one_or_none()

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Plugin no encontrado"
        )

    return plugin


@router.post(
    "/marketplace/plugins/{plugin_id}/instalar",
    response_model=InstalacionPluginResponse,
)
async def instalar_plugin(
    plugin_id: UUID,
    data: InstalacionPluginCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Instalar un plugin"""
    # Verificar que el plugin existe
    result = await db.execute(select(Plugin).where(Plugin.id == plugin_id))
    plugin = result.scalar_one_or_none()

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Plugin no encontrado"
        )

    # Crear instalación
    instalacion = InstalacionPlugin(
        plugin_id=plugin_id,
        configuracion=data.configuracion,
        api_key_id=data.api_key_id,
        version_instalada=plugin.version,
    )

    db.add(instalacion)

    # Actualizar estadísticas del plugin
    plugin.descargas += 1
    plugin.instalaciones_activas += 1

    await db.commit()
    await db.refresh(instalacion)
    return instalacion


@router.post(
    "/marketplace/plugins/{plugin_id}/resenas", response_model=ResenaPluginResponse
)
async def crear_resena(
    plugin_id: UUID, data: ResenaPluginCreate, db: AsyncSession = Depends(get_db)
):
    """Crear reseña de un plugin"""
    resena = ResenaPlugin(**data.dict())
    db.add(resena)

    # Actualizar calificación promedio del plugin
    result = await db.execute(select(Plugin).where(Plugin.id == plugin_id))
    plugin = result.scalar_one_or_none()

    if plugin:
        plugin.total_calificaciones += 1
        total_puntos = (
            plugin.calificacion_promedio * (plugin.total_calificaciones - 1)
        ) + data.calificacion
        plugin.calificacion_promedio = round(total_puntos / plugin.total_calificaciones)

    await db.commit()
    await db.refresh(resena)
    return resena


@router.get("/marketplace/estadisticas", response_model=EstadisticasMarketplace)
async def obtener_estadisticas_marketplace(db: AsyncSession = Depends(get_db)):
    """Obtener estadísticas del marketplace"""
    # Total de plugins
    result = await db.execute(select(func.count(Plugin.id)))
    total_plugins = result.scalar()

    # Plugins activos
    result = await db.execute(
        select(func.count(Plugin.id)).where(Plugin.estado == "aprobado")
    )
    plugins_activos = result.scalar()

    # Plugins verificados
    result = await db.execute(
        select(func.count(Plugin.id)).where(
            and_(Plugin.verificado == True, Plugin.estado == "aprobado")
        )
    )
    plugins_verificados = result.scalar()

    # Total descargas
    result = await db.execute(select(func.sum(Plugin.descargas)))
    total_descargas = result.scalar() or 0

    # Total instalaciones
    result = await db.execute(select(func.sum(Plugin.instalaciones_activas)))
    total_instalaciones = result.scalar() or 0

    # Plugins populares
    result = await db.execute(
        select(Plugin)
        .where(Plugin.estado == "aprobado")
        .order_by(desc(Plugin.descargas))
        .limit(10)
    )
    plugins_populares = result.scalars().all()

    # Categorías
    result = await db.execute(
        select(Plugin.categoria, func.count(Plugin.id))
        .where(Plugin.estado == "aprobado")
        .group_by(Plugin.categoria)
    )
    categorias = [{"categoria": cat, "total": total} for cat, total in result.all()]

    return EstadisticasMarketplace(
        total_plugins=total_plugins,
        plugins_activos=plugins_activos,
        plugins_verificados=plugins_verificados,
        total_descargas=total_descargas,
        total_instalaciones=total_instalaciones,
        plugins_populares=plugins_populares,
        categorias=categorias,
    )


# ============================================================================
# Logs y Estadísticas
# ============================================================================


@router.get("/logs", response_model=List[LogAPIPublicaResponse])
async def listar_logs(
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    limite: int = 100,
    api_key: APIKey = Depends(verificar_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Listar logs de uso de la API"""
    query = select(LogAPIPublica).where(LogAPIPublica.api_key_id == api_key.id)

    if fecha_desde:
        query = query.where(LogAPIPublica.timestamp >= fecha_desde)
    if fecha_hasta:
        query = query.where(LogAPIPublica.timestamp <= fecha_hasta)

    query = query.order_by(desc(LogAPIPublica.timestamp)).limit(limite)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/estadisticas", response_model=EstadisticasAPI)
async def obtener_estadisticas(
    dias: int = 7,
    api_key: APIKey = Depends(verificar_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Obtener estadísticas de uso de la API"""
    fecha_inicio = datetime.utcnow() - timedelta(days=dias)

    # Total requests
    result = await db.execute(
        select(func.count(LogAPIPublica.id)).where(
            and_(
                LogAPIPublica.api_key_id == api_key.id,
                LogAPIPublica.timestamp >= fecha_inicio,
            )
        )
    )
    total_requests = result.scalar()

    # Requests exitosos
    result = await db.execute(
        select(func.count(LogAPIPublica.id)).where(
            and_(
                LogAPIPublica.api_key_id == api_key.id,
                LogAPIPublica.timestamp >= fecha_inicio,
                LogAPIPublica.status_code < 400,
            )
        )
    )
    requests_exitosos = result.scalar()

    # Tiempo promedio
    result = await db.execute(
        select(func.avg(LogAPIPublica.tiempo_respuesta_ms)).where(
            and_(
                LogAPIPublica.api_key_id == api_key.id,
                LogAPIPublica.timestamp >= fecha_inicio,
            )
        )
    )
    tiempo_promedio = result.scalar() or 0

    return EstadisticasAPI(
        total_requests=total_requests,
        requests_exitosos=requests_exitosos,
        requests_fallidos=total_requests - requests_exitosos,
        tiempo_respuesta_promedio_ms=round(tiempo_promedio, 2),
        endpoints_mas_usados=[],
        errores_comunes=[],
        uso_por_dia=[],
    )
