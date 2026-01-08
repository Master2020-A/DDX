"""
API endpoints para estudios especiales: EKG, EEG, Ecografías
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.models.estudios_especiales import EstudioEKG, EstudioEEG, Ecografia
from app.models.usuario import Usuario
from app.models.paciente import Paciente
from app.api.dependencies import get_current_user, get_current_active_medico
from app.services.interpretador_ekg import get_interpretador_ekg
from app.services.interpretador_ekg_ia import InterpretadorEKGIA
from app.services.interpretador_eeg import get_interpretador_eeg
from app.services.interpretador_eeg_ia import InterpretadorEEGIA
from app.services.interpretador_ecografia import get_interpretador_ecografia
from app.services.interpretador_ecografia_ia import InterpretadorEcografiaIA
from app.services.extractor_estudios_especiales import ExtractorEstudiosEspeciales
from app.services.procesador_archivos_medicos import ProcesadorArchivosMedicos
from pydantic import BaseModel, Field
import tempfile
import shutil

router = APIRouter(tags=["Estudios Especiales"])


# ==================== SCHEMAS ====================


class CrearEstudioEKG(BaseModel):
    paciente_id: UUID
    consulta_id: Optional[UUID] = None
    fecha_estudio: datetime
    motivo: Optional[str] = None
    indicacion_clinica: Optional[str] = None

    # Datos del paciente
    edad_paciente: Optional[int] = None
    peso_kg: Optional[float] = None
    altura_cm: Optional[float] = None
    presion_arterial: Optional[str] = None

    # Parámetros medidos
    frecuencia_cardiaca: Optional[int] = None
    intervalo_pr: Optional[int] = None
    duracion_qrs: Optional[int] = None
    intervalo_qt: Optional[int] = None
    intervalo_qtc: Optional[int] = None
    eje_qrs: Optional[int] = None

    # Ritmo
    ritmo: Optional[str] = None
    ritmo_regular: Optional[bool] = True

    # Ondas y segmentos
    onda_p: Optional[str] = None
    complejo_qrs: Optional[str] = None
    segmento_st: Optional[str] = None
    onda_t: Optional[str] = None
    onda_u: Optional[str] = None


class CrearEstudioEEG(BaseModel):
    paciente_id: UUID
    consulta_id: Optional[UUID] = None
    fecha_estudio: datetime
    motivo: Optional[str] = None
    indicacion_clinica: Optional[str] = None

    # Datos del paciente
    edad_paciente: Optional[int] = None
    medicamentos_actuales: Optional[str] = None
    horas_ayuno: Optional[int] = None
    horas_sueno_previo: Optional[int] = None

    # Tipo de estudio
    tipo_estudio: str = Field(..., description="basal, sueno, vigilia, prolongado")
    duracion_minutos: Optional[int] = None

    # Condiciones del estudio
    estado_conciencia: Optional[str] = None
    cooperacion_paciente: Optional[str] = None
    artefactos: Optional[List[str]] = None

    # Actividad de fondo
    actividad_fondo: Optional[str] = None
    frecuencia_dominante: Optional[float] = None
    amplitud_promedio: Optional[float] = None
    simetria: Optional[str] = None
    reactividad: Optional[str] = None

    # Ritmos cerebrales
    ritmo_alfa: Optional[str] = None
    ritmo_beta: Optional[str] = None
    ritmo_theta: Optional[str] = None
    ritmo_delta: Optional[str] = None

    # Hallazgos anormales
    ondas_agudas: bool = False
    espigas: bool = False
    complejos_punta_onda: bool = False
    actividad_paroxistica: bool = False
    enlentecimiento: Optional[str] = None

    # Localización
    localizacion_hallazgos: Optional[List[str]] = None
    lateralidad: Optional[str] = None

    # Pruebas de activación
    fotoestimulacion: Optional[str] = None
    hiperventilacion: Optional[str] = None
    privacion_sueno: Optional[str] = None


class CrearEcografia(BaseModel):
    paciente_id: UUID
    consulta_id: Optional[UUID] = None
    fecha_estudio: datetime
    motivo: Optional[str] = None
    indicacion_clinica: Optional[str] = None

    # Tipo de ecografía
    tipo_ecografia: str
    region_anatomica: str
    via_acceso: Optional[str] = None

    # Datos obstétricos
    es_obstetrica: bool = False
    edad_gestacional_semanas: Optional[int] = None
    numero_fetos: Optional[int] = None

    # Equipo
    equipo_utilizado: Optional[str] = None
    transductor: Optional[str] = None
    modo: Optional[str] = None

    # Mediciones
    mediciones: Optional[List[dict]] = None

    # Hallazgos
    hallazgos_organos: Optional[dict] = None
    masas_detectadas: Optional[List[dict]] = None
    liquido_libre: bool = False
    cantidad_liquido: Optional[str] = None

    # Doppler
    estudio_doppler: bool = False
    flujo_vascular: Optional[str] = None
    resistencia_vascular: Optional[str] = None

    # Calidad
    calidad_estudio: Optional[str] = None
    limitaciones: Optional[str] = None

    # BI-RADS (mamarias)
    birads: Optional[str] = None


# ==================== ENDPOINTS EKG ====================


@router.post("/ekg", status_code=status.HTTP_201_CREATED)
async def crear_estudio_ekg(
    data: CrearEstudioEKG,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """Crear un nuevo estudio de EKG con interpretación automática"""

    # Verificar que el paciente existe
    result = await db.execute(select(Paciente).where(Paciente.id == data.paciente_id))
    paciente = result.scalar_one_or_none()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado"
        )

    # Preparar parámetros para interpretación
    parametros = {
        "frecuencia_cardiaca": data.frecuencia_cardiaca,
        "intervalo_pr": data.intervalo_pr,
        "duracion_qrs": data.duracion_qrs,
        "intervalo_qt": data.intervalo_qt,
        "intervalo_qtc": data.intervalo_qtc,
        "eje_qrs": data.eje_qrs,
        "ritmo": data.ritmo,
        "ritmo_regular": data.ritmo_regular,
    }

    # Interpretar EKG automáticamente
    interpretador = get_interpretador_ekg()
    resultado_interpretacion = interpretador.interpretar_ekg(parametros)

    # Crear estudio
    estudio = EstudioEKG(
        paciente_id=data.paciente_id,
        consulta_id=data.consulta_id,
        medico_id=current_user.id,
        fecha_estudio=data.fecha_estudio,
        motivo=data.motivo,
        indicacion_clinica=data.indicacion_clinica,
        edad_paciente=data.edad_paciente,
        peso_kg=data.peso_kg,
        altura_cm=data.altura_cm,
        presion_arterial=data.presion_arterial,
        frecuencia_cardiaca=data.frecuencia_cardiaca,
        intervalo_pr=data.intervalo_pr,
        duracion_qrs=data.duracion_qrs,
        intervalo_qt=data.intervalo_qt,
        intervalo_qtc=data.intervalo_qtc,
        eje_qrs=data.eje_qrs,
        ritmo=data.ritmo,
        ritmo_regular=data.ritmo_regular,
        onda_p=data.onda_p,
        complejo_qrs=data.complejo_qrs,
        segmento_st=data.segmento_st,
        onda_t=data.onda_t,
        onda_u=data.onda_u,
        # Interpretación automática
        interpretacion_ia=resultado_interpretacion["interpretacion"],
        confianza_ia=resultado_interpretacion["confianza"],
        hallazgos=resultado_interpretacion["hallazgos"],
        alteraciones=resultado_interpretacion["alteraciones"],
        categorias_detectadas=resultado_interpretacion["categorias_detectadas"],
        interpretacion_medica=resultado_interpretacion["interpretacion"],
        recomendaciones=resultado_interpretacion["recomendaciones"],
        clasificacion=resultado_interpretacion["clasificacion"],
        requiere_atencion=resultado_interpretacion["requiere_atencion"],
        es_critico=resultado_interpretacion["es_critico"],
        estado="interpretado",
    )

    db.add(estudio)
    await db.commit()
    await db.refresh(estudio)

    return {
        "mensaje": "Estudio de EKG creado exitosamente",
        "id": str(estudio.id),
        "interpretacion": resultado_interpretacion,
        "requiere_atencion": estudio.requiere_atencion,
        "es_critico": estudio.es_critico,
    }


@router.get("/ekg/paciente/{paciente_id}")
async def listar_estudios_ekg_paciente(
    paciente_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar todos los estudios de EKG de un paciente"""

    result = await db.execute(
        select(EstudioEKG)
        .where(EstudioEKG.paciente_id == paciente_id)
        .order_by(EstudioEKG.fecha_estudio.desc())
    )
    estudios = result.scalars().all()

    return {"total": len(estudios), "estudios": estudios}


