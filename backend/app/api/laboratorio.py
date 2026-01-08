"""
Endpoints para manejo de resultados de laboratorio clínico
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from uuid import UUID
import tempfile
import os

from app.core.database import get_db
from app.api.dependencies import get_current_active_medico
from app.models.usuario import Usuario
from app.models.paciente import Paciente
from app.models.laboratorio import PruebaLaboratorio, RangoReferencia
from app.services.laboratorio_service import get_analizador
from app.services.extractor_laboratorio import obtener_extractor
from app.services.generador_pdf_laboratorio import get_generador_pdf_laboratorio
from pydantic import BaseModel
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


# Schemas
class ResultadoLaboratorio(BaseModel):
    """Resultado de una prueba de laboratorio"""
    parametro: str
    valor: float


class CrearPruebaLaboratorio(BaseModel):
    """Request para crear nueva prueba de laboratorio"""
    paciente_id: UUID
    consulta_id: Optional[UUID] = None
    area: str
    tipo_prueba: str
    resultados: List[ResultadoLaboratorio]
    laboratorio_externo: Optional[str] = None
    numero_orden: Optional[str] = None
    fecha_resultado: Optional[datetime] = None
    notas_medico: Optional[str] = None


class ActualizarPruebaLaboratorio(BaseModel):
    """Request para actualizar prueba de laboratorio"""
    resultados: Optional[List[ResultadoLaboratorio]] = None
    estado: Optional[str] = None
    notas_medico: Optional[str] = None


@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_prueba_laboratorio(
    prueba_data: CrearPruebaLaboratorio,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Crea nuevo registro de prueba de laboratorio y analiza resultados
    """
    # Verificar que el paciente existe
    result = await db.execute(
        select(Paciente).where(Paciente.id == prueba_data.paciente_id)
    )
    paciente = result.scalar_one_or_none()
    
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    
    try:
        # Convertir resultados a diccionario
        resultados_dict = {r.parametro: r.valor for r in prueba_data.resultados}
        
        # Obtener rangos de referencia
        result = await db.execute(
            select(RangoReferencia).where(
                RangoReferencia.area == prueba_data.area,
                RangoReferencia.activo == True
            )
        )
        rangos = result.scalars().all()
        
        if not rangos:
            logger.warning(f"No se encontraron rangos para área: {prueba_data.area}")
        
        # Convertir rangos a diccionarios
        rangos_dict = [
            {
                'parametro': r.parametro,
                'sexo': r.sexo,
                'edad_min': r.edad_min,
                'edad_max': r.edad_max,
                'valor_min': r.valor_min,
                'valor_max': r.valor_max,
                'critico_bajo': r.critico_bajo,
                'critico_alto': r.critico_alto,
                'unidad': r.unidad,
                'interpretacion_bajo': r.interpretacion_bajo,
                'interpretacion_alto': r.interpretacion_alto
            }
            for r in rangos
        ]
        
        # Analizar resultados
        analizador = get_analizador()
        analisis = analizador.analizar_resultados(
            area=prueba_data.area,
            tipo_prueba=prueba_data.tipo_prueba,
            resultados=resultados_dict,
            rangos=rangos_dict,
            sexo=paciente.sexo,
            edad=paciente.edad
        )
        
        # Crear registro de prueba
        nueva_prueba = PruebaLaboratorio(
            paciente_id=prueba_data.paciente_id,
            consulta_id=prueba_data.consulta_id,
            medico_id=current_user.id,
            area=prueba_data.area,
            tipo_prueba=prueba_data.tipo_prueba,
            resultados=resultados_dict,
            interpretacion=analisis.get('interpretacion'),
            valores_anormales=analisis.get('valores_anormales'),
            valores_criticos=analisis.get('valores_criticos'),
            estado='completado',
            requiere_atencion=analisis.get('requiere_atencion', False),
            laboratorio_externo=prueba_data.laboratorio_externo,
            numero_orden=prueba_data.numero_orden,
            fecha_resultado=prueba_data.fecha_resultado or datetime.utcnow(),
            notas_medico=prueba_data.notas_medico
        )
        
        db.add(nueva_prueba)
        await db.commit()
        await db.refresh(nueva_prueba)
        
        logger.info(f"Prueba de laboratorio creada: {nueva_prueba.id}")
        
        return {
            'id': str(nueva_prueba.id),
            'paciente_id': str(nueva_prueba.paciente_id),
            'area': nueva_prueba.area,
            'tipo_prueba': nueva_prueba.tipo_prueba,
            'resultados': nueva_prueba.resultados,
            'interpretacion': nueva_prueba.interpretacion,
            'valores_anormales': nueva_prueba.valores_anormales,
            'valores_criticos': nueva_prueba.valores_criticos,
            'requiere_atencion': nueva_prueba.requiere_atencion,
            'estado': nueva_prueba.estado,
            'fecha_resultado': nueva_prueba.fecha_resultado.isoformat(),
            'created_at': nueva_prueba.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creando prueba de laboratorio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando prueba de laboratorio: {str(e)}"
        )


