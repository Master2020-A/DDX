from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Response
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from uuid import UUID
import os
import shutil
from pathlib import Path
from datetime import datetime
import logging

from app.core.database import get_db
from app.models.imagen_medica import ImagenMedica
from app.models.usuario import Usuario
from app.schemas.imagen_medica import (
    ImagenMedicaCreate,
    ImagenMedicaResponse,
    ImagenMedicaUpdate,
    GaleriaResponse,
    SolicitudAnalisisIA
)
from app.api.dependencies import get_current_active_medico
from app.services.imagen_ia_service import imagen_ia_service
from app.services.imagen_ia_multimodal_service import get_servicio_multimodal
from app.services.generador_reportes_pdf_basico import get_generador_pdf

# Configurar logger
logger = logging.getLogger(__name__)

# Importación opcional de procesador NIfTI
try:
    from app.services.nifti_processor import get_nifti_processor
    NIFTI_DISPONIBLE = True
    logger.info("✅ Procesador NIfTI disponible")
except ImportError as e:
    logger.warning(f"⚠️ Procesador NIfTI no disponible: {e}")
    logger.warning("   Instala nibabel para soporte NIfTI: pip install nibabel")
    NIFTI_DISPONIBLE = False
    get_nifti_processor = None

router = APIRouter()

# Configuración de almacenamiento
UPLOAD_DIR = Path("uploads/imagenes_medicas")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {
    'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 
    'image/bmp', 'image/tiff', 'application/dicom',
    # Formatos de imágenes médicas 3D/4D
    'application/octet-stream',  # NIfTI (.nii, .nii.gz)
    'application/x-nifti',
    'application/gzip',  # .nii.gz
}
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB (para imágenes 3D)


