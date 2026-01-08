"""
Script para configurar catálogos del sistema:
1. Ejecuta migración de tablas
2. Puebla datos iniciales
"""
import asyncio
import sys
from pathlib import Path
from app.core.database import engine


async def ejecutar_migracion():
    """Ejecutar migración de catálogos"""
    print("\n" + "="*70)
    print("PASO 1: EJECUTANDO MIGRACIÓN DE CATÁLOGOS")
    print("="*70)
    
    sql_file = Path(__file__).parent / "migrations" / "002_catalogos.sql"
    
    if not sql_file.exists():
        print(f"❌ ERROR: No se encontró {sql_file}")
        return False
    
    print(f"\n📄 Leyendo migración: {sql_file.name}")
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    async with engine.begin() as conn:
        try:
            print("🔄 Ejecutando migración...")
            raw_conn = await conn.get_raw_connection()
            driver_conn = raw_conn.driver_connection
            await driver_conn.execute(sql_content)
            
            print("✅ Migración completada\n")
            print("📊 Tablas creadas:")
            print("   ✓ codigos_postales")
            print("   ✓ instituciones_salud")
            print("   ✓ parentescos")
            print("   ✓ niveles_escolaridad")
            print("   ✓ tipos_examen_laboratorio")
            print("   ✓ sustancias_toxicas")
            
            return True
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False


