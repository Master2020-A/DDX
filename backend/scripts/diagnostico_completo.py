"""Script de diagnóstico completo"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, select, func
from app.core.database import AsyncSessionLocal
from app.models.hospitalizacion import Cama, Hospitalizacion
from app.models.interconsulta import Interconsulta
from app.models.paciente import Paciente
from app.models.usuario import Usuario

async def main():
    print("\n" + "="*60)
    print("🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA")
    print("="*60 + "\n")
    
    async with AsyncSessionLocal() as db:
        try:
            # 1. Verificar tablas
            print("1️⃣ Verificando tablas...")
            result = await db.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('camas', 'hospitalizaciones', 'interconsultas', 'pacientes', 'usuarios')
                ORDER BY table_name
            """))
            tablas = result.fetchall()
            print(f"   Tablas encontradas: {[t[0] for t in tablas]}")
            
            # 2. Contar registros
            print("\n2️⃣ Contando registros...")
            
            result = await db.execute(select(func.count(Usuario.id)))
            usuarios = result.scalar()
            print(f"   👤 Usuarios: {usuarios}")
            
            result = await db.execute(select(func.count(Paciente.id)))
            pacientes = result.scalar()
            print(f"   🏥 Pacientes: {pacientes}")
            
            result = await db.execute(select(func.count(Cama.id)))
            camas = result.scalar()
            print(f"   🛏️  Camas: {camas}")
            
            result = await db.execute(select(func.count(Hospitalizacion.id)))
            hosp = result.scalar()
            print(f"   🏨 Hospitalizaciones: {hosp}")
            
            result = await db.execute(select(func.count(Interconsulta.id)))
            inter = result.scalar()
            print(f"   🔄 Interconsultas: {inter}")
            
            # 3. Verificar columnas de hospitalizaciones
            print("\n3️⃣ Verificando columnas de hospitalizaciones...")
            result = await db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'hospitalizaciones'
                ORDER BY ordinal_position
            """))
            columnas = [r[0] for r in result.fetchall()]
            print(f"   Columnas: {', '.join(columnas)}")
            
            if 'resumen_clinico' in columnas:
                print("   ✅ Columna 'resumen_clinico' existe")
            else:
                print("   ❌ Columna 'resumen_clinico' NO existe")
            
            # 4. Verificar índices
            print("\n4️⃣ Verificando índices...")
            result = await db.execute(text("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename IN ('camas', 'hospitalizaciones', 'interconsultas')
                ORDER BY tablename, indexname
            """))
            indices = result.fetchall()
            print(f"   Índices encontrados: {len(indices)}")
            
            # 5. Probar queries básicas
            print("\n5️⃣ Probando queries básicas...")
            
            # Listar camas
            try:
                result = await db.execute(select(Cama).limit(5))
                camas_list = result.scalars().all()
                print(f"   ✅ Query de camas OK ({len(camas_list)} registros)")
            except Exception as e:
                print(f"   ❌ Error en query de camas: {e}")
            
            # Listar hospitalizaciones
            try:
                result = await db.execute(select(Hospitalizacion).limit(5))
                hosp_list = result.scalars().all()
                print(f"   ✅ Query de hospitalizaciones OK ({len(hosp_list)} registros)")
            except Exception as e:
                print(f"   ❌ Error en query de hospitalizaciones: {e}")
            
            # Listar interconsultas
            try:
                result = await db.execute(select(Interconsulta).limit(5))
                inter_list = result.scalars().all()
                print(f"   ✅ Query de interconsultas OK ({len(inter_list)} registros)")
            except Exception as e:
                print(f"   ❌ Error en query de interconsultas: {e}")
            
            print("\n" + "="*60)
            print("✅ DIAGNÓSTICO COMPLETADO")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error general: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