@router.post("/upload", response_model=ImagenMedicaResponse, status_code=status.HTTP_201_CREATED)
async def subir_imagen(
    archivo: UploadFile = File(...),
    paciente_id: str = Form(...),
    titulo: str = Form(...),
    tipo_imagen: str = Form(...),
    descripcion: Optional[str] = Form(None),
    consulta_id: Optional[str] = Form(None),
    region_anatomica: Optional[str] = Form(None),
    lateralidad: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Sube una imagen médica al sistema
    Soporta: JPEG, PNG, DICOM, NIfTI (.nii, .nii.gz), TIFF, etc.
    """
    # Obtener extensión del archivo
    extension = Path(archivo.filename).suffix.lower()
    
    # Validar tipo de archivo (por content-type Y extensión)
    extensiones_validas = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', 
                          '.dcm', '.dicom', '.nii', '.gz'}
    
    es_valido = (
        archivo.content_type in ALLOWED_EXTENSIONS or 
        extension in extensiones_validas or
        archivo.filename.endswith('.nii.gz')  # Caso especial para .nii.gz
    )
    
    if not es_valido:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido. Formatos soportados: JPEG, PNG, DICOM, NIfTI (.nii, .nii.gz), TIFF"
        )
    
    # Leer archivo y validar tamaño
    contenido = await archivo.read()
    if len(contenido) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El archivo excede el tamaño máximo de {MAX_FILE_SIZE / 1024 / 1024} MB"
        )
    
    # Generar nombre único para el archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extension = Path(archivo.filename).suffix.lower()
    nombre_archivo = f"{paciente_id}_{timestamp}_{archivo.filename}"
    ruta_completa = UPLOAD_DIR / nombre_archivo
    
    # Guardar archivo
    with open(ruta_completa, "wb") as f:
        f.write(contenido)
    
    # Detectar tipo de formato médico
    es_dicom = archivo.content_type == 'application/dicom' or extension == '.dcm' or extension == '.dicom'
    es_nifti = extension == '.nii' or archivo.filename.endswith('.nii.gz')
    
    # Log para debugging
    logger.info(f"Archivo subido: {archivo.filename}")
    logger.info(f"Extension: {extension}")
    logger.info(f"Content-Type: {archivo.content_type}")
    logger.info(f"Es NIfTI: {es_nifti}")
    logger.info(f"Es DICOM: {es_dicom}")
    
    # Construir URL para acceder a la imagen
    url_archivo = f"/uploads/imagenes_medicas/{nombre_archivo}"
    
    # Crear registro en BD
    nueva_imagen = ImagenMedica(
        paciente_id=UUID(paciente_id),
        consulta_id=UUID(consulta_id) if consulta_id else None,
        usuario_id=current_user.id,
        nombre_archivo=archivo.filename,
        ruta_archivo=str(ruta_completa),
        url_archivo=url_archivo,
        tipo_archivo=archivo.content_type,
        tamanio_bytes=len(contenido),
        titulo=titulo,
        descripcion=descripcion,
        tipo_imagen=tipo_imagen,
        region_anatomica=region_anatomica,
        lateralidad=lateralidad,
        es_dicom=es_dicom
    )
    
    db.add(nueva_imagen)
    await db.commit()
    await db.refresh(nueva_imagen)
    
    # Procesar archivos NIfTI para generar previews
    if es_nifti:
        if NIFTI_DISPONIBLE:
            try:
                logger.info(f"🧠 Procesando archivo NIfTI: {archivo.filename}")
                nifti_processor = get_nifti_processor()
                
                # Extraer metadatos
                metadatos = nifti_processor.extraer_metadatos(str(ruta_completa))
                
                # Generar previews en directorio específico
                preview_dir = UPLOAD_DIR / "previews" / str(nueva_imagen.id)
                resultado_proceso = nifti_processor.procesar_para_visualizacion(
                    str(ruta_completa),
                    preview_dir
                )
                
                # Convertir rutas absolutas de previews a URLs relativas
                previews_urls = {}
                for eje, ruta_absoluta in resultado_proceso.get('previews', {}).items():
                    # Convertir ruta absoluta a relativa desde "uploads"
                    ruta_path = Path(ruta_absoluta)
                    ruta_relativa = ruta_path.relative_to(Path("uploads"))
                    # Crear URL con barras normales
                    preview_url = f"/uploads/{ruta_relativa.as_posix()}"
                    previews_urls[eje] = preview_url
                
                # Actualizar imagen con metadatos NIfTI
                nueva_imagen.resultados_ia = {
                    'nifti_metadatos': metadatos,
                    'nifti_previews': previews_urls,
                    'procesado_nifti': True
                }
                
                await db.commit()
                await db.refresh(nueva_imagen)
                
                logger.info(f"✅ Archivo NIfTI procesado exitosamente")
                
            except Exception as e:
                logger.error(f"❌ Error procesando NIfTI: {e}")
                # No fallar el upload si falla el procesamiento
        else:
            logger.warning(f"⚠️ Archivo NIfTI subido pero no procesado (falta nibabel)")
            nueva_imagen.resultados_ia = {
                'nifti_metadatos': {'error': 'nibabel no instalado'},
                'procesado_nifti': False
            }
            await db.commit()
            await db.refresh(nueva_imagen)
    
    return nueva_imagen


@router.get("/paciente/{paciente_id}", response_model=GaleriaResponse)
async def listar_imagenes_paciente(
    paciente_id: UUID,
    tipo_imagen: Optional[str] = None,
    region_anatomica: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Lista todas las imágenes de un paciente con filtros opcionales
    """
    query = select(ImagenMedica).where(ImagenMedica.paciente_id == paciente_id)
    
    if tipo_imagen:
        query = query.where(ImagenMedica.tipo_imagen == tipo_imagen)
    
    if region_anatomica:
        query = query.where(ImagenMedica.region_anatomica == region_anatomica)
    
    query = query.order_by(ImagenMedica.created_at.desc())
    
    result = await db.execute(query)
    imagenes = result.scalars().all()
    
    # Estadísticas
    por_tipo = {}
    por_region = {}
    
    for img in imagenes:
        por_tipo[img.tipo_imagen] = por_tipo.get(img.tipo_imagen, 0) + 1
        if img.region_anatomica:
            por_region[img.region_anatomica] = por_region.get(img.region_anatomica, 0) + 1
    
    return GaleriaResponse(
        total=len(imagenes),
        imagenes=imagenes,
        por_tipo=por_tipo,
        por_region=por_region
    )


@router.get("/{imagen_id}", response_model=ImagenMedicaResponse)
async def obtener_imagen(
    imagen_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Obtiene los metadatos de una imagen específica
    """
    result = await db.execute(
        select(ImagenMedica).where(ImagenMedica.id == imagen_id)
    )
    imagen = result.scalar_one_or_none()
    
    if not imagen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagen no encontrada"
        )
    
    return imagen


@router.get("/{imagen_id}/download")
async def descargar_imagen(
    imagen_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Descarga el archivo de imagen
    """
    result = await db.execute(
        select(ImagenMedica).where(ImagenMedica.id == imagen_id)
    )
    imagen = result.scalar_one_or_none()
    
    if not imagen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagen no encontrada"
        )
    
    if not os.path.exists(imagen.ruta_archivo):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo de imagen no encontrado en el servidor"
        )
    
    return FileResponse(
        path=imagen.ruta_archivo,
        filename=imagen.nombre_archivo,
        media_type=imagen.tipo_archivo
    )


