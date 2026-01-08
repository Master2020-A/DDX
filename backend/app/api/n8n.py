"""
API endpoints para integración con N8N
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
import secrets
import httpx
import os

from app.api.dependencies import get_db, get_current_user, get_current_admin
from app.models.usuario import Usuario
from app.models.n8n_config import N8NConfig, N8NEventLog
from app.schemas.n8n import (
    N8NConfigCreate,
    N8NConfigUpdate,
    N8NConfigResponse,
    N8NConfigStats,
    N8NEventLogResponse,
    WebhookTestRequest,
    WebhookTestResponse,
    N8NAPIKeyGenerate,
    N8NAPIKeyResponse,
    EventosDisponiblesResponse,
    EventoDisponible,
    N8NWorkflowsStatus,
    N8NExecutionsStatus,
)

from app.services.n8n_webhook_service import n8n_webhook_service

router = APIRouter(tags=["N8N Integration"])


# ========== Configuración ==========


@router.post(
    "/config", response_model=N8NConfigResponse, status_code=status.HTTP_201_CREATED
)
async def crear_configuracion_n8n(
    config: N8NConfigCreate,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin),
):
    """
    Crear configuración de N8N (solo administradores)
    """
    # Verificar si ya existe una configuración activa
    result = await db.execute(select(N8NConfig).filter(N8NConfig.activo == True))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una configuración activa de N8N",
        )

    # Generar API key
    api_key = f"n8n_{secrets.token_urlsafe(32)}"

    # Crear configuración
    n8n_config = N8NConfig(
        **config.dict(), api_key=api_key, created_by=current_admin.id
    )

    db.add(n8n_config)
    await db.commit()
    await db.refresh(n8n_config)

    return n8n_config


@router.get("/config", response_model=N8NConfigResponse)
async def obtener_configuracion_n8n(
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener configuración activa de N8N
    """
    result = await db.execute(select(N8NConfig).filter(N8NConfig.activo == True))
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay configuración de N8N activa",
        )

    return config


@router.put("/config/{config_id}", response_model=N8NConfigResponse)
async def actualizar_configuracion_n8n(
    config_id: UUID,
    config_update: N8NConfigUpdate,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin),
):
    """
    Actualizar configuración de N8N (solo administradores)
    """
    result = await db.execute(select(N8NConfig).filter(N8NConfig.id == config_id))
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada"
        )

    # Actualizar campos
    for field, value in config_update.dict(exclude_unset=True).items():
        setattr(config, field, value)

    await db.commit()
    await db.refresh(config)

    return config


@router.delete("/config/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_configuracion_n8n(
    config_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin),
):
    """
    Eliminar configuración de N8N (solo administradores)
    """
    result = await db.execute(select(N8NConfig).filter(N8NConfig.id == config_id))
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada"
        )

    db.delete(config)
    await db.commit()


