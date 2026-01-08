"""
API Endpoints para Procesamiento de Lenguaje Natural (PLN)
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.usuario import Usuario
from app.services.transcripcion_voz_service import TranscripcionVozService
from app.services.extraccion_informacion_service import ExtraccionInformacionService
from app.services.resumen_clinico_service import ResumenClinicoService
from app.services.traduccion_medica_service import TraduccionMedicaService

router = APIRouter(tags=["Procesamiento de Lenguaje Natural"])


# ==================== MODELOS PYDANTIC ====================


class TranscripcionRequest(BaseModel):
    paciente_id: Optional[UUID] = None
    consulta_id: Optional[UUID] = None
    idioma: Optional[str] = None


class ExtraccionRequest(BaseModel):
    texto: str
    tipo_documento: str
    paciente_id: Optional[UUID] = None
    consulta_id: Optional[UUID] = None


class ResumenRequest(BaseModel):
    paciente_id: UUID
    tipo_resumen: str = "completo"
    periodo_dias: Optional[int] = None
    incluir_consultas: bool = True
    incluir_laboratorios: bool = True
    incluir_imagenes: bool = True
    incluir_medicamentos: bool = True


class TraduccionRequest(BaseModel):
    texto: str
    idioma_origen: str
    idioma_destino: str
    tipo_contenido: str = "texto_libre"
    especialidad: Optional[str] = None


class TerminoDiccionarioRequest(BaseModel):
    termino_es: str
    termino_en: str
    categoria: str
    definicion_es: Optional[str] = None
    definicion_en: Optional[str] = None
    termino_la: Optional[str] = None
    especialidad: Optional[str] = None
    codigo_cie10: Optional[str] = None
    codigo_snomed: Optional[str] = None


# ==================== TRANSCRIPCIÓN DE VOZ ====================


@router.post("/transcribir-audio")
async def transcribir_audio(
    archivo: UploadFile = File(...),
    paciente_id: Optional[str] = Form(None),
    consulta_id: Optional[str] = Form(None),
    idioma: Optional[str] = Form(None),
    extraer_informacion: bool = Form(False),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Transcribir audio a texto usando Whisper

    - **archivo**: Archivo de audio (mp3, wav, m4a, etc.)
    - **paciente_id**: ID del paciente (opcional)
    - **consulta_id**: ID de la consulta (opcional)
    - **idioma**: Código de idioma (es, en, etc.) - opcional
    - **extraer_informacion**: Si se debe extraer información médica automáticamente
    """

    try:
        # Leer contenido del archivo
        contenido = await archivo.read()

        service = TranscripcionVozService()

        # Convertir IDs de string a UUID si existen
        paciente_uuid = UUID(paciente_id) if paciente_id else None
        consulta_uuid = UUID(consulta_id) if consulta_id else None

        if extraer_informacion:
            resultado = await service.transcribir_y_extraer(
                archivo_audio=contenido,
                nombre_archivo=archivo.filename,
                paciente_id=paciente_uuid,
                medico_id=current_user.id,
                consulta_id=consulta_uuid,
                db=db,
            )
        else:
            resultado = await service.transcribir_audio(
                archivo_audio=contenido,
                nombre_archivo=archivo.filename,
                paciente_id=paciente_uuid,
                medico_id=current_user.id,
                consulta_id=consulta_uuid,
                idioma=idioma,
                db=db,
            )

        return resultado

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transcripciones/paciente/{paciente_id}")
async def obtener_transcripciones_paciente(
    paciente_id: UUID,
    limite: int = 10,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtener transcripciones de un paciente"""

    service = TranscripcionVozService()
    transcripciones = await service.obtener_transcripciones_paciente(
        paciente_id=paciente_id, db=db, limite=limite
    )

    return {"transcripciones": transcripciones}


# ==================== EXTRACCIÓN DE INFORMACIÓN ====================


@router.post("/extraer-informacion")
async def extraer_informacion(
    request: ExtraccionRequest,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Extraer información estructurada de texto médico

    - **texto**: Texto a analizar
    - **tipo_documento**: Tipo (nota_evolucion, historia_clinica, receta, etc.)
    - **paciente_id**: ID del paciente (opcional)
    - **consulta_id**: ID de la consulta (opcional)
    """

    try:
        service = ExtraccionInformacionService()

        resultado = await service.extraer_informacion(
            texto=request.texto,
            tipo_documento=request.tipo_documento,
            paciente_id=request.paciente_id,
            medico_id=current_user.id,
            consulta_id=request.consulta_id,
            db=db,
        )

        return resultado

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extraer-entidades")
async def extraer_entidades_nombradas(
    texto: str, current_user: Usuario = Depends(get_current_user)
):
    """
    Extraer solo entidades nombradas médicas del texto

    - **texto**: Texto a analizar
    """

    try:
        service = ExtraccionInformacionService()
        entidades = await service.extraer_entidades_nombradas(texto)

        return entidades

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== GENERACIÓN DE RESÚMENES ====================


@router.post("/generar-resumen")
async def generar_resumen_clinico(
    request: ResumenRequest,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generar resumen clínico automático

    - **paciente_id**: ID del paciente
    - **tipo_resumen**: Tipo (completo, ejecutivo, por_sistema, cronologico)
    - **periodo_dias**: Días hacia atrás (None = todo el historial)
    - **incluir_consultas**: Incluir consultas
    - **incluir_laboratorios**: Incluir laboratorios
    - **incluir_imagenes**: Incluir estudios de imagen
    - **incluir_medicamentos**: Incluir medicamentos
    """

    try:
        service = ResumenClinicoService()

        resumen = await service.generar_resumen(
            paciente_id=request.paciente_id,
            medico_id=current_user.id,
            tipo_resumen=request.tipo_resumen,
            periodo_dias=request.periodo_dias,
            incluir_consultas=request.incluir_consultas,
            incluir_laboratorios=request.incluir_laboratorios,
            incluir_imagenes=request.incluir_imagenes,
            incluir_medicamentos=request.incluir_medicamentos,
            db=db,
        )

        return resumen

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resumenes/paciente/{paciente_id}")
async def obtener_resumenes_paciente(
    paciente_id: UUID,
    limite: int = 5,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtener resúmenes previos de un paciente"""

    service = ResumenClinicoService()
    resumenes = await service.obtener_resumenes_paciente(
        paciente_id=paciente_id, db=db, limite=limite
    )

    return {"resumenes": resumenes}


# ==================== TRADUCCIÓN MÉDICA ====================


@router.post("/traducir")
async def traducir_texto_medico(
    request: TraduccionRequest,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Traducir texto médico entre idiomas

    - **texto**: Texto a traducir
    - **idioma_origen**: Código de idioma origen (es, en, fr, pt, de, it, la)
    - **idioma_destino**: Código de idioma destino
    - **tipo_contenido**: Tipo (termino_medico, diagnostico, procedimiento, medicamento, texto_libre)
    - **especialidad**: Especialidad médica (opcional)
    """

    try:
        service = TraduccionMedicaService()

        traduccion = await service.traducir(
            texto=request.texto,
            idioma_origen=request.idioma_origen,
            idioma_destino=request.idioma_destino,
            tipo_contenido=request.tipo_contenido,
            especialidad=request.especialidad,
            medico_id=current_user.id,
            db=db,
        )

        return traduccion

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/traducir-documento")
async def traducir_documento_completo(
    texto: str,
    idioma_origen: str,
    idioma_destino: str,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Traducir documento médico completo

    - **texto**: Documento completo a traducir
    - **idioma_origen**: Código de idioma origen
    - **idioma_destino**: Código de idioma destino
    """

    try:
        service = TraduccionMedicaService()

        resultado = await service.traducir_documento(
            texto=texto,
            idioma_origen=idioma_origen,
            idioma_destino=idioma_destino,
            db=db,
        )

        return resultado

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/idiomas-soportados")
async def obtener_idiomas_soportados():
    """Obtener lista de idiomas soportados para traducción"""

    service = TraduccionMedicaService()
    return {"idiomas": service.IDIOMAS_SOPORTADOS}


# ==================== DICCIONARIO MÉDICO ====================


@router.post("/diccionario/agregar")
async def agregar_termino_diccionario(
    request: TerminoDiccionarioRequest,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Agregar término al diccionario médico

    Requiere permisos de administrador o médico verificado
    """

    try:
        service = TraduccionMedicaService()

        resultado = await service.agregar_termino_diccionario(
            termino_es=request.termino_es,
            termino_en=request.termino_en,
            categoria=request.categoria,
            definicion_es=request.definicion_es,
            definicion_en=request.definicion_en,
            termino_la=request.termino_la,
            especialidad=request.especialidad,
            codigo_cie10=request.codigo_cie10,
            codigo_snomed=request.codigo_snomed,
            db=db,
        )

        return resultado

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/diccionario/buscar")
async def buscar_terminos_diccionario(
    busqueda: str,
    idioma: str = "es",
    categoria: Optional[str] = None,
    limite: int = 10,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Buscar términos en el diccionario médico

    - **busqueda**: Término a buscar
    - **idioma**: Idioma de búsqueda (es, en)
    - **categoria**: Filtrar por categoría (opcional)
    - **limite**: Número máximo de resultados
    """

    service = TraduccionMedicaService()
    terminos = await service.buscar_terminos_diccionario(
        busqueda=busqueda, idioma=idioma, categoria=categoria, db=db, limite=limite
    )

    return {"terminos": terminos}


# ==================== ENDPOINT DE PRUEBA ====================


@router.get("/health")
async def health_check():
    """Verificar que el módulo PLN está funcionando"""
    return {
        "status": "ok",
        "modulo": "Procesamiento de Lenguaje Natural",
        "funcionalidades": [
            "Transcripción de voz a texto",
            "Extracción de información",
            "Generación de resúmenes",
            "Traducción médica",
        ],
    }