@router.put("/{imagen_id}", response_model=ImagenMedicaResponse)
async def actualizar_imagen(
    imagen_id: UUID,
    imagen_data: ImagenMedicaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Actualiza los metadatos de una imagen (título, descripción, anotaciones)
    """
    result = await db.execute(
        select(ImagenMedica).where(ImagenMedica.id == imagen_id)
    )
    imagen = result.scalar_one_or_none()
    
    if not imagen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagen no encontrada"
        )
    
    # Actualizar campos
    update_data = imagen_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(imagen, field, value)
    
    await db.commit()
    await db.refresh(imagen)
    
    return imagen


@router.delete("/{imagen_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_imagen(
    imagen_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Elimina una imagen y su archivo asociado
    """
    result = await db.execute(
        select(ImagenMedica).where(ImagenMedica.id == imagen_id)
    )
    imagen = result.scalar_one_or_none()
    
    if not imagen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagen no encontrada"
        )
    
    # Eliminar archivo físico
    if os.path.exists(imagen.ruta_archivo):
        os.remove(imagen.ruta_archivo)
    
    # Eliminar registro de BD
    await db.delete(imagen)
    await db.commit()
    
    return None


def _generar_hallazgos_nifti(analisis_avanzado: dict) -> list:
    """Genera hallazgos legibles desde el análisis avanzado"""
    hallazgos = []
    
    # Métricas globales
    if 'metricas_globales' in analisis_avanzado:
        m = analisis_avanzado['metricas_globales']
        hallazgos.append(f"Volumen de tejido: {m['volumen_tejido_cm3']:.1f} cm³")
    
    # Análisis multiplanar
    if 'analisis_multiplanar' in analisis_avanzado:
        planos_validos = []
        for plano, datos in analisis_avanzado['analisis_multiplanar'].items():
            if not datos.get('vacio'):
                planos_validos.append(f"{plano} ({datos['porcentaje_ocupacion']:.1f}% ocupación)")
        if planos_validos:
            hallazgos.append(f"Análisis multiplanar completado: {', '.join(planos_validos)}")
    
    # Calidad
    if 'calidad_imagen' in analisis_avanzado and 'error' not in analisis_avanzado['calidad_imagen']:
        c = analisis_avanzado['calidad_imagen']
        hallazgos.append(f"Calidad de imagen: {c['calidad_estimada']}")
        for rec in c.get('recomendaciones', []):
            hallazgos.append(rec)
    
    # Regiones detectadas
    if 'deteccion_regiones' in analisis_avanzado:
        r = analisis_avanzado['deteccion_regiones']
        if 'regiones_principales' in r and len(r['regiones_principales']) > 0:
            hallazgos.append(f"Detectadas {len(r['regiones_principales'])} regiones principales de interés")
    
    return hallazgos


