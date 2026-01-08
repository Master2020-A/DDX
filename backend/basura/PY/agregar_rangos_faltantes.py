"""
Script para agregar rangos de referencia faltantes
"""
import sys
import asyncio
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.laboratorio import RangoReferencia


# Nuevos rangos a agregar
NUEVOS_RANGOS = [
    # ÍNDICES ERITROCITARIOS
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'vcm',
        'valor_min': 80.0,
        'valor_max': 100.0,
        'unidad': 'fL',
        'descripcion': 'Volumen Corpuscular Medio',
        'interpretacion_bajo': 'Microcitosis - anemia ferropénica',
        'interpretacion_alto': 'Macrocitosis - deficiencia B12/folato'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'hcm',
        'valor_min': 27.0,
        'valor_max': 31.0,
        'unidad': 'pg',
        'descripcion': 'Hemoglobina Corpuscular Media',
        'interpretacion_bajo': 'Hipocromía',
        'interpretacion_alto': 'Hipercromía'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'chcm',
        'valor_min': 32.0,
        'valor_max': 36.0,
        'unidad': 'g/dL',
        'descripcion': 'Concentración de Hemoglobina Corpuscular Media'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'rdw',
        'valor_min': 11.5,
        'valor_max': 14.5,
        'unidad': '%',
        'descripcion': 'Amplitud de Distribución Eritrocitaria',
        'interpretacion_alto': 'Anisocitosis'
    },
    # VALORES ABSOLUTOS
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'neutrofilos_abs',
        'valor_min': 1.8,
        'valor_max': 7.7,
        'critico_bajo': 0.5,
        'critico_alto': 20.0,
        'unidad': 'x10³/μL',
        'descripcion': 'Neutrófilos absolutos',
        'interpretacion_bajo': 'Neutropenia',
        'interpretacion_alto': 'Neutrofilia'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'linfocitos_abs',
        'valor_min': 1.0,
        'valor_max': 4.8,
        'critico_bajo': 0.5,
        'unidad': 'x10³/μL',
        'descripcion': 'Linfocitos absolutos'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'monocitos_abs',
        'valor_min': 0.2,
        'valor_max': 1.0,
        'unidad': 'x10³/μL',
        'descripcion': 'Monocitos absolutos'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'eosinofilos_abs',
        'valor_min': 0.0,
        'valor_max': 0.5,
        'unidad': 'x10³/μL',
        'descripcion': 'Eosinófilos absolutos'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'basofilos_abs',
        'valor_min': 0.0,
        'valor_max': 0.2,
        'unidad': 'x10³/μL',
        'descripcion': 'Basófilos absolutos'
    },
    # BANDAS Y SEGMENTADOS
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'bandas',
        'valor_min': 0.0,
        'valor_max': 3.0,
        'unidad': '%',
        'descripcion': 'Neutrófilos en banda',
        'interpretacion_alto': 'Desviación a la izquierda'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'segmentados',
        'valor_min': 40.0,
        'valor_max': 70.0,
        'unidad': '%',
        'descripcion': 'Neutrófilos segmentados'
    },
]


async def agregar_rangos():
    """Agrega rangos faltantes a la base de datos"""
    print("="*80)
    print("🔬 AGREGANDO RANGOS DE REFERENCIA FALTANTES")
    print("="*80)
    print()
    
    async with AsyncSessionLocal() as session:
        try:
            print(f"📊 Insertando {len(NUEVOS_RANGOS)} nuevos rangos...")
            print()
            
            for rango_data in NUEVOS_RANGOS:
                rango = RangoReferencia(**rango_data)
                session.add(rango)
                
                print(f"  ✅ {rango_data['parametro']} ({rango_data['unidad']})")
            
            await session.commit()
            
            print()
            print("="*80)
            print("✅ RANGOS AGREGADOS CORRECTAMENTE")
            print("="*80)
            print()
            print(f"Total de rangos agregados: {len(NUEVOS_RANGOS)}")
            print()
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(agregar_rangos())