@router.get("/ekg/{estudio_id}")
async def obtener_estudio_ekg(
    estudio_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener detalle de un estudio de EKG"""

    result = await db.execute(select(EstudioEKG).where(EstudioEKG.id == estudio_id))
    estudio = result.scalar_one_or_none()

    if not estudio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Estudio de EKG no encontrado"
        )

    return estudio


# ==================== ENDPOINTS EEG ====================


@router.post("/eeg", status_code=status.HTTP_201_CREATED)
async def crear_estudio_eeg(
    data: CrearEstudioEEG,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """Crear un nuevo estudio de EEG con interpretación automática"""

    # Verificar que el paciente existe
    result = await db.execute(select(Paciente).where(Paciente.id == data.paciente_id))
    paciente = result.scalar_one_or_none()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado"
        )

    # Preparar parámetros para interpretación
    parametros = data.dict()

    # Interpretar EEG automáticamente
    interpretador = get_interpretador_eeg()
    resultado_interpretacion = interpretador.interpretar_eeg(parametros)

    # Crear estudio
    estudio = EstudioEEG(
        **data.dict(),
        medico_id=current_user.id,
        # Interpretación automática
        interpretacion_ia=resultado_interpretacion["interpretacion"],
        confianza_ia=resultado_interpretacion["confianza"],
        hallazgos=resultado_interpretacion["hallazgos"],
        alteraciones=resultado_interpretacion["alteraciones"],
        categorias_detectadas=resultado_interpretacion["categorias_detectadas"],
        interpretacion_medica=resultado_interpretacion["interpretacion"],
        recomendaciones=resultado_interpretacion["recomendaciones"],
        clasificacion=resultado_interpretacion["clasificacion"],
        requiere_atencion=resultado_interpretacion["requiere_atencion"],
        es_critico=resultado_interpretacion["es_critico"],
        estado="interpretado",
    )

    db.add(estudio)
    await db.commit()
    await db.refresh(estudio)

    return {
        "mensaje": "Estudio de EEG creado exitosamente",
        "id": str(estudio.id),
        "interpretacion": resultado_interpretacion,
        "requiere_atencion": estudio.requiere_atencion,
        "es_critico": estudio.es_critico,
    }


@router.get("/eeg/paciente/{paciente_id}")
async def listar_estudios_eeg_paciente(
    paciente_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar todos los estudios de EEG de un paciente"""

    result = await db.execute(
        select(EstudioEEG)
        .where(EstudioEEG.paciente_id == paciente_id)
        .order_by(EstudioEEG.fecha_estudio.desc())
    )
    estudios = result.scalars().all()

    return {"total": len(estudios), "estudios": estudios}


@router.get("/eeg/{estudio_id}")
async def obtener_estudio_eeg(
    estudio_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener detalle de un estudio de EEG"""

    result = await db.execute(select(EstudioEEG).where(EstudioEEG.id == estudio_id))
    estudio = result.scalar_one_or_none()

    if not estudio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Estudio de EEG no encontrado"
        )

    return estudio


# ==================== ENDPOINTS ECOGRAFÍA ====================


@router.post("/ecografia", status_code=status.HTTP_201_CREATED)
async def crear_ecografia(
    data: CrearEcografia,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """Crear una nueva ecografía con interpretación automática"""

    # Verificar que el paciente existe
    result = await db.execute(select(Paciente).where(Paciente.id == data.paciente_id))
    paciente = result.scalar_one_or_none()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado"
        )

    # Preparar parámetros para interpretación
    parametros = data.dict()

    # Interpretar ecografía automáticamente
    interpretador = get_interpretador_ecografia()
    resultado_interpretacion = interpretador.interpretar_ecografia(parametros)

    # Crear estudio
    ecografia = Ecografia(
        **data.dict(),
        medico_id=current_user.id,
        # Interpretación automática
        interpretacion_ia=resultado_interpretacion["interpretacion"],
        confianza_ia=resultado_interpretacion["confianza"],
        hallazgos=resultado_interpretacion["hallazgos"],
        categorias_detectadas=resultado_interpretacion["categorias_detectadas"],
        estructuras_identificadas=resultado_interpretacion.get(
            "estructuras_identificadas"
        ),
        interpretacion_medica=resultado_interpretacion["interpretacion"],
        recomendaciones=resultado_interpretacion["recomendaciones"],
        clasificacion=resultado_interpretacion["clasificacion"],
        requiere_atencion=resultado_interpretacion["requiere_atencion"],
        requiere_seguimiento=resultado_interpretacion["requiere_seguimiento"],
        estado="interpretado",
    )

    db.add(ecografia)
    await db.commit()
    await db.refresh(ecografia)

    return {
        "mensaje": "Ecografía creada exitosamente",
        "id": str(ecografia.id),
        "interpretacion": resultado_interpretacion,
        "requiere_atencion": ecografia.requiere_atencion,
        "requiere_seguimiento": ecografia.requiere_seguimiento,
    }


@router.get("/ecografia/paciente/{paciente_id}")
async def listar_ecografias_paciente(
    paciente_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar todas las ecografías de un paciente"""

    result = await db.execute(
        select(Ecografia)
        .where(Ecografia.paciente_id == paciente_id)
        .order_by(Ecografia.fecha_estudio.desc())
    )
    ecografias = result.scalars().all()

    return {"total": len(ecografias), "ecografias": ecografias}


@router.get("/ecografia/{ecografia_id}")
async def obtener_ecografia(
    ecografia_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener detalle de una ecografía"""

    result = await db.execute(select(Ecografia).where(Ecografia.id == ecografia_id))
    ecografia = result.scalar_one_or_none()

    if not ecografia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ecografía no encontrada"
        )

    return ecografia


# ==================== ENDPOINTS GENERALES ====================


@router.get("/paciente/{paciente_id}/resumen")
async def obtener_resumen_estudios(
    paciente_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener resumen de todos los estudios especiales de un paciente"""

    # EKG
    result_ekg = await db.execute(
        select(EstudioEKG)
        .where(EstudioEKG.paciente_id == paciente_id)
        .order_by(EstudioEKG.fecha_estudio.desc())
    )
    estudios_ekg = result_ekg.scalars().all()

    # EEG
    result_eeg = await db.execute(
        select(EstudioEEG)
        .where(EstudioEEG.paciente_id == paciente_id)
        .order_by(EstudioEEG.fecha_estudio.desc())
    )
    estudios_eeg = result_eeg.scalars().all()

    # Ecografías
    result_eco = await db.execute(
        select(Ecografia)
        .where(Ecografia.paciente_id == paciente_id)
        .order_by(Ecografia.fecha_estudio.desc())
    )
    ecografias = result_eco.scalars().all()

    return {
        "paciente_id": str(paciente_id),
        "ekg": {
            "total": len(estudios_ekg),
            "criticos": sum(1 for e in estudios_ekg if e.es_critico),
            "requieren_atencion": sum(1 for e in estudios_ekg if e.requiere_atencion),
            "estudios": estudios_ekg[:5],  # Últimos 5
        },
        "eeg": {
            "total": len(estudios_eeg),
            "criticos": sum(1 for e in estudios_eeg if e.es_critico),
            "requieren_atencion": sum(1 for e in estudios_eeg if e.requiere_atencion),
            "estudios": estudios_eeg[:5],
        },
        "ecografias": {
            "total": len(ecografias),
            "requieren_atencion": sum(1 for e in ecografias if e.requiere_atencion),
            "requieren_seguimiento": sum(
                1 for e in ecografias if e.requiere_seguimiento
            ),
            "estudios": ecografias[:5],
        },
    }


# ==================== EXTRACCIÓN DESDE ARCHIVOS ====================


@router.post("/extraer-desde-archivo")
async def extraer_datos_desde_archivo(
    archivo: UploadFile = File(...),
    metodo_analisis: str = Form("auto"),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Extrae datos de un archivo de estudio especial
    Soporta: PDF, imágenes, .ecg, .mat

    Args:
        archivo: Archivo a procesar
        metodo_analisis: Método de análisis a usar
            - "auto": OCR primero, IA si falla (por defecto)
            - "ocr": Solo OCR
            - "ia": Forzar uso de IA (requiere API key)

    Retorna los datos extraídos + análisis de anomalías
    """
    # Validar formato
    extension = archivo.filename.split(".")[-1].lower()
    formatos_permitidos = [
        "pdf",
        "jpg",
        "jpeg",
        "png",
        "tiff",
        "bmp",
        "ecg",
        "mat",
        "dat",
        "csv",
    ]

    if extension not in formatos_permitidos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato no soportado. Use: {', '.join(formatos_permitidos)}",
        )

    # Guardar archivo temporalmente
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{extension}")
    try:
        # Copiar contenido
        shutil.copyfileobj(archivo.file, temp_file)
        temp_file.close()

        # Extraer datos usando el procesador mejorado
        try:
            # Usar procesador mejorado para .ecg, .mat, .csv
            if extension in ["ecg", "mat", "dat", "csv"]:
                procesador = ProcesadorArchivosMedicos()
                resultado = procesador.procesar_archivo(temp_file.name)
            else:
                # Para PDF e imágenes, usar procesador según método elegido
                procesador = ProcesadorArchivosMedicos()

                # Si el usuario fuerza IA, usar directamente
                if metodo_analisis == "ia":
                    import os

                    if not os.getenv("OPENAI_API_KEY"):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="API key de OpenAI no configurada. Configure OPENAI_API_KEY en .env",
                        )
                    # Forzar análisis con IA
                    resultado_ia = procesador._analizar_con_ia(temp_file.name)
                    if resultado_ia and "datos" in resultado_ia:
                        # Formatear resultado de IA en el formato esperado
                        resultado = {
                            "tipo_estudio": resultado_ia.get("tipo_estudio", "ekg"),
                            "datos": resultado_ia["datos"],
                            "metodo": "ia_vision",
                            "confianza": resultado_ia.get("confianza", 0.85),
                            "interpretacion_ia": resultado_ia.get("interpretacion", ""),
                            "texto_muestra": resultado_ia.get("interpretacion", "")[
                                :200
                            ],
                        }
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error al analizar con IA. Verifica que la imagen sea válida.",
                        )
                elif metodo_analisis == "ocr":
                    # Solo OCR, sin IA
                    resultado = procesador.procesar_archivo(temp_file.name)
                    # Deshabilitar IA temporalmente
                    resultado["metodo"] = "ocr_only"
                else:
                    # Auto: OCR primero, IA si falla
                    resultado = procesador.procesar_archivo(temp_file.name)

                # Usar extractor original como fallback
                if not resultado or not resultado.get("datos"):
                    extractor = ExtractorEstudiosEspeciales()
                    resultado = extractor.extraer_desde_archivo(temp_file.name)
                # Agregar análisis de anomalías
                if "datos" in resultado and resultado["tipo_estudio"] != "desconocido":
                    procesador = ProcesadorArchivosMedicos()
                    anomalias = procesador._detectar_anomalias_texto(
                        resultado.get("texto_extraido", ""), resultado["tipo_estudio"]
                    )
                    # Analizar valores numéricos
                    if resultado["tipo_estudio"] == "ekg":
                        datos = resultado["datos"]
                        if "frecuencia_cardiaca" in datos:
                            try:
                                fc = int(datos["frecuencia_cardiaca"])
                                anomalias.extend(procesador._analizar_fc(fc))
                            except:
                                pass
                        if "intervalo_pr" in datos:
                            try:
                                pr = int(datos["intervalo_pr"])
                                anomalias.extend(procesador._analizar_pr(pr))
                            except:
                                pass
                        if "duracion_qrs" in datos:
                            try:
                                qrs = int(datos["duracion_qrs"])
                                anomalias.extend(procesador._analizar_qrs(qrs))
                            except:
                                pass
                        if "intervalo_qtc" in datos:
                            try:
                                qtc = int(datos["intervalo_qtc"])
                                anomalias.extend(procesador._analizar_qtc(qtc))
                            except:
                                pass
                        if "eje_qrs" in datos:
                            try:
                                eje = int(datos["eje_qrs"])
                                anomalias.extend(procesador._analizar_eje(eje))
                            except:
                                pass
                    resultado["anomalias"] = list(set(anomalias))

            # Agregar información sobre conversión CSV a imagen si está disponible
            respuesta = {
                "mensaje": "Datos extraídos exitosamente",
                "tipo_estudio": resultado.get("tipo_estudio", "desconocido"),
                "datos": resultado.get("datos", {}),
                "anomalias": resultado.get("anomalias", []),
                "confianza": resultado.get("confianza", 0.5),
                "texto_muestra": resultado.get(
                    "texto_muestra", resultado.get("texto_extraido", "")
                ),
            }

            # Si es CSV con señales, agregar opción de conversión
            if extension == "csv" and resultado.get("datos", {}).get(
                "conversion_imagen_disponible"
            ):
                respuesta["conversion_csv_disponible"] = True
                respuesta["mensaje_conversion"] = (
                    "Este CSV contiene señales temporales. "
                    "Puedes usar el endpoint /convertir-csv-a-imagen para análisis con IA."
                )

            return respuesta

        except ImportError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Las librerías de OCR no están instaladas en el servidor",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al extraer datos: {str(e)}",
            )

    finally:
        # Limpiar archivo temporal
        try:
            import os

            os.unlink(temp_file.name)
        except:
            pass


@router.post("/convertir-csv-a-imagen")
async def convertir_csv_a_imagen_y_analizar(
    archivo: UploadFile = File(...),
    num_derivaciones: int = Form(12),
    usar_ia: bool = Form(True),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Convierte un archivo CSV de señales ECG a imagen y opcionalmente lo analiza con IA

    Args:
        archivo: Archivo CSV con señales temporales
        num_derivaciones: Número de derivaciones a graficar (default: 12)
        usar_ia: Si True, analiza la imagen con IA (requiere API key)

    Returns:
        Datos extraídos del análisis con IA + información de la conversión
    """
    # Validar extensión
    extension = archivo.filename.split(".")[-1].lower()
    if extension != "csv":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se aceptan archivos CSV",
        )

    # Guardar archivo temporalmente
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    try:
        shutil.copyfileobj(archivo.file, temp_file)
        temp_file.close()

        # Convertir y analizar
        try:
            procesador = ProcesadorArchivosMedicos()
            resultado = procesador.convertir_csv_a_imagen_y_analizar(
                csv_path=temp_file.name,
                num_derivaciones=num_derivaciones,
                usar_ia=usar_ia,
            )

            if "error" in resultado:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=resultado["error"]
                )

            return {
                "mensaje": "CSV convertido a imagen exitosamente",
                "tipo_estudio": resultado.get("tipo_estudio", "ekg"),
                "datos": resultado.get("datos", {}),
                "anomalias": resultado.get("anomalias", []),
                "interpretacion_ia": resultado.get("interpretacion_ia", ""),
                "confianza": resultado.get("confianza", 0.7),
                "metodo": resultado.get("metodo", "csv_convertido_a_imagen"),
            }

        except ImportError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Matplotlib no está instalado. Ejecutar: pip install matplotlib",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al convertir CSV: {str(e)}",
            )
    finally:
        # Limpiar archivo temporal
        try:
            import os

            os.unlink(temp_file.name)
        except:
            pass


# ==================== INTERPRETACIÓN AVANZADA CON IA ====================


@router.post("/ekg/{ekg_id}/interpretar-ia")
async def interpretar_ekg_con_ia(
    ekg_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """
    Interpreta un EKG existente usando IA (Groq) para análisis avanzado.
    """
    try:
        # Obtener el estudio EKG
        result = await db.execute(select(EstudioEKG).where(EstudioEKG.id == ekg_id))
        ekg = result.scalar_one_or_none()

        if not ekg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudio EKG no encontrado",
            )

        # Preparar parámetros para la IA
        parametros = {
            "edad_paciente": ekg.edad_paciente,
            "presion_arterial": ekg.presion_arterial,
            "frecuencia_cardiaca": ekg.frecuencia_cardiaca,
            "ritmo": ekg.ritmo,
            "ritmo_regular": ekg.ritmo_regular,
            "intervalo_pr": ekg.intervalo_pr,
            "duracion_qrs": ekg.duracion_qrs,
            "intervalo_qt": ekg.intervalo_qt,
            "intervalo_qtc": ekg.intervalo_qtc,
            "eje_qrs": ekg.eje_qrs,
            "onda_p": ekg.onda_p,
            "complejo_qrs": ekg.complejo_qrs,
            "segmento_st": ekg.segmento_st,
            "onda_t": ekg.onda_t,
            "hallazgos": ekg.hallazgos,
            "motivo": ekg.motivo,
        }

        # Interpretar con IA
        interpretador = InterpretadorEKGIA()
        resultado = interpretador.interpretar_ekg_avanzado(parametros)

        # Actualizar el estudio con la interpretación de IA
        ekg.interpretacion_ia = resultado.get("interpretacion")
        ekg.diagnostico = resultado.get("diagnostico_principal")
        ekg.clasificacion = resultado.get("clasificacion")
        ekg.es_critico = resultado.get("es_critico", False)
        ekg.requiere_atencion = resultado.get("requiere_atencion_inmediata", False)

        # Guardar recomendaciones como lista
        if resultado.get("recomendaciones"):
            ekg.recomendaciones = resultado["recomendaciones"]

        await db.commit()
        await db.refresh(ekg)

        return {
            "ekg_id": str(ekg.id),
            "interpretacion_ia": resultado,
            "actualizado": True,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al interpretar EKG con IA: {str(e)}",
        )


@router.post("/eeg/{eeg_id}/interpretar-ia")
async def interpretar_eeg_con_ia(
    eeg_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """
    Interpreta un EEG existente usando IA (Groq) para análisis avanzado.
    """
    try:
        # Obtener el estudio EEG
        result = await db.execute(select(EstudioEEG).where(EstudioEEG.id == eeg_id))
        eeg = result.scalar_one_or_none()

        if not eeg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudio EEG no encontrado",
            )

        # Preparar parámetros para la IA
        parametros = {
            "edad_paciente": eeg.edad_paciente,
            "medicamentos_actuales": eeg.medicamentos_actuales,
            "tipo_estudio": eeg.tipo_estudio,
            "duracion_minutos": eeg.duracion_minutos,
            "estado_conciencia": eeg.estado_conciencia,
            "cooperacion_paciente": eeg.cooperacion_paciente,
            "actividad_fondo": eeg.actividad_fondo,
            "frecuencia_dominante": eeg.frecuencia_dominante,
            "amplitud_promedio": eeg.amplitud_promedio,
            "simetria": eeg.simetria,
            "reactividad": eeg.reactividad,
            "ritmo_alfa": eeg.ritmo_alfa,
            "ritmo_beta": eeg.ritmo_beta,
            "ritmo_theta": eeg.ritmo_theta,
            "ritmo_delta": eeg.ritmo_delta,
            "ondas_agudas": eeg.ondas_agudas,
            "espigas": eeg.espigas,
            "complejos_punta_onda": eeg.complejos_punta_onda,
            "actividad_paroxistica": eeg.actividad_paroxistica,
            "localizacion_hallazgos": eeg.localizacion_hallazgos,
            "lateralidad": eeg.lateralidad,
            "fotoestimulacion": eeg.fotoestimulacion,
            "hiperventilacion": eeg.hiperventilacion,
            "motivo": eeg.motivo,
        }

        # Interpretar con IA
        interpretador = InterpretadorEEGIA()
        resultado = interpretador.interpretar_eeg_avanzado(parametros)

        # Actualizar el estudio con la interpretación de IA
        eeg.interpretacion_ia = resultado.get("interpretacion")
        eeg.diagnostico = resultado.get("diagnostico_principal")
        eeg.clasificacion = resultado.get("clasificacion")
        eeg.requiere_atencion = resultado.get("requiere_atencion_inmediata", False)

        # Guardar recomendaciones como lista
        if resultado.get("recomendaciones"):
            eeg.recomendaciones = resultado["recomendaciones"]

        await db.commit()
        await db.refresh(eeg)

        return {
            "eeg_id": str(eeg.id),
            "interpretacion_ia": resultado,
            "actualizado": True,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al interpretar EEG con IA: {str(e)}",
        )


@router.post("/ecografia/{ecografia_id}/interpretar-ia")
async def interpretar_ecografia_con_ia(
    ecografia_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """
    Interpreta una Ecografía existente usando IA (Groq) para análisis avanzado.
    """
    try:
        # Obtener la ecografía
        result = await db.execute(select(Ecografia).where(Ecografia.id == ecografia_id))
        ecografia = result.scalar_one_or_none()

        if not ecografia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Ecografía no encontrada"
            )

        # Preparar parámetros para la IA
        parametros = {
            "tipo_ecografia": ecografia.tipo_ecografia,
            "region_anatomica": ecografia.region_anatomica,
            "modo": ecografia.modo,
            "via_acceso": ecografia.via_acceso,
            "transductor": ecografia.transductor,
            "es_obstetrica": ecografia.es_obstetrica,
            "edad_gestacional_semanas": ecografia.edad_gestacional_semanas,
            "numero_fetos": ecografia.numero_fetos,
            "estudio_doppler": ecografia.estudio_doppler,
            "flujo_vascular": ecografia.flujo_vascular,
            "resistencia_vascular": ecografia.resistencia_vascular,
            "liquido_libre": ecografia.liquido_libre,
            "cantidad_liquido": ecografia.cantidad_liquido,
            "calidad_estudio": ecografia.calidad_estudio,
            "limitaciones": ecografia.limitaciones,
            "birads": ecografia.birads,
            "motivo": ecografia.motivo,
        }

        # Interpretar con IA
        interpretador = InterpretadorEcografiaIA()
        resultado = interpretador.interpretar_ecografia_avanzado(parametros)

        # Actualizar el estudio con la interpretación de IA
        ecografia.interpretacion_ia = resultado.get("interpretacion")
        ecografia.diagnostico = resultado.get("diagnostico_principal")
        ecografia.clasificacion = resultado.get("clasificacion")
        ecografia.requiere_atencion = resultado.get(
            "requiere_atencion_inmediata", False
        )

        # Guardar recomendaciones como lista
        if resultado.get("recomendaciones"):
            ecografia.recomendaciones = resultado["recomendaciones"]

        await db.commit()
        await db.refresh(ecografia)

        return {
            "ecografia_id": str(ecografia.id),
            "interpretacion_ia": resultado,
            "actualizado": True,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al interpretar Ecografía con IA: {str(e)}",
        )


# ==================== ENDPOINTS ANÁLISIS AVANZADO EKG ====================


@router.post("/ekg/analizar-imagen")
async def analizar_ekg_desde_imagen(
    archivo: UploadFile = File(...),
    paciente_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """
    Analiza una imagen de EKG y extrae parámetros automáticamente.
    Usa digitalización avanzada + detección de ondas + diagnóstico narrativo.
    """
    try:
        from app.services.ekg_analizador_completo import EKGAnalizadorCompleto

        # Leer archivo
        contenido = await archivo.read()

        # Preparar info del paciente si está disponible
        paciente_info = None
        if paciente_id:
            result = await db.execute(
                select(Paciente).where(Paciente.id == UUID(paciente_id))
            )
            paciente = result.scalar_one_or_none()
            if paciente:
                paciente_info = {
                    "name": f"{paciente.nombre} {paciente.apellido_paterno}",
                    "age": paciente.edad if hasattr(paciente, "edad") else 0,
                    "date_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "indication": "Análisis automático desde imagen",
                }

        # Analizar con el sistema completo
        analizador = EKGAnalizadorCompleto()
        resultado = analizador.analizar_desde_imagen(contenido, paciente_info)

        if not resultado["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=resultado.get("error", "No se pudo analizar la imagen"),
            )

        return {
            "success": True,
            "mediciones": resultado["mediciones"],
            "ondas_detectadas": resultado["ondas"],
            "diagnostico": resultado["diagnostico"],
            "interpretacion_detallada": resultado["interpretacion_detallada"],
            "calidad_senal": resultado["calidad_senal"],
            "reporte_texto": resultado.get("reporte_texto"),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al analizar imagen de EKG: {str(e)}",
        )


@router.post("/ekg/extraer-parametros")
async def extraer_parametros_ekg(
    archivo: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """
    Extrae parámetros automáticamente de una imagen de EKG para pre-llenar formulario.
    Retorna solo los parámetros necesarios para el formulario.
    """
    try:
        from app.services.ekg_analizador_completo import EKGAnalizadorCompleto

        # Leer archivo
        contenido = await archivo.read()

        # Extraer parámetros
        analizador = EKGAnalizadorCompleto()
        resultado = analizador.extraer_parametros_automaticos(contenido)

        if not resultado["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=resultado.get("error", "No se pudieron extraer parámetros"),
            )

        return {"success": True, "parametros": resultado["parametros"]}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al extraer parámetros: {str(e)}",
        )


@router.post("/ekg/{ekg_id}/generar-grafica-anotada")
async def generar_grafica_anotada_ekg(
    ekg_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Genera una gráfica anotada con marcadores de ondas P, Q, R, S, T
    para un estudio EKG existente (si tiene imagen asociada).
    """
    try:
        from app.services.ekg_analizador_completo import EKGAnalizadorCompleto
        from app.services.ekg_graficador import EKGGraficador

        # Obtener el EKG
        result = await db.execute(select(EstudioEKG).where(EstudioEKG.id == ekg_id))
        ekg = result.scalar_one_or_none()

        if not ekg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudio EKG no encontrado",
            )

        # Verificar si tiene imagen asociada
        if not ekg.archivo_imagen:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El estudio no tiene imagen asociada",
            )

        # Leer imagen (asumiendo que está guardada en el sistema)
        # Por ahora retornamos un placeholder
        # En producción, leerías el archivo del storage

        return {
            "ekg_id": str(ekg.id),
            "mensaje": "Funcionalidad de gráfica anotada disponible",
            "nota": "Requiere integración con sistema de archivos",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar gráfica: {str(e)}",
        )


@router.get("/ekg/{ekg_id}/interpretacion-narrativa")
async def obtener_interpretacion_narrativa(
    ekg_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene la interpretación narrativa detallada de un EKG existente.
    Genera textos médicos por componente (P, PR, QRS, ST-T, QT).
    """
    try:
        from app.services.ekg_diagnostico_avanzado import EKGDiagnosticoAvanzado

        # Obtener el EKG
        result = await db.execute(select(EstudioEKG).where(EstudioEKG.id == ekg_id))
        ekg = result.scalar_one_or_none()

        if not ekg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudio EKG no encontrado",
            )

        # Preparar mediciones
        intervals = {
            "heart_rate": ekg.frecuencia_cardiaca or 0,
            "PR_interval": ekg.intervalo_pr or 0,
            "QRS_duration": ekg.duracion_qrs or 0,
            "QT_interval": ekg.intervalo_qt or 0,
            "QTc": ekg.intervalo_qtc or 0,
            "QRS_Axis": ekg.eje_qrs or 0,
            "P_amplitude": 0.15,  # Valores por defecto
            "T_amplitude": 0.3,
            "ST_level": 0.0,
        }

        waves = {
            "P_peaks": [100, 600, 1100] if ekg.onda_p != "Ausente" else [],
            "R_peaks": [200, 700, 1200],
            "T_peaks": [300, 800, 1300],
            "Q_peaks": [],
            "S_peaks": [],
        }

        # Generar interpretación
        diagnostico_engine = EKGDiagnosticoAvanzado()
        resultado = diagnostico_engine.analizar(intervals, waves, {})

        return {
            "ekg_id": str(ekg.id),
            "interpretacion_narrativa": resultado["detailed_interpretation"],
            "diagnostico": resultado["rhythm"],
            "hallazgos": resultado["diagnoses"],
            "riesgo": resultado["prognosis_text"],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar interpretación narrativa: {str(e)}",
        )


# ==================== ENDPOINTS EXTRACCIÓN AUTOMÁTICA ====================


@router.post("/eeg/extraer-parametros")
async def extraer_parametros_eeg(
    archivo: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """
    Extrae parámetros automáticamente de una imagen de EEG para pre-llenar formulario.
    """
    try:
        from app.services.eeg_analizador_completo import EEGAnalizadorCompleto

        # Leer archivo
        contenido = await archivo.read()

        # Extraer parámetros
        analizador = EEGAnalizadorCompleto()
        resultado = analizador.extraer_parametros_automaticos(contenido)

        if not resultado["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=resultado.get("error", "No se pudieron extraer parámetros"),
            )

        return {"success": True, "parametros": resultado["parametros"]}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al extraer parámetros: {str(e)}",
        )


@router.post("/ecografia/extraer-parametros")
async def extraer_parametros_ecografia(
    archivo: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """
    Extrae parámetros automáticamente de una imagen de Ecografía para pre-llenar formulario.
    """
    try:
        from app.services.eeg_analizador_completo import EcografiaAnalizadorCompleto

        # Leer archivo
        contenido = await archivo.read()

        # Extraer parámetros
        analizador = EcografiaAnalizadorCompleto()
        resultado = analizador.extraer_parametros_automaticos(contenido)

        if not resultado["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=resultado.get("error", "No se pudieron extraer parámetros"),
            )

        return {"success": True, "parametros": resultado["parametros"]}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al extraer parámetros: {str(e)}",
        )


# ==================== GENERACIÓN DE PDFs ====================


@router.get("/ekg/{ekg_id}/pdf-analisis")
async def generar_pdf_analisis_ekg(
    ekg_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Generar PDF con el análisis de parámetros del EKG"""
    from app.services.generador_pdf_estudios_especiales import get_generador_pdf
    from fastapi.responses import StreamingResponse

    try:
        print(f"🟢 GENERANDO PDF DE ANÁLISIS para EKG: {ekg_id}")

        result = await db.execute(select(EstudioEKG).where(EstudioEKG.id == ekg_id))
        estudio = result.scalar_one_or_none()
        if not estudio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudio de EKG no encontrado",
            )

        result_paciente = await db.execute(
            select(Paciente).where(Paciente.id == estudio.paciente_id)
        )
        paciente = result_paciente.scalar_one_or_none()

        datos = {
            "paciente": {
                "nombre_completo": paciente.nombre_completo if paciente else "N/A",
                "edad": paciente.edad if paciente else "N/A",
                "sexo": paciente.genero if paciente else "N/A",
                "fecha_estudio": (
                    estudio.fecha_estudio.strftime("%d/%m/%Y %H:%M")
                    if estudio.fecha_estudio
                    else "N/A"
                ),
                "medico": f"Dr(a). {current_user.nombre_completo if hasattr(current_user, 'nombre_completo') else 'N/A'}",
            },
            "frecuencia_cardiaca": estudio.frecuencia_cardiaca,
            "intervalo_pr": estudio.intervalo_pr,
            "duracion_qrs": estudio.duracion_qrs,
            "intervalo_qt": estudio.intervalo_qt,
            "intervalo_qtc": estudio.intervalo_qtc,
            "eje_qrs": estudio.eje_qrs,
            "ritmo": estudio.ritmo,
            "onda_p": estudio.onda_p,
            "complejo_qrs": estudio.complejo_qrs,
            "segmento_st": estudio.segmento_st,
            "onda_t": estudio.onda_t,
        }

        generador = get_generador_pdf()
        pdf_buffer = generador.generar_reporte_analisis_ekg(datos)

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=EKG_Analisis_{ekg_id}.pdf"
            },
        )
    except HTTPException:
        raise
    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ReportLab no está instalado. Por favor instale: pip install reportlab",
        )
    except Exception as e:
        print(f"Error al generar PDF de análisis EKG: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el PDF: {str(e)}",
        )


@router.get("/ekg/{ekg_id}/pdf-interpretacion")
async def generar_pdf_interpretacion_ekg(
    ekg_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Generar PDF con la interpretación de IA del EKG"""
    from app.services.generador_pdf_estudios_especiales import get_generador_pdf
    from fastapi.responses import StreamingResponse

    try:
        print(f"🔵 GENERANDO PDF DE INTERPRETACIÓN para EKG: {ekg_id}")

        result = await db.execute(select(EstudioEKG).where(EstudioEKG.id == ekg_id))
        estudio = result.scalar_one_or_none()
        if not estudio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudio de EKG no encontrado",
            )

        result_paciente = await db.execute(
            select(Paciente).where(Paciente.id == estudio.paciente_id)
        )
        paciente = result_paciente.scalar_one_or_none()

        # Convertir hallazgos y recomendaciones a lista (manejar tanto string como array)
        hallazgos_lista = []
        if estudio.hallazgos:
            if isinstance(estudio.hallazgos, str):
                # Si es string, dividir por saltos de línea
                hallazgos_lista = [
                    h.strip() for h in estudio.hallazgos.split("\n") if h.strip()
                ]
            elif isinstance(estudio.hallazgos, list):
                # Si ya es lista, usarla directamente
                hallazgos_lista = estudio.hallazgos

        recomendaciones_lista = []
        if estudio.recomendaciones:
            if isinstance(estudio.recomendaciones, str):
                # Si es string, dividir por saltos de línea
                recomendaciones_lista = [
                    r.strip() for r in estudio.recomendaciones.split("\n") if r.strip()
                ]
            elif isinstance(estudio.recomendaciones, list):
                # Si ya es lista, usarla directamente
                recomendaciones_lista = estudio.recomendaciones

        datos = {
            "paciente": {
                "nombre_completo": paciente.nombre_completo if paciente else "N/A",
                "edad": paciente.edad if paciente else "N/A",
                "sexo": paciente.genero if paciente else "N/A",
                "fecha_estudio": (
                    estudio.fecha_estudio.strftime("%d/%m/%Y %H:%M")
                    if estudio.fecha_estudio
                    else "N/A"
                ),
                "medico": f"Dr(a). {current_user.nombre_completo if hasattr(current_user, 'nombre_completo') else 'N/A'}",
            },
            "clasificacion": estudio.clasificacion,
            "interpretacion": estudio.interpretacion_ia
            or estudio.interpretacion_medica,
            "hallazgos": hallazgos_lista,
            "recomendaciones": recomendaciones_lista,
            "confianza_ia": estudio.confianza_ia or 0,
            "requiere_atencion": estudio.requiere_atencion,
            "es_critico": estudio.es_critico,
        }

        print(
            f"📊 Datos para PDF Interpretación: clasificacion={datos['clasificacion']}, interpretacion={'SÍ' if datos['interpretacion'] else 'NO'}"
        )
        print(f"🔍 TIPO de interpretacion: {type(datos['interpretacion'])}")
        print(
            f"🔍 CONTENIDO de interpretacion (primeros 200 chars): {str(datos['interpretacion'])[:200]}"
        )

        generador = get_generador_pdf()
        pdf_buffer = generador.generar_reporte_interpretacion_ekg(datos)

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=EKG_Interpretacion_{ekg_id}.pdf"
            },
        )
    except HTTPException:
        raise
    except ImportError as e:
        print(f"❌ Error de importación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ReportLab no está instalado. Por favor instale: pip install reportlab",
        )
    except Exception as e:
        print(f"❌ Error al generar PDF de interpretación EKG: {str(e)}")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el PDF de interpretación: {str(e)}",
        )