@router.post("/{imagen_id}/analizar-ia", response_model=ImagenMedicaResponse)
async def analizar_imagen_ia(
    imagen_id: UUID,
    solicitud: Optional[SolicitudAnalisisIA] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Solicita análisis de IA para una imagen médica
    """
    result = await db.execute(
        select(ImagenMedica).where(ImagenMedica.id == imagen_id)
    )
    imagen = result.scalar_one_or_none()
    
    if not imagen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagen no encontrada"
        )
    
    if not os.path.exists(imagen.ruta_archivo):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo de imagen no encontrado"
        )
    
    # Determinar ruta de archivo para análisis
    # Para archivos NIfTI, usar el preview PNG en lugar del .nii
    ruta_analisis = imagen.ruta_archivo
    if imagen.resultados_ia and 'nifti_previews' in imagen.resultados_ia:
        # Es un archivo NIfTI, usar preview axial
        preview_url = imagen.resultados_ia['nifti_previews'].get('axial')
        if preview_url:
            # Convertir URL a ruta de archivo
            # /uploads/imagenes_medicas/previews/... -> uploads/imagenes_medicas/previews/...
            ruta_preview = preview_url.lstrip('/')
            if os.path.exists(ruta_preview):
                ruta_analisis = ruta_preview
                logger.info(f"🧠 Usando preview NIfTI para análisis: {ruta_preview}")
            else:
                logger.warning(f"⚠️ Preview NIfTI no encontrado: {ruta_preview}")
    
    # Obtener servicio multi-modal
    servicio_multimodal = get_servicio_multimodal()
    
    # Ejecutar análisis según tipo de imagen y región
    resultado_ia = await servicio_multimodal.analizar_imagen(
        imagen_path=ruta_analisis,
        tipo_imagen=imagen.tipo_imagen,
        region_anatomica=imagen.region_anatomica or "general",
        umbral_confianza=solicitud.umbral_confianza if solicitud else 0.5
    )
    
    # Si es archivo NIfTI, ejecutar análisis avanzado adicional
    if imagen.resultados_ia and 'nifti_previews' in imagen.resultados_ia:
        logger.info(f"🧠 Ejecutando análisis avanzado de NIfTI...")
        
        try:
            from app.services.nifti_analisis_avanzado import get_analisis_avanzado
            
            analizador = get_analisis_avanzado()
            analisis_avanzado = analizador.analizar_completo(imagen.ruta_archivo)
            
            if 'error' not in analisis_avanzado:
                # Combinar resultados
                resultado_ia['nifti_previews'] = imagen.resultados_ia['nifti_previews']
                resultado_ia['nifti_metadatos'] = imagen.resultados_ia.get('nifti_metadatos')
                resultado_ia['nifti_analisis_avanzado'] = analisis_avanzado
                resultado_ia['procesado_nifti'] = True
                
                # Generar hallazgos detallados basados en análisis avanzado
                hallazgos_avanzados = _generar_hallazgos_nifti(analisis_avanzado)
                if hallazgos_avanzados:
                    resultado_ia['hallazgos'] = resultado_ia.get('hallazgos', []) + hallazgos_avanzados
                
                logger.info(f"✅ Análisis avanzado NIfTI completado")
            else:
                logger.warning(f"⚠️ Error en análisis avanzado: {analisis_avanzado['error']}")
                # Preservar metadatos básicos
                resultado_ia['nifti_previews'] = imagen.resultados_ia['nifti_previews']
                resultado_ia['nifti_metadatos'] = imagen.resultados_ia.get('nifti_metadatos')
                resultado_ia['procesado_nifti'] = True
                
        except Exception as e:
            logger.error(f"❌ Error en análisis avanzado NIfTI: {e}")
            # Preservar metadatos básicos si falla
            resultado_ia['nifti_previews'] = imagen.resultados_ia['nifti_previews']
            resultado_ia['nifti_metadatos'] = imagen.resultados_ia.get('nifti_metadatos')
            resultado_ia['procesado_nifti'] = True
    
    imagen.analisis_ia_completado = True
    imagen.resultados_ia = resultado_ia
    imagen.confianza_ia = resultado_ia.get('confianza_global', 0.0)
    imagen.hallazgos = resultado_ia.get('hallazgos', [])
    
    await db.commit()
    await db.refresh(imagen)
    
    return imagen


@router.get("/{imagen_id}/reporte-avanzado")
async def obtener_reporte_avanzado(
    imagen_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Obtiene reporte detallado de análisis avanzado para imágenes NIfTI
    """
    result = await db.execute(
        select(ImagenMedica).where(ImagenMedica.id == imagen_id)
    )
    imagen = result.scalar_one_or_none()
    
    if not imagen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagen no encontrada"
        )
    
    # Verificar si tiene análisis avanzado
    if not imagen.resultados_ia or 'nifti_analisis_avanzado' not in imagen.resultados_ia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Esta imagen no tiene análisis avanzado. Ejecute el análisis IA primero."
        )
    
    # Generar reporte legible
    try:
        from app.services.nifti_analisis_avanzado import get_analisis_avanzado
        
        analizador = get_analisis_avanzado()
        analisis = imagen.resultados_ia['nifti_analisis_avanzado']
        reporte_texto = analizador.generar_reporte_detallado(analisis, imagen.nombre_archivo)
        
        return {
            'imagen_id': str(imagen.id),
            'nombre_archivo': imagen.nombre_archivo,
            'analisis_completo': analisis,
            'reporte_texto': reporte_texto,
            'timestamp': imagen.updated_at.isoformat() if imagen.updated_at else None
        }
        
    except Exception as e:
        logger.error(f"Error generando reporte: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando reporte: {str(e)}"
        )