@router.get("/paciente/{paciente_id}")
async def listar_pruebas_paciente(
    paciente_id: UUID,
    area: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Lista todas las pruebas de laboratorio de un paciente
    """
    query = select(PruebaLaboratorio).where(
        PruebaLaboratorio.paciente_id == paciente_id
    )
    
    if area:
        query = query.where(PruebaLaboratorio.area == area)
    
    query = query.order_by(PruebaLaboratorio.fecha_resultado.desc())
    
    result = await db.execute(query)
    pruebas = result.scalars().all()
    
    return [
        {
            'id': str(p.id),
            'area': p.area,
            'tipo_prueba': p.tipo_prueba,
            'fecha_resultado': p.fecha_resultado.isoformat() if p.fecha_resultado else None,
            'estado': p.estado,
            'requiere_atencion': p.requiere_atencion,
            'valores_criticos_count': len(p.valores_criticos) if p.valores_criticos else 0,
            'valores_anormales_count': len(p.valores_anormales) if p.valores_anormales else 0,
            'laboratorio_externo': p.laboratorio_externo,
            'numero_orden': p.numero_orden
        }
        for p in pruebas
    ]


@router.get("/{prueba_id}")
async def obtener_prueba_detalle(
    prueba_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Obtiene detalles completos de una prueba de laboratorio
    """
    result = await db.execute(
        select(PruebaLaboratorio).where(PruebaLaboratorio.id == prueba_id)
    )
    prueba = result.scalar_one_or_none()
    
    if not prueba:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prueba no encontrada"
        )
    
    return {
        'id': str(prueba.id),
        'paciente_id': str(prueba.paciente_id),
        'consulta_id': str(prueba.consulta_id) if prueba.consulta_id else None,
        'medico_id': str(prueba.medico_id),
        'area': prueba.area,
        'tipo_prueba': prueba.tipo_prueba,
        'resultados': prueba.resultados,
        'interpretacion': prueba.interpretacion,
        'valores_anormales': prueba.valores_anormales,
        'valores_criticos': prueba.valores_criticos,
        'estado': prueba.estado,
        'requiere_atencion': prueba.requiere_atencion,
        'laboratorio_externo': prueba.laboratorio_externo,
        'numero_orden': prueba.numero_orden,
        'fecha_solicitud': prueba.fecha_solicitud.isoformat(),
        'fecha_resultado': prueba.fecha_resultado.isoformat() if prueba.fecha_resultado else None,
        'notas_medico': prueba.notas_medico,
        'created_at': prueba.created_at.isoformat(),
        'updated_at': prueba.updated_at.isoformat()
    }


