"""
Script para ejecutar TODAS las migraciones y configuración del sistema
"""
import asyncio
import sys
from pathlib import Path
from app.core.database import engine


async def ejecutar_migracion_sql(archivo_sql: Path) -> bool:
    """Ejecutar un archivo SQL de migración"""
    print(f"\n📄 Ejecutando: {archivo_sql.name}")
    
    if not archivo_sql.exists():
        print(f"❌ ERROR: Archivo no encontrado")
        return False
    
    with open(archivo_sql, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    async with engine.begin() as conn:
        try:
            raw_conn = await conn.get_raw_connection()
            driver_conn = raw_conn.driver_connection
            await driver_conn.execute(sql_content)
            print(f"✅ {archivo_sql.name} - Completado")
            return True
        except Exception as e:
            print(f"❌ ERROR en {archivo_sql.name}: {e}")
            return False


async def poblar_catalogos():
    """Poblar catálogos con datos iniciales"""
    print("\n" + "="*70)
    print("POBLANDO CATÁLOGOS CON DATOS INICIALES")
    print("="*70)
    
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
    
    parentescos = [
        {"nombre": "Madre", "orden": 1}, {"nombre": "Padre", "orden": 2},
        {"nombre": "Tutor(a) legal", "orden": 3}, {"nombre": "Abuelo(a) materno(a)", "orden": 4},
        {"nombre": "Abuelo(a) paterno(a)", "orden": 5}, {"nombre": "Tío(a)", "orden": 6},
        {"nombre": "Hermano(a)", "orden": 7}, {"nombre": "Amigo(a)", "orden": 8},
        {"nombre": "Otro", "orden": 9}
    ]
    
    escolaridades = [
        {"nombre": "Sin escolaridad", "orden": 0}, {"nombre": "Preescolar", "orden": 1},
        {"nombre": "Primaria incompleta", "orden": 2}, {"nombre": "Primaria completa", "orden": 3},
        {"nombre": "Secundaria incompleta", "orden": 4}, {"nombre": "Secundaria completa", "orden": 5},
        {"nombre": "Preparatoria incompleta", "orden": 6}, {"nombre": "Preparatoria completa", "orden": 7},
        {"nombre": "Técnico o comercial", "orden": 8}, {"nombre": "Universidad incompleta", "orden": 9},
        {"nombre": "Universidad completa", "orden": 10}, {"nombre": "Posgrado", "orden": 11}
    ]
    
    examenes = [
        {"nombre": "Biometría hemática", "categoria": "Laboratorio", "orden": 1},
        {"nombre": "Química sanguínea", "categoria": "Laboratorio", "orden": 2},
        {"nombre": "EGO (Examen General de Orina)", "categoria": "Laboratorio", "orden": 3},
        {"nombre": "Urocultivo", "categoria": "Laboratorio", "orden": 4},
        {"nombre": "Coproparasitoscópico", "categoria": "Laboratorio", "orden": 5},
        {"nombre": "Radiografía", "categoria": "Gabinete", "orden": 6},
        {"nombre": "Ultrasonido", "categoria": "Gabinete", "orden": 7},
        {"nombre": "Electrocardiograma", "categoria": "Gabinete", "orden": 8}
    ]
    
    sustancias = [
        {"nombre": "Tabaco", "categoria": "Legal", "nivel": "Medio", "orden": 1},
        {"nombre": "Alcohol", "categoria": "Legal", "nivel": "Medio", "orden": 2},
        {"nombre": "Cannabis", "categoria": "Droga", "nivel": "Medio", "orden": 3},
        {"nombre": "Cocaína", "categoria": "Droga", "nivel": "Alto", "orden": 4},
        {"nombre": "Heroína", "categoria": "Droga", "nivel": "Alto", "orden": 5},
        {"nombre": "LSD", "categoria": "Droga", "nivel": "Alto", "orden": 6},
        {"nombre": "Inhalables", "categoria": "Inhalante", "nivel": "Alto", "orden": 7},
        {"nombre": "Antras", "categoria": "Droga", "nivel": "Alto", "orden": 8},
        {"nombre": "Otros", "categoria": "Otro", "nivel": "Variable", "orden": 9}
    ]
    
    async with AsyncSessionLocal() as session:
        try:
            for inst_data in instituciones:
                inst = InstitucionSalud(**inst_data, pais="México")
                session.add(inst)
            print(f"✅ {len(instituciones)} instituciones de salud")
            
            for p_data in parentescos:
                session.add(Parentesco(**p_data))
            print(f"✅ {len(parentescos)} tipos de parentesco")
            
            for e_data in escolaridades:
                session.add(NivelEscolaridad(**e_data, pais="México"))
            print(f"✅ {len(escolaridades)} niveles de escolaridad")
            
            for ex_data in examenes:
                session.add(TipoExamenLaboratorio(**ex_data))
            print(f"✅ {len(examenes)} tipos de examen")
            
            for s_data in sustancias:
                s = SustanciaToxica(
                    nombre=s_data["nombre"], categoria=s_data["categoria"],
                    nivel_peligrosidad=s_data["nivel"], orden=s_data["orden"]
                )
                session.add(s)
            print(f"✅ {len(sustancias)} sustancias tóxicas")
            
            await session.commit()
            return True
            
        except Exception as e:
            await session.rollback()
            print(f"❌ ERROR: {e}")
            return False


async def main():
    """Ejecutar todas las migraciones en orden"""
    print("\n" + "="*70)
    print("🚀 EJECUTANDO TODAS LAS MIGRACIONES DEL SISTEMA DDX")
    print("="*70)
    
    migrations_dir = Path(__file__).parent / "migrations"
    
    # Lista de migraciones en orden
    migraciones = [
        "001_historia_clinica_pediatrica.sql",
        "002_catalogos.sql",
        "003_mejoras_historia_clinica.sql"
    ]
    
    exito_total = True
    
    # Ejecutar migraciones SQL
    print("\n📋 PASO 1: MIGRACIONES SQL")
    print("-" * 70)
    for nombre_mig in migraciones:
        archivo = migrations_dir / nombre_mig
        if not await ejecutar_migracion_sql(archivo):
            exito_total = False
            print(f"\n⚠️  WARNING: Migración {nombre_mig} falló, continuando...")
    
    # Poblar catálogos
    print("\n📋 PASO 2: POBLAR CATÁLOGOS")
    print("-" * 70)
    if not await poblar_catalogos():
        exito_total = False
    
    # Resumen final
    print("\n" + "="*70)
    if exito_total:
        print("✅ TODAS LAS MIGRACIONES COMPLETADAS EXITOSAMENTE")
    else:
        print("⚠️  MIGRACIONES COMPLETADAS CON ALGUNOS ERRORES")
    print("="*70)
    
    print("\n📊 RESUMEN:")
    print("   ✓ Tablas de Historia Clínica")
    print("   ✓ Tablas de Catálogos")
    print("   ✓ Mejoras a Historia Clínica")
    print("   ✓ Datos de catálogos poblados")
    
    print("\n💡 SIGUIENTE PASO:")
    print("   Iniciar el backend:")
    print("   > uvicorn app.main:app --reload --port=8612")
    print("\n" + "="*70 + "\n")
    
    return exito_total


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