@router.post("/{imagen_id}/segmentar-anatomico")
async def segmentar_anatomico(
    imagen_id: UUID,
    fast: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Ejecuta segmentación anatómica con TotalSegmentator en imagen NIfTI
    """
    result = await db.execute(
        select(ImagenMedica).where(ImagenMedica.id == imagen_id)
    )
    imagen = result.scalar_one_or_none()
    
    if not imagen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagen no encontrada"
        )
    
    # Verificar que es archivo NIfTI
    if not (imagen.nombre_archivo.endswith('.nii') or imagen.nombre_archivo.endswith('.nii.gz')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede segmentar archivos NIfTI (.nii o .nii.gz)"
        )
    
    if not os.path.exists(imagen.ruta_archivo):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado"
        )
    
    try:
        from app.services.segmentacion_anatomica import get_segmentador
        
        segmentador = get_segmentador()
        
        print(f"\n{'='*80}")
        print(f"🔬 DEBUG: Iniciando segmentación anatómica")
        print(f"   Archivo: {imagen.nombre_archivo}")
        print(f"   TotalSegmentator disponible: {segmentador.totalsegmentator_disponible}")
        print(f"{'='*80}\n")
        
        # Crear directorio para segmentación
        seg_dir = UPLOAD_DIR / "segmentaciones" / str(imagen.id)
        
        logger.warning(f"🔬 Iniciando segmentación anatómica para {imagen.nombre_archivo}...")
        
        # Ejecutar segmentación
        resultado_seg = segmentador.segmentar_completo(
            ruta_archivo=imagen.ruta_archivo,
            output_dir=seg_dir,
            fast=fast
        )
        
        print(f"\n{'='*80}")
        print(f"✅ DEBUG: Segmentación completada")
        print(f"   Método: {resultado_seg.get('metodo', 'desconocido')}")
        print(f"   Estructuras: {resultado_seg.get('total_estructuras', 0)}")
        print(f"{'='*80}\n")
        
        if 'error' in resultado_seg:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error en segmentación: {resultado_seg['error']}"
            )
        
        # Generar datos de visualización
        vis_data = segmentador.generar_visualizacion_3d(resultado_seg, top_n=15)
        
        # Actualizar resultados en imagen
        if not imagen.resultados_ia:
            imagen.resultados_ia = {}
        
        imagen.resultados_ia['segmentacion_anatomica'] = resultado_seg
        imagen.resultados_ia['visualizacion_3d'] = vis_data
        
        await db.commit()
        await db.refresh(imagen)
        
        logger.info(f"✅ Segmentación completada: {resultado_seg.get('total_estructuras', 0)} estructuras")
        
        return {
            'imagen_id': str(imagen.id),
            'segmentacion': resultado_seg,
            'visualizacion': vis_data,
            'mensaje': resultado_seg.get('mensaje', 'Segmentación completada')
        }
        
    except Exception as e:
        logger.error(f"❌ Error en segmentación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ejecutando segmentación: {str(e)}"
        )


@router.get("/{imagen_id}/visualizacion-3d")
async def obtener_visualizacion_3d(
    imagen_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Obtiene datos de visualización 3D de estructuras segmentadas
    """
    result = await db.execute(
        select(ImagenMedica).where(ImagenMedica.id == imagen_id)
    )
    imagen = result.scalar_one_or_none()
    
    if not imagen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagen no encontrada"
        )
    
    if not imagen.resultados_ia or 'visualizacion_3d' not in imagen.resultados_ia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay datos de visualización 3D. Ejecute segmentación primero."
        )
    
    return {
        'imagen_id': str(imagen.id),
        'nombre_archivo': imagen.nombre_archivo,
        'visualizacion': imagen.resultados_ia['visualizacion_3d'],
        'segmentacion_disponible': 'segmentacion_anatomica' in imagen.resultados_ia
    }