@router.get("/config/stats", response_model=N8NConfigStats)
async def obtener_estadisticas_n8n(
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener estadísticas de N8N
    """
    result = await db.execute(select(N8NConfig).filter(N8NConfig.activo == True))
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay configuración de N8N activa",
        )

    tasa_exito = 0.0
    if config.total_eventos_enviados > 0:
        tasa_exito = (
            config.total_eventos_exitosos / config.total_eventos_enviados
        ) * 100

    return N8NConfigStats(
        total_eventos_enviados=config.total_eventos_enviados,
        total_eventos_exitosos=config.total_eventos_exitosos,
        total_eventos_fallidos=config.total_eventos_fallidos,
        tasa_exito=round(tasa_exito, 2),
        ultimo_evento_enviado=config.ultimo_evento_enviado,
    )


# ========== API Keys ==========


@router.post("/api-key/generate", response_model=N8NAPIKeyResponse)
async def generar_api_key_n8n(
    request: N8NAPIKeyGenerate,
    db: Session = Depends(get_db),
    current_admin: Usuario = Depends(get_current_admin),
):
    """
    Generar nueva API key para N8N (solo administradores)
    """
    # Generar API key
    api_key = f"n8n_{secrets.token_urlsafe(32)}"

    # Crear o actualizar configuración
    result = await db.execute(select(N8NConfig).filter(N8NConfig.activo == True))
    config = result.scalar_one_or_none()

    if config:
        config.api_key = api_key
        config.nombre = request.nombre
        config.descripcion = request.descripcion
    else:
        config = N8NConfig(
            nombre=request.nombre,
            descripcion=request.descripcion,
            api_key=api_key,
            n8n_webhook_url=os.getenv(
                "N8N_WEBHOOK_URL", "http://localhost:5678/webhook"
            ),
            created_by=current_admin.id,
        )
        db.add(config)

    await db.commit()
    await db.refresh(config)

    return N8NAPIKeyResponse(
        api_key=api_key,
        mensaje="API key generada exitosamente",
        expires_at=None,
        usage="Usar en N8N HTTP Request headers: Authorization: Bearer {api_key}",
    )


@router.post("/api-key/regenerate", response_model=N8NAPIKeyResponse)
async def regenerar_api_key_n8n(
    db: Session = Depends(get_db), current_admin: Usuario = Depends(get_current_admin)
):
    """
    Regenerar API key existente (solo administradores)
    """
    result = await db.execute(select(N8NConfig).filter(N8NConfig.activo == True))
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay configuración de N8N activa",
        )

    # Generar nueva API key
    new_api_key = f"n8n_{secrets.token_urlsafe(32)}"
    config.api_key = new_api_key

    await db.commit()

    return N8NAPIKeyResponse(
        api_key=new_api_key,
        mensaje="API key regenerada exitosamente. La anterior ya no es válida.",
        expires_at=None,
        usage="Actualizar en N8N HTTP Request headers: Authorization: Bearer {api_key}",
    )


# ========== Event Logs ==========


@router.get("/events", response_model=List[N8NEventLogResponse])
async def obtener_eventos_n8n(
    evento_tipo: Optional[str] = None,
    exitoso: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener log de eventos enviados a N8N
    """
    stmt = select(N8NEventLog)

    if evento_tipo:
        stmt = stmt.filter(N8NEventLog.evento_tipo == evento_tipo)

    if exitoso is not None:
        stmt = stmt.filter(N8NEventLog.exitoso == exitoso)

    stmt = stmt.order_by(N8NEventLog.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    events = result.scalars().all()
    return events


@router.get("/events/{event_id}", response_model=N8NEventLogResponse)
async def obtener_evento_n8n(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener detalle de un evento específico
    """
    result = await db.execute(select(N8NEventLog).filter(N8NEventLog.id == event_id))
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado"
        )

    return event


# ========== Webhooks ==========


@router.post("/webhook/test", response_model=WebhookTestResponse)
async def probar_webhook_n8n(
    request: WebhookTestRequest, current_admin: Usuario = Depends(get_current_admin)
):
    """
    Probar envío de webhook a N8N (solo administradores)
    """
    import time

    test_payload = {
        "event": request.event_type,
        "data": request.test_data or {"mensaje": "Este es un evento de prueba"},
        "timestamp": "2024-01-01T00:00:00Z",
        "source": "DDX",
        "priority": "normal",
    }

    try:
        start_time = time.time()

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(request.url, json=test_payload)

        tiempo_respuesta = int((time.time() - start_time) * 1000)

        return WebhookTestResponse(
            exitoso=200 <= response.status_code < 300,
            mensaje=(
                "Webhook enviado exitosamente"
                if 200 <= response.status_code < 300
                else "Error al enviar webhook"
            ),
            codigo_http=response.status_code,
            tiempo_respuesta_ms=tiempo_respuesta,
            error=None if 200 <= response.status_code < 300 else response.text[:500],
        )

    except httpx.TimeoutException:
        return WebhookTestResponse(
            exitoso=False,
            mensaje="Timeout al enviar webhook",
            codigo_http=None,
            tiempo_respuesta_ms=None,
            error="Timeout después de 10 segundos",
        )
    except Exception as e:
        return WebhookTestResponse(
            exitoso=False,
            mensaje="Error al enviar webhook",
            codigo_http=None,
            tiempo_respuesta_ms=None,
            error=str(e),
        )


@router.get("/eventos-disponibles", response_model=EventosDisponiblesResponse)
async def obtener_eventos_disponibles(
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener lista de eventos disponibles para suscripción
    """
    eventos = [
        EventoDisponible(
            nombre="paciente.creado",
            descripcion="Se crea un nuevo paciente",
            categoria="Pacientes",
            prioridad_default="normal",
            ejemplo_payload={
                "paciente_id": "uuid",
                "nombre_completo": "Juan Pérez",
                "edad": 45,
            },
        ),
        EventoDisponible(
            nombre="paciente.actualizado",
            descripcion="Se actualiza información de un paciente",
            categoria="Pacientes",
            prioridad_default="normal",
            ejemplo_payload={
                "paciente_id": "uuid",
                "cambios": {"telefono": "555-1234"},
            },
        ),
        EventoDisponible(
            nombre="laboratorio.resultado_critico",
            descripcion="Resultado de laboratorio con valores críticos",
            categoria="Laboratorio",
            prioridad_default="critical",
            ejemplo_payload={
                "paciente_id": "uuid",
                "parametro": "Glucosa",
                "valor": 450,
                "nivel": "CRÍTICO",
            },
        ),
        EventoDisponible(
            nombre="laboratorio.completado",
            descripcion="Se completa un resultado de laboratorio",
            categoria="Laboratorio",
            prioridad_default="normal",
            ejemplo_payload={
                "resultado_id": "uuid",
                "paciente_id": "uuid",
                "tipo_prueba": "Hemograma",
            },
        ),
        EventoDisponible(
            nombre="cita.agendada",
            descripcion="Se agenda una nueva cita",
            categoria="Citas",
            prioridad_default="normal",
            ejemplo_payload={
                "cita_id": "uuid",
                "paciente_id": "uuid",
                "fecha": "2024-01-15",
                "hora": "10:00",
            },
        ),
        EventoDisponible(
            nombre="cita.cancelada",
            descripcion="Se cancela una cita",
            categoria="Citas",
            prioridad_default="normal",
            ejemplo_payload={
                "cita_id": "uuid",
                "paciente_id": "uuid",
                "motivo": "Paciente no disponible",
            },
        ),
        EventoDisponible(
            nombre="imagen.subida",
            descripcion="Se sube una nueva imagen médica",
            categoria="Imágenes",
            prioridad_default="normal",
            ejemplo_payload={
                "imagen_id": "uuid",
                "paciente_id": "uuid",
                "tipo": "Radiografía",
            },
        ),
        EventoDisponible(
            nombre="imagen.analisis_completado",
            descripcion="Se completa el análisis de una imagen",
            categoria="Imágenes",
            prioridad_default="high",
            ejemplo_payload={
                "imagen_id": "uuid",
                "tipo_analisis": "Segmentación 3D",
                "hallazgos": {},
            },
        ),
        EventoDisponible(
            nombre="estudio.completado",
            descripcion="Se completa un estudio especial (EKG, EEG, Eco)",
            categoria="Estudios Especiales",
            prioridad_default="normal",
            ejemplo_payload={
                "estudio_id": "uuid",
                "tipo_estudio": "EKG",
                "categoria": "Cardiología",
            },
        ),
        EventoDisponible(
            nombre="receta.emitida",
            descripcion="Se emite una receta médica",
            categoria="Recetas",
            prioridad_default="normal",
            ejemplo_payload={
                "receta_id": "uuid",
                "paciente_id": "uuid",
                "medicamentos": [],
            },
        ),
        EventoDisponible(
            nombre="telemedicina.consulta_iniciada",
            descripcion="Se inicia una consulta de telemedicina",
            categoria="Telemedicina",
            prioridad_default="normal",
            ejemplo_payload={
                "consulta_id": "uuid",
                "paciente_id": "uuid",
                "medico_id": "uuid",
            },
        ),
        EventoDisponible(
            nombre="diagnostico.generado",
            descripcion="Se genera un diagnóstico con IA",
            categoria="Diagnóstico",
            prioridad_default="high",
            ejemplo_payload={
                "diagnostico_id": "uuid",
                "diagnostico_principal": "Diabetes Tipo 2",
                "confianza": 0.95,
            },
        ),
    ]

    categorias = list(set([e.categoria for e in eventos]))

    return EventosDisponiblesResponse(
        total=len(eventos), categorias=sorted(categorias), eventos=eventos
    )


# ========== N8N Workflows Management ==========


@router.get("/workflows/status", response_model=N8NWorkflowsStatus)
async def obtener_estado_workflows(current_admin: Usuario = Depends(get_current_admin)):
    """
    Obtener estado de workflows de N8N (solo administradores)
    """
    n8n_api_url = os.getenv("N8N_API_URL", "http://localhost:5678/api/v1")
    n8n_api_key = os.getenv("N8N_API_KEY", "")

    if not n8n_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="N8N API key no configurada",
        )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{n8n_api_url}/workflows", headers={"X-N8N-API-KEY": n8n_api_key}
            )
            response.raise_for_status()
            workflows = response.json().get("data", [])

        active_count = len([w for w in workflows if w.get("active")])

        return N8NWorkflowsStatus(
            total=len(workflows),
            active=active_count,
            inactive=len(workflows) - active_count,
            workflows=workflows[:50],  # Limitar a 50
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error conectando con N8N API: {str(e)}",
        )


@router.get("/executions/recent", response_model=N8NExecutionsStatus)
async def obtener_ejecuciones_recientes(
    current_admin: Usuario = Depends(get_current_admin),
):
    """
    Obtener ejecuciones recientes de N8N (solo administradores)
    """
    n8n_api_url = os.getenv("N8N_API_URL", "http://localhost:5678/api/v1")
    n8n_api_key = os.getenv("N8N_API_KEY", "")

    if not n8n_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="N8N API key no configurada",
        )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{n8n_api_url}/executions",
                headers={"X-N8N-API-KEY": n8n_api_key},
                params={"limit": 100},
            )
            response.raise_for_status()
            executions = response.json().get("data", [])

        success_count = len(
            [e for e in executions if e.get("finished") and not e.get("stoppedAt")]
        )
        failed_count = len(
            [e for e in executions if e.get("stoppedAt") and not e.get("finished")]
        )
        running_count = len(
            [e for e in executions if not e.get("finished") and not e.get("stoppedAt")]
        )

        return N8NExecutionsStatus(
            total=len(executions),
            success=success_count,
            failed=failed_count,
            running=running_count,
            executions=executions[:50],  # Limitar a 50
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error conectando con N8N API: {str(e)}",
        )
