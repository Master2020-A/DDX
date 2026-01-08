"""
Script de verificación del sistema DDX
Verifica BD, datos, y configuración
"""
import asyncio
from sqlalchemy import select, func, text
from app.core.database import AsyncSessionLocal
from app.models.paciente import Paciente
from app.models.consulta import Consulta
from app.models.catalogos import CodigoPostal


async def verificar_sistema():
    """Verificar estado del sistema"""
    print("="*70)
    print("VERIFICACIÓN DEL SISTEMA DDX")
    print("="*70)
    print()
    
    async with AsyncSessionLocal() as db:
        try:
            # 1. Verificar conexión a BD
            print("1️⃣  CONEXIÓN A BASE DE DATOS")
            await db.execute(text("SELECT 1"))
            print("   ✅ Conexión exitosa")
            print()
            
            # 2. Verificar pacientes
            print("2️⃣  PACIENTES")
            result = await db.execute(select(func.count(Paciente.id)))
            total_pacientes = result.scalar()
            print(f"   📊 Total: {total_pacientes}")
            
            if total_pacientes > 0:
                result = await db.execute(
                    select(Paciente).limit(3).order_by(Paciente.created_at.desc())
                )
                pacientes = result.scalars().all()
                print("   📋 Últimos 3 pacientes:")
                for p in pacientes:
                    print(f"      - {p.nombre_completo} ({p.genero})")
            else:
                print("   ⚠️  No hay pacientes registrados")
            print()
            
            # 3. Verificar consultas
            print("3️⃣  CONSULTAS")
            result = await db.execute(select(func.count(Consulta.id)))
            total_consultas = result.scalar()
            print(f"   📊 Total: {total_consultas}")
            
            if total_consultas > 0:
                result = await db.execute(
                    select(Consulta).limit(3).order_by(Consulta.fecha_hora.desc())
                )
                consultas = result.scalars().all()
                print("   📋 Últimas 3 consultas:")
                for c in consultas:
                    print(f"      - Estado: {c.estado} | Fecha: {c.fecha_hora}")
            else:
                print("   ⚠️  No hay consultas registradas")
            print()
            
            # 4. Verificar códigos postales
            print("4️⃣  CÓDIGOS POSTALES")
            result = await db.execute(select(func.count(CodigoPostal.id)))
            total_cps = result.scalar()
            print(f"   📊 Total registros: {total_cps}")
            
            # Verificar CP 83288
            result = await db.execute(
                select(CodigoPostal).where(CodigoPostal.codigo_postal == "83288")
            )
            cps_83288 = result.scalars().all()
            print(f"   🏘️  CP 83288: {len(cps_83288)} colonias")
            
            if cps_83288:
                print("   📋 Colonias del CP 83288:")
                for cp in cps_83288[:5]:
                    print(f"      - {cp.colonia}")
                if len(cps_83288) > 5:
                    print(f"      ... y {len(cps_83288) - 5} más")
            else:
                print("   ⚠️  CP 83288 no encontrado")
            print()
            
            # 5. Resumen
            print("="*70)
            print("📊 RESUMEN")
            print("="*70)
            
            if total_pacientes == 0:
                print("❌ PROBLEMA: No hay pacientes en la BD")
                print("   Solución: Crear pacientes desde el frontend")
                print()
            
            if total_consultas == 0:
                print("❌ PROBLEMA: No hay consultas en la BD")
                print("   Solución: Crear consultas desde el frontend")
                print()
            
            if total_cps == 0:
                print("❌ PROBLEMA: No hay códigos postales en la BD")
                print("   Solución: Ejecutar python agregar_codigos_postales.py")
                print()
            elif len(cps_83288) < 10:
                print("⚠️  ADVERTENCIA: CP 83288 tiene pocas colonias")
                print("   Solución: Ejecutar actualizar_colonias.bat")
                print()
            
            if total_pacientes > 0 and total_consultas > 0 and total_cps > 0:
                print("✅ SISTEMA OK - Todos los datos están presentes")
                print()
            
            print("="*70)
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(verificar_sistema())
    except KeyboardInterrupt:
        print("\n⚠️  Verificación cancelada")
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