@router.get("/estadisticas/general")
async def estadisticas_imagenes(
    paciente_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Obtiene estadísticas generales de imágenes
    """
    query = select(ImagenMedica)
    
    if paciente_id:
        query = query.where(ImagenMedica.paciente_id == paciente_id)
    
    result = await db.execute(query)
    imagenes = result.scalars().all()
    
    estadisticas = {
        "total_imagenes": len(imagenes),
        "total_bytes": sum(img.tamanio_bytes for img in imagenes),
        "por_tipo": {},
        "por_region": {},
        "con_analisis_ia": sum(1 for img in imagenes if img.analisis_ia_completado),
        "dicom": sum(1 for img in imagenes if img.es_dicom),
        "con_anotaciones": sum(1 for img in imagenes if img.anotaciones)
    }
    
    for img in imagenes:
        estadisticas["por_tipo"][img.tipo_imagen] = estadisticas["por_tipo"].get(img.tipo_imagen, 0) + 1
        if img.region_anatomica:
            estadisticas["por_region"][img.region_anatomica] = estadisticas["por_region"].get(img.region_anatomica, 0) + 1
    
    return estadisticas


@router.get("/ia/disponibilidad")
async def obtener_disponibilidad_ia(
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Obtiene información sobre qué modelos de IA están disponibles
    """
    servicio_multimodal = get_servicio_multimodal()
    
    disponibilidad = servicio_multimodal.obtener_disponibilidad()
    modelos_cargados = servicio_multimodal.obtener_modelos_cargados()
    
    return {
        "disponibilidad": disponibilidad,
        "modelos_cargados": modelos_cargados,
        "capacidades": {
            "rayos_x_torax": {
                "disponible": disponibilidad.get("rayos_x_torax", False),
                "patologias": [
                    "Atelectasis", "Cardiomegaly", "Consolidation", "Edema",
                    "Effusion", "Emphysema", "Fibrosis", "Infiltration",
                    "Mass", "Nodule", "Pleural_Thickening", "Pneumonia",
                    "Pneumothorax", "Hernia"
                ] if disponibilidad.get("rayos_x_torax", False) else []
            },
            "tomografia": {
                "disponible": disponibilidad.get("tomografia", False),
                "regiones": ["craneo", "torax", "abdomen", "columna"]
            },
            "resonancia": {
                "disponible": disponibilidad.get("resonancia", False),
                "regiones": ["craneo", "columna", "rodilla", "hombro"]
            },
            "ecografia": {
                "disponible": True,
                "regiones": ["abdomen", "pelvis", "cuello", "tiroides"]
            },
            "mamografia": {
                "disponible": True,
                "clasificacion": "BIRADS"
            },
            "endoscopia": {
                "disponible": True,
                "tipos": ["gastrica", "colonoscopia"]
            }
        }
    }


@router.get("/segmentacion/info")
async def obtener_info_segmentacion(
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Obtiene información sobre los modelos de segmentación avanzada disponibles
    """
    servicio_multimodal = get_servicio_multimodal()
    return servicio_multimodal.obtener_info_segmentacion()


@router.post("/{imagen_id}/segmentar")
async def segmentar_imagen(
    imagen_id: UUID,
    tipo_segmentacion: str = "auto",
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Ejecuta segmentación avanzada en una imagen
    
    Tipos disponibles:
    - auto: Análisis completo automático
    - pulmones: Segmentación de pulmones (LungMask)
    - total: Segmentación de 104 estructuras (TotalSegmentator)  
    - lesiones: Detección de lesiones (DeepLesion)
    """
    # Buscar imagen
    result = await db.execute(
        select(ImagenMedica).where(ImagenMedica.id == imagen_id)
    )
    imagen = result.scalar_one_or_none()
    
    if not imagen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagen no encontrada"
        )
    
    # Verificar que la imagen existe en disco
    if not imagen.ruta_archivo or not os.path.exists(imagen.ruta_archivo):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo de imagen no encontrado"
        )
    
    try:
        # Ejecutar segmentación
        servicio_multimodal = get_servicio_multimodal()
        resultado = servicio_multimodal.segmentar_imagen(
            ruta_imagen=imagen.ruta_archivo,
            tipo_segmentacion=tipo_segmentacion
        )
        
        # Actualizar base de datos con resultados de segmentación
        if not resultado.get('error'):
            if imagen.resultados_ia is None:
                imagen.resultados_ia = {}
            
            # Agregar resultados de segmentación
            imagen.resultados_ia['segmentacion'] = {
                'tipo': tipo_segmentacion,
                'fecha': datetime.now().isoformat(),
                'resultados': resultado
            }
            
            await db.commit()
            
        return resultado
        
    except Exception as e:
        logger.error(f"Error en segmentación de imagen {imagen_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en segmentación: {str(e)}"
        )


