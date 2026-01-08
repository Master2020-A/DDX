"""
Script para poblar la base de datos con rangos de referencia de laboratorio
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.laboratorio import RangoReferencia
from app.core.config import settings

# Rangos de referencia comunes
RANGOS_REFERENCIA = [
    # HEMATOLOGÍA - Biometría Hemática
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'hemoglobina',
        'sexo': 'M',
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 13.5,
        'valor_max': 17.5,
        'unidad': 'g/dL',
        'descripcion': 'Hemoglobina en hombres adultos',
        'activo': True
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'hemoglobina',
        'sexo': 'F',
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 12.0,
        'valor_max': 16.0,
        'unidad': 'g/dL',
        'descripcion': 'Hemoglobina en mujeres adultas',
        'activo': True
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'hematocrito',
        'sexo': 'M',
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 40.0,
        'valor_max': 54.0,
        'unidad': '%',
        'descripcion': 'Hematocrito en hombres adultos',
        'activo': True
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'hematocrito',
        'sexo': 'F',
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 36.0,
        'valor_max': 48.0,
        'unidad': '%',
        'descripcion': 'Hematocrito en mujeres adultas',
        'activo': True
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'leucocitos',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 4.5,
        'valor_max': 11.0,
        'unidad': 'K/µL',
        'descripcion': 'Leucocitos totales',
        'activo': True
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'plaquetas',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 150.0,
        'valor_max': 450.0,
        'unidad': 'K/µL',
        'descripcion': 'Plaquetas',
        'activo': True
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'eritrocitos',
        'sexo': 'M',
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 4.5,
        'valor_max': 5.9,
        'unidad': 'M/µL',
        'descripcion': 'Eritrocitos en hombres',
        'activo': True
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'eritrocitos',
        'sexo': 'F',
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 4.0,
        'valor_max': 5.2,
        'unidad': 'M/µL',
        'descripcion': 'Eritrocitos en mujeres',
        'activo': True
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'neutrofilos',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 40.0,
        'valor_max': 70.0,
        'unidad': '%',
        'descripcion': 'Neutrófilos',
        'activo': True
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'linfocitos',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 20.0,
        'valor_max': 40.0,
        'unidad': '%',
        'descripcion': 'Linfocitos',
        'activo': True
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'monocitos',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 2.0,
        'valor_max': 8.0,
        'unidad': '%',
        'descripcion': 'Monocitos',
        'activo': True
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'eosinofilos',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 1.0,
        'valor_max': 4.0,
        'unidad': '%',
        'descripcion': 'Eosinófilos',
        'activo': True
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'basofilos',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 0.0,
        'valor_max': 1.0,
        'unidad': '%',
        'descripcion': 'Basófilos',
        'activo': True
    },
    
    # QUÍMICA CLÍNICA - Glucosa
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'glucosa',
        'parametro': 'glucosa',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 70.0,
        'valor_max': 100.0,
        'unidad': 'mg/dL',
        'descripcion': 'Glucosa en ayunas',
        'activo': True
    },
    
    # QUÍMICA CLÍNICA - Función Renal
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_renal',
        'parametro': 'creatinina',
        'sexo': 'M',
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 0.7,
        'valor_max': 1.3,
        'unidad': 'mg/dL',
        'descripcion': 'Creatinina en hombres',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_renal',
        'parametro': 'creatinina',
        'sexo': 'F',
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 0.6,
        'valor_max': 1.1,
        'unidad': 'mg/dL',
        'descripcion': 'Creatinina en mujeres',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_renal',
        'parametro': 'urea',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 16.6,
        'valor_max': 48.5,
        'unidad': 'mg/dL',
        'descripcion': 'Urea',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_renal',
        'parametro': 'acido_urico',
        'sexo': 'M',
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 3.5,
        'valor_max': 7.2,
        'unidad': 'mg/dL',
        'descripcion': 'Ácido úrico en hombres',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_renal',
        'parametro': 'acido_urico',
        'sexo': 'F',
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 2.6,
        'valor_max': 6.0,
        'unidad': 'mg/dL',
        'descripcion': 'Ácido úrico en mujeres',
        'activo': True
    },
    
    # QUÍMICA CLÍNICA - Perfil Lipídico
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'perfil_lipidico',
        'parametro': 'colesterol_total',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 0.0,
        'valor_max': 200.0,
        'unidad': 'mg/dL',
        'descripcion': 'Colesterol total deseable',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'perfil_lipidico',
        'parametro': 'trigliceridos',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 0.0,
        'valor_max': 150.0,
        'unidad': 'mg/dL',
        'descripcion': 'Triglicéridos normales',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'perfil_lipidico',
        'parametro': 'hdl',
        'sexo': 'M',
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 40.0,
        'valor_max': 999.0,
        'unidad': 'mg/dL',
        'descripcion': 'HDL en hombres (mayor es mejor)',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'perfil_lipidico',
        'parametro': 'hdl',
        'sexo': 'F',
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 50.0,
        'valor_max': 999.0,
        'unidad': 'mg/dL',
        'descripcion': 'HDL en mujeres (mayor es mejor)',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'perfil_lipidico',
        'parametro': 'ldl',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 0.0,
        'valor_max': 100.0,
        'unidad': 'mg/dL',
        'descripcion': 'LDL óptimo',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'perfil_lipidico',
        'parametro': 'vldl',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 2.0,
        'valor_max': 30.0,
        'unidad': 'mg/dL',
        'descripcion': 'VLDL',
        'activo': True
    },
    
    # QUÍMICA CLÍNICA - Función Hepática
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_hepatica',
        'parametro': 'tgo',
        'sexo': 'M',
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 0.0,
        'valor_max': 40.0,
        'unidad': 'U/L',
        'descripcion': 'TGO/AST en hombres',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_hepatica',
        'parametro': 'tgo',
        'sexo': 'F',
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 0.0,
        'valor_max': 32.0,
        'unidad': 'U/L',
        'descripcion': 'TGO/AST en mujeres',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_hepatica',
        'parametro': 'tgp',
        'sexo': 'M',
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 0.0,
        'valor_max': 41.0,
        'unidad': 'U/L',
        'descripcion': 'TGP/ALT en hombres',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_hepatica',
        'parametro': 'tgp',
        'sexo': 'F',
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 0.0,
        'valor_max': 33.0,
        'unidad': 'U/L',
        'descripcion': 'TGP/ALT en mujeres',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_hepatica',
        'parametro': 'bilirrubina_total',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 0.3,
        'valor_max': 1.2,
        'unidad': 'mg/dL',
        'descripcion': 'Bilirrubina total',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_hepatica',
        'parametro': 'bilirrubina_directa',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 0.0,
        'valor_max': 0.3,
        'unidad': 'mg/dL',
        'descripcion': 'Bilirrubina directa',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_hepatica',
        'parametro': 'bilirrubina_indirecta',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 0.2,
        'valor_max': 0.9,
        'unidad': 'mg/dL',
        'descripcion': 'Bilirrubina indirecta',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_hepatica',
        'parametro': 'fosfatasa_alcalina',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 40.0,
        'valor_max': 130.0,
        'unidad': 'U/L',
        'descripcion': 'Fosfatasa alcalina',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_hepatica',
        'parametro': 'proteinas_totales',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 6.0,
        'valor_max': 8.3,
        'unidad': 'g/dL',
        'descripcion': 'Proteínas totales',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_hepatica',
        'parametro': 'albumina',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 3.5,
        'valor_max': 5.5,
        'unidad': 'g/dL',
        'descripcion': 'Albúmina',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_hepatica',
        'parametro': 'globulinas',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 2.0,
        'valor_max': 3.5,
        'unidad': 'g/dL',
        'descripcion': 'Globulinas',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_hepatica',
        'parametro': 'ggt',
        'sexo': 'M',
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 0.0,
        'valor_max': 60.0,
        'unidad': 'U/L',
        'descripcion': 'Gamma-glutamil transferasa en hombres',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_hepatica',
        'parametro': 'ggt',
        'sexo': 'F',
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 0.0,
        'valor_max': 40.0,
        'unidad': 'U/L',
        'descripcion': 'Gamma-glutamil transferasa en mujeres',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_hepatica',
        'parametro': 'ldh',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 140.0,
        'valor_max': 280.0,
        'unidad': 'U/L',
        'descripcion': 'Lactato deshidrogenasa',
        'activo': True
    },
    
    # ELECTROLITOS
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'electrolitos',
        'parametro': 'sodio',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 136.0,
        'valor_max': 145.0,
        'unidad': 'mEq/L',
        'descripcion': 'Sodio sérico',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'electrolitos',
        'parametro': 'potasio',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 3.5,
        'valor_max': 5.1,
        'unidad': 'mEq/L',
        'descripcion': 'Potasio sérico',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'electrolitos',
        'parametro': 'cloro',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 98.0,
        'valor_max': 107.0,
        'unidad': 'mEq/L',
        'descripcion': 'Cloro sérico',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'electrolitos',
        'parametro': 'calcio',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 8.5,
        'valor_max': 10.5,
        'unidad': 'mg/dL',
        'descripcion': 'Calcio sérico',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'electrolitos',
        'parametro': 'magnesio',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 1.7,
        'valor_max': 2.2,
        'unidad': 'mg/dL',
        'descripcion': 'Magnesio sérico',
        'activo': True
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'electrolitos',
        'parametro': 'fosforo',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 2.5,
        'valor_max': 4.5,
        'unidad': 'mg/dL',
        'descripcion': 'Fósforo sérico',
        'activo': True
    },
    
    # INMUNOLOGÍA
    {
        'area': 'inmunologia',
        'tipo_prueba': 'pcr',
        'parametro': 'pcr',
        'sexo': None,
        'edad_min': 18,
        'edad_max': 120,
        'valor_min': 0.0,
        'valor_max': 3.0,
        'unidad': 'mg/L',
        'descripcion': 'Proteína C Reactiva',
        'activo': True
    },
    
    # VSG
    {
        'area': 'hematologia',
        'tipo_prueba': 'vsg',
        'parametro': 'vsg',
        'sexo': 'M',
        'edad_min': 18,
        'edad_max': 50,
        'valor_min': 0.0,
        'valor_max': 15.0,
        'unidad': 'mm/h',
        'descripcion': 'VSG en hombres menores de 50 años',
        'activo': True
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'vsg',
        'parametro': 'vsg',
        'sexo': 'M',
        'edad_min': 50,
        'edad_max': 120,
        'valor_min': 0.0,
        'valor_max': 20.0,
        'unidad': 'mm/h',
        'descripcion': 'VSG en hombres mayores de 50 años',
        'activo': True
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'vsg',
        'parametro': 'vsg',
        'sexo': 'F',
        'edad_min': 18,
        'edad_max': 50,
        'valor_min': 0.0,
        'valor_max': 20.0,
        'unidad': 'mm/h',
        'descripcion': 'VSG en mujeres menores de 50 años',
        'activo': True
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'vsg',
        'parametro': 'vsg',
        'sexo': 'F',
        'edad_min': 50,
        'edad_max': 120,
        'valor_min': 0.0,
        'valor_max': 30.0,
        'unidad': 'mm/h',
        'descripcion': 'VSG en mujeres mayores de 50 años',
        'activo': True
    },
]


async def poblar_rangos():
    """Pobla la base de datos con rangos de referencia"""
    # Crear engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True
    )
    
    # Crear sesión
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            print("🔄 Poblando rangos de referencia...")
            
            # Insertar rangos
            for rango_data in RANGOS_REFERENCIA:
                rango = RangoReferencia(**rango_data)
                session.add(rango)
            
            await session.commit()
            print(f"✅ {len(RANGOS_REFERENCIA)} rangos de referencia insertados correctamente")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(poblar_rangos())