@router.put("/{prueba_id}")
async def actualizar_prueba(
    prueba_id: UUID,
    update_data: ActualizarPruebaLaboratorio,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Actualiza una prueba de laboratorio existente y re-analiza los resultados
    """
    result = await db.execute(
        select(PruebaLaboratorio).where(PruebaLaboratorio.id == prueba_id)
    )
    prueba = result.scalar_one_or_none()
    
    if not prueba:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prueba no encontrada"
        )
    
    # Actualizar campos básicos
    if update_data.estado:
        prueba.estado = update_data.estado
    
    if update_data.notas_medico is not None:
        prueba.notas_medico = update_data.notas_medico
    
    # Si se actualizan resultados, re-analizar completamente
    if update_data.resultados:
        logger.info(f"🔄 Re-analizando prueba {prueba_id} con {len(update_data.resultados)} parámetros")
        
        # Convertir resultados a dict
        resultados_dict = {r.parametro: r.valor for r in update_data.resultados}
        prueba.resultados = resultados_dict
        
        # Obtener paciente para edad y sexo
        result_paciente = await db.execute(
            select(Paciente).where(Paciente.id == prueba.paciente_id)
        )
        paciente = result_paciente.scalar_one_or_none()
        
        if paciente:
            # Obtener rangos de referencia
            result_rangos = await db.execute(
                select(RangoReferencia).where(
                    RangoReferencia.area == prueba.area,
                    RangoReferencia.tipo_prueba == prueba.tipo_prueba,
                    RangoReferencia.activo == True
                )
            )
            rangos = result_rangos.scalars().all()
            
            # Analizar resultados
            analizador = get_analizador()
            analisis = analizador.analizar_resultados(
                resultados=resultados_dict,
                rangos=rangos,
                sexo=paciente.sexo,
                edad=paciente.edad
            )
            
            # Actualizar análisis
            prueba.estado = analisis['estado']
            prueba.requiere_atencion = analisis['requiere_atencion']
            prueba.valores_criticos_count = analisis['valores_criticos']
            prueba.valores_anormales_count = analisis['valores_anormales']
            prueba.interpretacion_clinica = analisis['interpretacion']
            
            logger.info(f"✅ Prueba re-analizada: {analisis['valores_anormales']} anormales, {analisis['valores_criticos']} críticos")
        
    await db.commit()
    await db.refresh(prueba)
    
    return {
        'mensaje': 'Prueba actualizada y re-analizada correctamente',
        'id': str(prueba.id),
        'estado': prueba.estado,
        'requiere_atencion': prueba.requiere_atencion
    }


@router.get("/rangos/")
async def obtener_todos_rangos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Obtiene todos los rangos de referencia del catálogo completo
    """
    result = await db.execute(
        select(RangoReferencia).where(
            RangoReferencia.activo == True
        ).order_by(
            RangoReferencia.area,
            RangoReferencia.tipo_prueba,
            RangoReferencia.parametro
        )
    )
    rangos = result.scalars().all()
    
    return [
        {
            'parametro': r.parametro,
            'area': r.area,
            'tipo_prueba': r.tipo_prueba,
            'nombre_completo': r.descripcion,  # Usar descripción como nombre completo por ahora
            'sexo': r.sexo,
            'grupo_etario': r.grupo_etario,
            'edad_min': r.edad_min,
            'edad_max': r.edad_max,
            'valor_min': r.valor_min,
            'valor_max': r.valor_max,
            'critico_bajo': r.critico_bajo,
            'critico_alto': r.critico_alto,
            'unidad': r.unidad,
            'descripcion': r.descripcion,
            'interpretacion_bajo': r.interpretacion_bajo,
            'interpretacion_alto': r.interpretacion_alto
        }
        for r in rangos
    ]


@router.get("/rangos/area/{area}")
async def obtener_rangos_area(
    area: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Obtiene todos los rangos de referencia de un área específica
    """
    result = await db.execute(
        select(RangoReferencia).where(
            RangoReferencia.area == area,
            RangoReferencia.activo == True
        )
    )
    rangos = result.scalars().all()
    
    return [
        {
            'parametro': r.parametro,
            'tipo_prueba': r.tipo_prueba,
            'sexo': r.sexo,
            'edad_min': r.edad_min,
            'edad_max': r.edad_max,
            'valor_min': r.valor_min,
            'valor_max': r.valor_max,
            'unidad': r.unidad,
            'descripcion': r.descripcion
        }
        for r in rangos
    ]


@router.post("/extraer-desde-archivo/")
async def extraer_laboratorio_desde_archivo(
    archivo: UploadFile = File(...),
    paciente_id: UUID = Form(...),
    consulta_id: Optional[UUID] = Form(None),
    laboratorio_externo: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Extrae datos de laboratorio desde un archivo PDF o imagen
    
    - **archivo**: Archivo PDF o imagen (JPG, PNG, etc.)
    - **paciente_id**: ID del paciente
    - **consulta_id**: ID de la consulta (opcional)
    - **laboratorio_externo**: Nombre del laboratorio (opcional)
    
    Returns:
        - Datos extraídos y sugerencias para crear la prueba
    """
    # Verificar que el paciente existe
    result = await db.execute(
        select(Paciente).where(Paciente.id == paciente_id)
    )
    paciente = result.scalar_one_or_none()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    
    # Verificar tipo de archivo
    extension = archivo.filename.split('.')[-1].lower()
    tipos_permitidos = ['pdf', 'jpg', 'jpeg', 'png', 'bmp', 'tiff']
    
    if extension not in tipos_permitidos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no soportado. Use: {', '.join(tipos_permitidos)}"
        )
    
    # Guardar archivo temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{extension}') as temp_file:
        contenido = await archivo.read()
        temp_file.write(contenido)
        temp_path = temp_file.name
    
    try:
        # Obtener extractor
        extractor = obtener_extractor()
        
        # Extraer datos según tipo de archivo
        if extension == 'pdf':
            resultado = extractor.extraer_desde_pdf(temp_path)
        else:
            resultado = extractor.extraer_desde_imagen(temp_path)
        
        if not resultado['exito']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al extraer datos: {resultado.get('error', 'Error desconocido')}"
            )
        
        # Formatear para API
        datos_formateados = extractor.formatear_para_api(
            resultado['resultados'],
            str(paciente_id),
            str(consulta_id) if consulta_id else None,
            laboratorio_externo
        )
        
        return {
            'exito': True,
            'parametros_encontrados': resultado['parametros_encontrados'],
            'resultados_extraidos': resultado['resultados'],
            'area_sugerida': datos_formateados['area'],
            'tipo_prueba_sugerido': datos_formateados['tipo_prueba'],
            'metodo_extraccion': resultado['metodo'],
            'datos_para_crear': datos_formateados,
            'texto_extraido': resultado.get('texto_extraido', '')[:500]  # Primeros 500 chars
        }
        
    finally:
        # Limpiar archivo temporal
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@router.post("/extraer-y-crear-desde-archivo/")
async def extraer_y_crear_laboratorio_desde_archivo(
    archivo: UploadFile = File(...),
    paciente_id: UUID = Form(...),
    consulta_id: Optional[UUID] = Form(None),
    laboratorio_externo: Optional[str] = Form(None),
    numero_orden: Optional[str] = Form(None),
    notas_medico: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Extrae datos de laboratorio desde un archivo y crea automáticamente la prueba
    
    - **archivo**: Archivo PDF o imagen
    - **paciente_id**: ID del paciente
    - **consulta_id**: ID de la consulta (opcional)
    - **laboratorio_externo**: Nombre del laboratorio (opcional)
    - **numero_orden**: Número de orden (opcional)
    - **notas_medico**: Notas adicionales (opcional)
    
    Returns:
        - Prueba de laboratorio creada con análisis automático
    """
    # Verificar que el paciente existe
    result = await db.execute(
        select(Paciente).where(Paciente.id == paciente_id)
    )
    paciente = result.scalar_one_or_none()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    
    # Verificar tipo de archivo
    extension = archivo.filename.split('.')[-1].lower()
    tipos_permitidos = ['pdf', 'jpg', 'jpeg', 'png', 'bmp', 'tiff']
    
    if extension not in tipos_permitidos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no soportado. Use: {', '.join(tipos_permitidos)}"
        )
    
    # Guardar archivo temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{extension}') as temp_file:
        contenido = await archivo.read()
        temp_file.write(contenido)
        temp_path = temp_file.name
    
    try:
        # Obtener extractor
        extractor = obtener_extractor()
        
        # Extraer datos
        if extension == 'pdf':
            resultado = extractor.extraer_desde_pdf(temp_path)
        else:
            resultado = extractor.extraer_desde_imagen(temp_path)
        
        if not resultado['exito']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al extraer datos: {resultado.get('error', 'Error desconocido')}"
            )
        
        if resultado['parametros_encontrados'] == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se encontraron parámetros de laboratorio en el archivo"
            )
        
        # Formatear resultados
        try:
            area, tipo_prueba = extractor.detectar_area_y_tipo(resultado['resultados'])
        except Exception as e:
            logger.error(f"Error detectando área y tipo: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se pudo determinar el área o tipo de prueba automáticamente. "
                       f"Los parámetros extraídos no coinciden con ningún tipo conocido. "
                       f"Intente con captura manual."
            )
        
        if not area or not tipo_prueba:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo determinar el área o tipo de prueba. Use captura manual."
            )
        
        # Crear prueba de laboratorio
        nueva_prueba = PruebaLaboratorio(
            paciente_id=paciente_id,
            consulta_id=consulta_id,
            medico_id=current_user.id,
            area=area,
            tipo_prueba=tipo_prueba,
            resultados=resultado['resultados'],
            laboratorio_externo=laboratorio_externo or f"Extraído de {archivo.filename}",
            numero_orden=numero_orden,
            fecha_resultado=datetime.now(),
            notas_medico=notas_medico,
            estado='pendiente'
        )
        
        # Analizar resultados
        try:
            analizador = get_analizador()
            # Usar el diccionario original, no el campo del modelo (que se convierte a JSON)
            analisis = await analizador.analizar_resultados(
                resultado['resultados'],  # Diccionario original
                nueva_prueba.area,
                nueva_prueba.tipo_prueba,
                paciente.edad,
                paciente.sexo,
                db
            )
            
            # Actualizar prueba con análisis
            nueva_prueba.valores_anormales = analisis['valores_anormales']
            nueva_prueba.valores_criticos = analisis['valores_criticos']
            nueva_prueba.interpretacion = analisis['interpretacion']
            nueva_prueba.requiere_atencion = analisis['requiere_atencion']
            nueva_prueba.estado = 'completado'
        except Exception as e:
            logger.error(f"Error analizando resultados: {e}")
            # Guardar sin análisis
            nueva_prueba.estado = 'pendiente'
            nueva_prueba.notas_medico = (nueva_prueba.notas_medico or '') + f"\n[Error en análisis automático: {str(e)}]"
        
        try:
            db.add(nueva_prueba)
            await db.commit()
            await db.refresh(nueva_prueba)
        except Exception as e:
            logger.error(f"Error guardando prueba en BD: {e}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al guardar la prueba en la base de datos: {str(e)}"
            )
        
        logger.info(f"Prueba de laboratorio creada desde archivo: {nueva_prueba.id}")
        
        return {
            'id': str(nueva_prueba.id),
            'paciente_id': str(nueva_prueba.paciente_id),
            'area': nueva_prueba.area,
            'tipo_prueba': nueva_prueba.tipo_prueba,
            'resultados': nueva_prueba.resultados,
            'valores_anormales': nueva_prueba.valores_anormales,
            'valores_criticos': nueva_prueba.valores_criticos,
            'interpretacion': nueva_prueba.interpretacion,
            'requiere_atencion': nueva_prueba.requiere_atencion,
            'estado': nueva_prueba.estado,
            'parametros_extraidos': resultado['parametros_encontrados'],
            'metodo_extraccion': resultado['metodo'],
            'created_at': nueva_prueba.created_at.isoformat()
        }
        
    finally:
        # Limpiar archivo temporal
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@router.get("/{prueba_id}/pdf")
async def generar_pdf_laboratorio(
    prueba_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Generar reporte PDF de una prueba de laboratorio
    """
    # Obtener prueba
    result = await db.execute(
        select(PruebaLaboratorio).where(PruebaLaboratorio.id == prueba_id)
    )
    prueba = result.scalar_one_or_none()
    
    if not prueba:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prueba de laboratorio no encontrada"
        )
    
    # Obtener datos del paciente
    result_paciente = await db.execute(
        select(Paciente).where(Paciente.id == prueba.paciente_id)
    )
    paciente = result_paciente.scalar_one_or_none()
    
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    
    # Preparar datos de la prueba
    # Convertir resultados de objeto a array si es necesario
    resultados_array = []
    if prueba.resultados:
        if isinstance(prueba.resultados, list):
            resultados_array = prueba.resultados
        elif isinstance(prueba.resultados, dict):
            # Convertir objeto a array
            resultados_array = [
                {'parametro': k, 'valor': v}
                for k, v in prueba.resultados.items()
            ]
    
    # Convertir alertas/valores_criticos a formato de texto
    alertas_texto = []
    if prueba.valores_criticos:
        for vc in prueba.valores_criticos:
            if isinstance(vc, dict):
                alertas_texto.append(vc.get('interpretacion', str(vc)))
            else:
                alertas_texto.append(str(vc))
    
    prueba_data = {
        'id': str(prueba.id),
        'area': prueba.area,
        'tipo_prueba': prueba.tipo_prueba,
        'fecha': prueba.fecha_resultado.isoformat() if prueba.fecha_resultado else (prueba.fecha_solicitud.isoformat() if prueba.fecha_solicitud else None),
        'estado': prueba.estado,
        'laboratorio_externo': prueba.laboratorio_externo,
        'numero_orden': prueba.numero_orden,
        'resultados': resultados_array,
        'interpretacion_clinica': prueba.interpretacion if prueba.interpretacion else '',
        'alertas': alertas_texto,
        'notas_medico': prueba.notas_medico
    }
    
    # Calcular edad del paciente
    edad = 'N/A'
    if paciente.fecha_nacimiento:
        from datetime import date
        hoy = date.today()
        edad = hoy.year - paciente.fecha_nacimiento.year - ((hoy.month, hoy.day) < (paciente.fecha_nacimiento.month, paciente.fecha_nacimiento.day))
    
    # Preparar datos del paciente
    paciente_data = {
        'nombre_completo': paciente.nombre_completo,
        'numero_expediente': paciente.numero_expediente,
        'fecha_nacimiento': paciente.fecha_nacimiento.strftime('%d/%m/%Y') if paciente.fecha_nacimiento else 'N/A',
        'edad': edad,
        'sexo': paciente.sexo
    }
    
    # Generar PDF
    try:
        generador = get_generador_pdf_laboratorio()
        pdf_buffer = generador.generar_reporte_laboratorio(prueba_data, paciente_data)
        
        # Crear nombre del archivo
        area_limpia = prueba.area.replace('_', ' ').title()
        tipo_limpio = prueba.tipo_prueba.replace('_', ' ').title()
        nombre_archivo = f"Laboratorio_{area_limpia}_{tipo_limpio}_{paciente.numero_expediente}.pdf"
        
        # Retornar PDF
        return Response(
            content=pdf_buffer.getvalue(),
            media_type='application/pdf',
            headers={
                "Content-Disposition": f'attachment; filename="{nombre_archivo}"',
                "Cache-Control": "no-cache"
            }
        )
    except Exception as e:
        logger.error(f"Error generando PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el PDF: {str(e)}"
        )