async def poblar_catalogos():
    """Poblar catálogos con datos iniciales"""
    print("\n" + "="*70)
    print("PASO 2: POBLANDO CATÁLOGOS CON DATOS INICIALES")
    print("="*70 + "\n")
    
    from app.core.database import AsyncSessionLocal
    from app.models.catalogos import (
        InstitucionSalud, Parentesco, NivelEscolaridad,
        TipoExamenLaboratorio, SustanciaToxica
    )
    
    # Instituciones de Salud
    instituciones = [
        {"nombre": "IMSS - Instituto Mexicano del Seguro Social", "tipo": "Seguridad Social", "nivel_atencion": "Todos los niveles"},
        {"nombre": "ISSSTE - Instituto de Seguridad y Servicios Sociales de los Trabajadores del Estado", "tipo": "Seguridad Social", "nivel_atencion": "Todos los niveles"},
        {"nombre": "SSA - Secretaría de Salud", "tipo": "Pública", "nivel_atencion": "Todos los niveles"},
        {"nombre": "IMSS-Bienestar", "tipo": "Pública", "nivel_atencion": "Primer y Segundo nivel"},
        {"nombre": "SEDENA - Servicios de Salud Militar", "tipo": "Militar", "nivel_atencion": "Todos los niveles"},
        {"nombre": "SEMAR - Servicios de Salud Naval", "tipo": "Militar", "nivel_atencion": "Todos los niveles"},
        {"nombre": "Pemex", "tipo": "Seguridad Social", "nivel_atencion": "Todos los niveles"},
        {"nombre": "Cruz Roja Mexicana", "tipo": "Privada", "nivel_atencion": "Urgencias"},
        {"nombre": "Clínica Particular", "tipo": "Privada", "nivel_atencion": "Variable"},
        {"nombre": "Hospital Privado", "tipo": "Privada", "nivel_atencion": "Todos los niveles"},
        {"nombre": "Centro de Salud", "tipo": "Pública", "nivel_atencion": "Primer nivel"},
        {"nombre": "Otro", "tipo": "Otro", "nivel_atencion": "Variable"}
    ]
    
    # Parentescos
    parentescos = [
        {"nombre": "Madre", "orden": 1},
        {"nombre": "Padre", "orden": 2},
        {"nombre": "Tutor(a) legal", "orden": 3},
        {"nombre": "Abuelo(a) materno(a)", "orden": 4},
        {"nombre": "Abuelo(a) paterno(a)", "orden": 5},
        {"nombre": "Tío(a)", "orden": 6},
        {"nombre": "Hermano(a)", "orden": 7},
        {"nombre": "Amigo(a)", "orden": 8},
        {"nombre": "Otro", "orden": 9}
    ]
    
    # Escolaridades
    escolaridades = [
        {"nombre": "Sin escolaridad", "orden": 0},
        {"nombre": "Preescolar", "orden": 1},
        {"nombre": "Primaria incompleta", "orden": 2},
        {"nombre": "Primaria completa", "orden": 3},
        {"nombre": "Secundaria incompleta", "orden": 4},
        {"nombre": "Secundaria completa", "orden": 5},
        {"nombre": "Preparatoria incompleta", "orden": 6},
        {"nombre": "Preparatoria completa", "orden": 7},
        {"nombre": "Técnico o comercial", "orden": 8},
        {"nombre": "Universidad incompleta", "orden": 9},
        {"nombre": "Universidad completa", "orden": 10},
        {"nombre": "Posgrado", "orden": 11}
    ]
    
    # Exámenes
    examenes = [
        {"nombre": "Biometría hemática", "categoria": "Laboratorio", "orden": 1},
        {"nombre": "Química sanguínea", "categoria": "Laboratorio", "orden": 2},
        {"nombre": "EGO (Examen General de Orina)", "categoria": "Laboratorio", "orden": 3},
        {"nombre": "Urocultivo", "categoria": "Laboratorio", "orden": 4},
        {"nombre": "Coproparasitoscópico", "categoria": "Laboratorio", "orden": 5},
        {"nombre": "Coprocultivo", "categoria": "Laboratorio", "orden": 6},
        {"nombre": "Radiografía", "categoria": "Gabinete", "orden": 7},
        {"nombre": "Ultrasonido", "categoria": "Gabinete", "orden": 8},
        {"nombre": "Tomografía", "categoria": "Gabinete", "orden": 9},
        {"nombre": "Electrocardiograma", "categoria": "Gabinete", "orden": 10}
    ]
    
    # Sustancias tóxicas
    sustancias = [
        {"nombre": "Tabaco", "categoria": "Legal", "nivel": "Medio", "orden": 1},
        {"nombre": "Alcohol", "categoria": "Legal", "nivel": "Medio", "orden": 2},
        {"nombre": "Cannabis", "categoria": "Droga", "nivel": "Medio", "orden": 3},
        {"nombre": "Cocaína", "categoria": "Droga", "nivel": "Alto", "orden": 4},
        {"nombre": "Heroína", "categoria": "Droga", "nivel": "Alto", "orden": 5},
        {"nombre": "Metanfetaminas", "categoria": "Droga", "nivel": "Alto", "orden": 6},
        {"nombre": "LSD", "categoria": "Droga", "nivel": "Alto", "orden": 7},
        {"nombre": "Inhalables", "categoria": "Inhalante", "nivel": "Alto", "orden": 8},
        {"nombre": "Antras", "categoria": "Droga", "nivel": "Alto", "orden": 9},
        {"nombre": "Otros", "categoria": "Otro", "nivel": "Variable", "orden": 10}
    ]
    
    async with AsyncSessionLocal() as session:
        try:
            # Poblar instituciones
            for inst_data in instituciones:
                inst = InstitucionSalud(**inst_data, pais="México")
                session.add(inst)
            await session.flush()
            print(f"✅ {len(instituciones)} instituciones de salud")
            
            # Poblar parentescos
            for p_data in parentescos:
                p = Parentesco(**p_data)
                session.add(p)
            await session.flush()
            print(f"✅ {len(parentescos)} tipos de parentesco")
            
            # Poblar escolaridades
            for e_data in escolaridades:
                e = NivelEscolaridad(**e_data, pais="México")
                session.add(e)
            await session.flush()
            print(f"✅ {len(escolaridades)} niveles de escolaridad")
            
            # Poblar exámenes
            for ex_data in examenes:
                ex = TipoExamenLaboratorio(**ex_data)
                session.add(ex)
            await session.flush()
            print(f"✅ {len(examenes)} tipos de examen")
            
            # Poblar sustancias
            for s_data in sustancias:
                s = SustanciaToxica(
                    nombre=s_data["nombre"],
                    categoria=s_data["categoria"],
                    nivel_peligrosidad=s_data["nivel"],
                    orden=s_data["orden"]
                )
                session.add(s)
            await session.flush()
            print(f"✅ {len(sustancias)} sustancias tóxicas")
            
            await session.commit()
            return True
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Ejecutar configuración completa"""
    print("\n" + "="*70)
    print("🔧 CONFIGURACIÓN DE CATÁLOGOS DEL SISTEMA DDX")
    print("="*70)
    
    # Paso 1: Migración
    if not await ejecutar_migracion():
        print("\n❌ Error en la migración. Abortando...")
        return False
    
    # Paso 2: Poblar datos
    if not await poblar_catalogos():
        print("\n❌ Error al poblar catálogos. Abortando...")
        return False
    
    print("\n" + "="*70)
    print("✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
    print("="*70)
    print("\n💡 Los catálogos están listos para usar en:")
    print("   • Formulario de pacientes")
    print("   • Historia clínica")
    print("   • Antecedentes familiares")
    print("\n" + "="*70 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        resultado = asyncio.run(main())
        sys.exit(0 if resultado else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso cancelado")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