@router.get("/{imagen_id}/nifti-preview/{eje}")
async def obtener_preview_nifti(
    imagen_id: UUID,
    eje: str = "axial",
    slice_idx: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Obtiene preview 2D de un archivo NIfTI en el eje especificado
    
    Args:
        imagen_id: ID de la imagen
        eje: 'axial', 'sagital' o 'coronal'
        slice_idx: Índice del corte (opcional, por defecto corte medio)
    """
    # Verificar disponibilidad de procesador NIfTI
    if not NIFTI_DISPONIBLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Procesador NIfTI no disponible. Instala nibabel: pip install nibabel"
        )
    
    # Buscar imagen
    result = await db.execute(
        select(ImagenMedica).where(ImagenMedica.id == imagen_id)
    )
    imagen = result.scalar_one_or_none()
    
    if not imagen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagen no encontrada"
        )
    
    # Verificar que sea NIfTI
    if not (imagen.nombre_archivo.endswith('.nii') or imagen.nombre_archivo.endswith('.nii.gz')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La imagen no es un archivo NIfTI"
        )
    
    # Validar eje
    if eje not in ['axial', 'sagital', 'coronal']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Eje debe ser: axial, sagital o coronal"
        )
    
    try:
        nifti_processor = get_nifti_processor()
        preview_bytes = nifti_processor.generar_preview_2d(
            imagen.ruta_archivo,
            slice_idx=slice_idx,
            eje=eje
        )
        
        if preview_bytes is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error generando preview"
            )
        
        return Response(
            content=preview_bytes,
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=3600"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generando preview NIfTI: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando preview: {str(e)}"
        )


@router.get("/{imagen_id}/reporte-pdf")
async def generar_reporte_pdf(
    imagen_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Genera y descarga un reporte PDF detallado del análisis IA
    """
    result = await db.execute(
        select(ImagenMedica).where(ImagenMedica.id == imagen_id)
    )
    imagen = result.scalar_one_or_none()

    if not imagen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagen no encontrada"
        )

    try:
        # Obtener generador de PDF
        generador_pdf = get_generador_pdf()

        # Preparar datos de la imagen
        imagen_data = {
            'id': str(imagen.id),
            'titulo': imagen.titulo,
            'descripcion': imagen.descripcion,
            'tipo_imagen': imagen.tipo_imagen,
            'region_anatomica': imagen.region_anatomica,
            'lateralidad': imagen.lateralidad,
            'tamanio_bytes': imagen.tamanio_bytes,
            'created_at': imagen.created_at.isoformat() if imagen.created_at else None,
            'analisis_ia_completado': imagen.analisis_ia_completado,
            'resultados_ia': imagen.resultados_ia,
            'hallazgos': imagen.hallazgos,
            'confianza_ia': imagen.confianza_ia
        }

        # Generar PDF
        ruta_imagen = imagen.ruta_archivo if imagen.ruta_archivo and os.path.exists(imagen.ruta_archivo) else None
        pdf_buffer = generador_pdf.generar_reporte_ia(imagen_data, ruta_imagen)

        # Crear nombre del archivo
        titulo_limpio = "".join(c for c in imagen.titulo if c.isalnum() or c in (' ', '-', '_')).rstrip()
        nombre_archivo = f"reporte_ia_{titulo_limpio}.pdf"

        # Retornar como Response con contenido binario
        return Response(
            content=pdf_buffer.getvalue(),
            media_type='application/pdf',
            headers={
                "Content-Disposition": f'attachment; filename="{nombre_archivo}"',
                "Cache-Control": "no-cache"
            }
        )

    except Exception as e:
        logger.error(f"Error generando PDF para imagen {imagen_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando reporte PDF: {str(e)}"
        )