@router.get("/eeg/{eeg_id}/pdf-analisis")
async def generar_pdf_analisis_eeg(
    eeg_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Generar PDF con el análisis de parámetros del EEG"""
    from app.services.generador_pdf_estudios_especiales import get_generador_pdf
    from fastapi.responses import StreamingResponse

    result = await db.execute(select(EstudioEEG).where(EstudioEEG.id == eeg_id))
    estudio = result.scalar_one_or_none()
    if not estudio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Estudio de EEG no encontrado"
        )

    result_paciente = await db.execute(
        select(Paciente).where(Paciente.id == estudio.paciente_id)
    )
    paciente = result_paciente.scalar_one_or_none()

    datos = {
        "paciente": {
            "nombre_completo": paciente.nombre_completo if paciente else "N/A",
            "edad": paciente.edad if paciente else "N/A",
            "sexo": paciente.genero if paciente else "N/A",
            "fecha_estudio": (
                estudio.fecha_estudio.strftime("%d/%m/%Y %H:%M")
                if estudio.fecha_estudio
                else "N/A"
            ),
            "medico": f"Dr(a). {current_user.nombre_completo if hasattr(current_user, 'nombre_completo') else 'N/A'}",
        },
        "tipo_estudio": estudio.tipo_estudio,
        "duracion_minutos": estudio.duracion_minutos,
        "estado_conciencia": estudio.estado_conciencia,
        "cooperacion_paciente": estudio.cooperacion_paciente,
        "actividad_fondo": estudio.actividad_fondo,
        "frecuencia_dominante": estudio.frecuencia_dominante,
        "amplitud_promedio": estudio.amplitud_promedio,
        "simetria": estudio.simetria,
        "ritmo_delta": estudio.ritmo_delta,
        "ritmo_theta": estudio.ritmo_theta,
        "ritmo_alfa": estudio.ritmo_alfa,
        "ritmo_beta": estudio.ritmo_beta,
    }

    generador = get_generador_pdf()
    pdf_buffer = generador.generar_reporte_analisis_eeg(datos)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=EEG_Analisis_{eeg_id}.pdf"
        },
    )


@router.get("/eeg/{eeg_id}/pdf-interpretacion")
async def generar_pdf_interpretacion_eeg(
    eeg_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Generar PDF con la interpretación de IA del EEG"""
    from app.services.generador_pdf_estudios_especiales import get_generador_pdf
    from fastapi.responses import StreamingResponse

    result = await db.execute(select(EstudioEEG).where(EstudioEEG.id == eeg_id))
    estudio = result.scalar_one_or_none()
    if not estudio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Estudio de EEG no encontrado"
        )

    result_paciente = await db.execute(
        select(Paciente).where(Paciente.id == estudio.paciente_id)
    )
    paciente = result_paciente.scalar_one_or_none()

    # Convertir hallazgos y recomendaciones de string a lista si es necesario
    hallazgos_lista = []
    if estudio.hallazgos:
        if isinstance(estudio.hallazgos, str):
            hallazgos_lista = estudio.hallazgos.split("\n") if estudio.hallazgos else []
        else:
            hallazgos_lista = estudio.hallazgos

    recomendaciones_lista = []
    if estudio.recomendaciones:
        if isinstance(estudio.recomendaciones, str):
            recomendaciones_lista = (
                estudio.recomendaciones.split("\n") if estudio.recomendaciones else []
            )
        else:
            recomendaciones_lista = estudio.recomendaciones

    datos = {
        "paciente": {
            "nombre_completo": paciente.nombre_completo if paciente else "N/A",
            "edad": paciente.edad if paciente else "N/A",
            "sexo": paciente.genero if paciente else "N/A",
            "fecha_estudio": (
                estudio.fecha_estudio.strftime("%d/%m/%Y %H:%M")
                if estudio.fecha_estudio
                else "N/A"
            ),
            "medico": f"Dr(a). {current_user.nombre_completo if hasattr(current_user, 'nombre_completo') else 'N/A'}",
        },
        "clasificacion": estudio.clasificacion,
        "interpretacion": estudio.interpretacion_ia or estudio.interpretacion_medica,
        "hallazgos": hallazgos_lista,
        "recomendaciones": recomendaciones_lista,
        "confianza_ia": estudio.confianza_ia or 0,
        "requiere_atencion": estudio.requiere_atencion,
        "es_critico": estudio.es_critico,
    }

    generador = get_generador_pdf()
    pdf_buffer = generador.generar_reporte_interpretacion_eeg(datos)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=EEG_Interpretacion_{eeg_id}.pdf"
        },
    )


