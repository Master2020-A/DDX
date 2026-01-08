"""
Script para inicializar la base de datos con el catálogo completo de laboratorio
Incluye todos los parámetros con rangos por sexo y edad
"""
import sys
import asyncio
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.core.database import AsyncSessionLocal
from app.models.laboratorio import RangoReferencia
from app.data.catalogo_laboratorio import CATALOGO_COMPLETO


async def limpiar_rangos_existentes(session: AsyncSession):
    """Elimina todos los rangos existentes"""
    print("🗑️  Limpiando rangos existentes...")
    await session.execute(delete(RangoReferencia))
    await session.commit()
    print("✅ Rangos anteriores eliminados\n")


async def inicializar_catalogo():
    """Inicializa el catálogo completo en la base de datos"""
    print("="*80)
    print("🔬 INICIALIZACIÓN DEL CATÁLOGO COMPLETO DE LABORATORIO")
    print("="*80)
    print()
    
    async with AsyncSessionLocal() as session:
        try:
            # Limpiar rangos existentes
            await limpiar_rangos_existentes(session)
            
            total_rangos = 0
            rangos_por_area = {}
            
            # Procesar cada área del catálogo
            for area, tipos_prueba in CATALOGO_COMPLETO.items():
                rangos_por_area[area] = 0
                
                print(f"📊 Procesando área: {area.upper()}")
                print("-" * 80)
                
                for tipo_prueba, info_prueba in tipos_prueba.items():
                    print(f"\n  📋 {info_prueba['nombre']}")
                    
                    # Procesar cada parámetro
                    for param_key, param_info in info_prueba['parametros'].items():
                        nombre_param = param_info['nombre_completo']
                        unidad = param_info['unidad']
                        descripcion = param_info.get('descripcion', '')
                        
                        # Obtener interpretaciones
                        interp = param_info.get('interpretacion', {})
                        interp_bajo = interp.get('bajo', '')
                        interp_alto = interp.get('alto', '')
                        
                        # Procesar cada rango (por sexo/edad)
                        rangos = param_info.get('rangos', {})
                        
                        for categoria, valores_rango in rangos.items():
                            # Determinar sexo y grupo etario
                            sexo = None
                            grupo_etario = None
                            
                            if 'hombre' in categoria:
                                sexo = 'M'
                            elif 'mujer' in categoria:
                                sexo = 'F'
                            
                            if 'recien_nacido' in categoria:
                                grupo_etario = 'recien_nacido'
                            elif 'nino' in categoria or 'pediatrico' in categoria:
                                grupo_etario = 'pediatrico'
                            elif 'adolescente' in categoria:
                                grupo_etario = 'adolescente'
                            elif 'embarazada' in categoria:
                                grupo_etario = 'embarazo'
                            elif 'adulto' in categoria:
                                grupo_etario = 'adulto'
                            
                            # Crear el rango
                            rango_data = {
                                'area': area,
                                'tipo_prueba': tipo_prueba,
                                'parametro': param_key,
                                'sexo': sexo,
                                'grupo_etario': grupo_etario,
                                'valor_min': valores_rango.get('min'),
                                'valor_max': valores_rango.get('max'),
                                'critico_bajo': valores_rango.get('critico_bajo'),
                                'critico_alto': valores_rango.get('critico_alto'),
                                'unidad': unidad,
                                'descripcion': descripcion,
                                'interpretacion_bajo': interp_bajo,
                                'interpretacion_alto': interp_alto
                            }
                            
                            rango = RangoReferencia(**rango_data)
                            session.add(rango)
                            
                            # Mostrar información
                            categoria_str = categoria.replace('_', ' ').title()
                            rango_str = f"{valores_rango.get('min', 'N/A')} - {valores_rango.get('max', 'N/A')}"
                            print(f"    ✅ {nombre_param} ({categoria_str}): {rango_str} {unidad}")
                            
                            total_rangos += 1
                            rangos_por_area[area] += 1
                
                print()
            
            # Guardar en la base de datos
            print("💾 Guardando en base de datos...")
            await session.commit()
            
            print()
            print("="*80)
            print("✅ CATÁLOGO INICIALIZADO CORRECTAMENTE")
            print("="*80)
            print()
            print("📋 Resumen por Área:")
            for area, count in rangos_por_area.items():
                print(f"  • {area.upper()}: {count} rangos")
            print()
            print(f"📊 TOTAL DE RANGOS: {total_rangos}")
            print()
            
            # Mostrar estadísticas adicionales
            print("📈 Estadísticas:")
            result = await session.execute(
                select(RangoReferencia.area, RangoReferencia.tipo_prueba)
                .distinct()
            )
            tipos_unicos = result.all()
            print(f"  • Tipos de pruebas: {len(tipos_unicos)}")
            
            result = await session.execute(
                select(RangoReferencia.parametro).distinct()
            )
            params_unicos = result.all()
            print(f"  • Parámetros únicos: {len(params_unicos)}")
            print()
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            raise


if __name__ == "__main__":
    print("\n⚠️  ADVERTENCIA: Este script eliminará todos los rangos existentes")
    print("   y los reemplazará con el catálogo completo.\n")
    
    respuesta = input("¿Desea continuar? (s/n): ")
    if respuesta.lower() == 's':
        asyncio.run(inicializar_catalogo())
    else:
        print("\n❌ Operación cancelada")