@router.get("/ecografia/{ecografia_id}/pdf-analisis")
async def generar_pdf_analisis_ecografia(
    ecografia_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Generar PDF con el análisis de parámetros de la Ecografía"""
    from app.services.generador_pdf_estudios_especiales import get_generador_pdf
    from fastapi.responses import StreamingResponse

    result = await db.execute(select(Ecografia).where(Ecografia.id == ecografia_id))
    estudio = result.scalar_one_or_none()
    if not estudio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ecografía no encontrada"
        )

    result_paciente = await db.execute(
        select(Paciente).where(Paciente.id == estudio.paciente_id)
    )
    paciente = result_paciente.scalar_one_or_none()

    datos = {
        "paciente": {
            "nombre_completo": paciente.nombre_completo if paciente else "N/A",
            "edad": paciente.edad if paciente else "N/A",
            "sexo": paciente.genero if paciente else "N/A",
            "fecha_estudio": (
                estudio.fecha_estudio.strftime("%d/%m/%Y %H:%M")
                if estudio.fecha_estudio
                else "N/A"
            ),
            "medico": f"Dr(a). {current_user.nombre_completo if hasattr(current_user, 'nombre_completo') else 'N/A'}",
        },
        "tipo_ecografia": estudio.tipo_ecografia,
        "region_anatomica": estudio.region_anatomica,
        "modo": estudio.modo,
        "via_acceso": estudio.via_acceso,
        "transductor": estudio.transductor,
        "equipo_utilizado": estudio.equipo_utilizado,
        "calidad_estudio": estudio.calidad_estudio,
    }

    generador = get_generador_pdf()
    pdf_buffer = generador.generar_reporte_analisis_ecografia(datos)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=Ecografia_Analisis_{ecografia_id}.pdf"
        },
    )


@router.get("/ecografia/{ecografia_id}/pdf-interpretacion")
async def generar_pdf_interpretacion_ecografia(
    ecografia_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Generar PDF con la interpretación de IA de la Ecografía"""
    from app.services.generador_pdf_estudios_especiales import get_generador_pdf
    from fastapi.responses import StreamingResponse

    result = await db.execute(select(Ecografia).where(Ecografia.id == ecografia_id))
    estudio = result.scalar_one_or_none()
    if not estudio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ecografía no encontrada"
        )

    result_paciente = await db.execute(
        select(Paciente).where(Paciente.id == estudio.paciente_id)
    )
    paciente = result_paciente.scalar_one_or_none()

    # Convertir hallazgos y recomendaciones de string a lista si es necesario
    hallazgos_lista = []
    if estudio.hallazgos:
        if isinstance(estudio.hallazgos, str):
            hallazgos_lista = estudio.hallazgos.split("\n") if estudio.hallazgos else []
        else:
            hallazgos_lista = estudio.hallazgos

    recomendaciones_lista = []
    if estudio.recomendaciones:
        if isinstance(estudio.recomendaciones, str):
            recomendaciones_lista = (
                estudio.recomendaciones.split("\n") if estudio.recomendaciones else []
            )
        else:
            recomendaciones_lista = estudio.recomendaciones

    datos = {
        "paciente": {
            "nombre_completo": paciente.nombre_completo if paciente else "N/A",
            "edad": paciente.edad if paciente else "N/A",
            "sexo": paciente.genero if paciente else "N/A",
            "fecha_estudio": (
                estudio.fecha_estudio.strftime("%d/%m/%Y %H:%M")
                if estudio.fecha_estudio
                else "N/A"
            ),
            "medico": f"Dr(a). {current_user.nombre_completo if hasattr(current_user, 'nombre_completo') else 'N/A'}",
        },
        "clasificacion": estudio.clasificacion,
        "interpretacion": estudio.interpretacion_ia or estudio.interpretacion_medica,
        "hallazgos": hallazgos_lista,
        "recomendaciones": recomendaciones_lista,
        "confianza_ia": estudio.confianza_ia or 0,
        "requiere_atencion": estudio.requiere_atencion,
        "requiere_seguimiento": estudio.requiere_seguimiento,
    }

    generador = get_generador_pdf()
    pdf_buffer = generador.generar_reporte_interpretacion_ecografia(datos)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=Ecografia_Interpretacion_{ecografia_id}.pdf"
        },
    )
