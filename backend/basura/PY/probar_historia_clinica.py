"""
Script para probar la funcionalidad de Historia Clínica Pediátrica
"""
import asyncio
import sys
from datetime import date
from uuid import uuid4
from sqlalchemy import select, text
from app.core.database import AsyncSessionLocal
from app.models.historia_clinica import HistoriaClinicaPediatrica, ExploracionFisica, AntecedentesNoPatologicos
from app.models.paciente import Paciente


async def verificar_tablas():
    """Verificar que las tablas existan"""
    print("\n" + "="*70)
    print("VERIFICANDO TABLAS DE BASE DE DATOS")
    print("="*70)
    
    async with AsyncSessionLocal() as session:
        try:
            # Verificar tabla historias_clinicas
            result = await session.execute(text(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='historias_clinicas'"
            ))
            count = result.scalar()
            
            if count > 0:
                print("✅ Tabla 'historias_clinicas' existe")
            else:
                print("❌ Tabla 'historias_clinicas' NO existe")
                return False
            
            # Verificar tabla exploracion_fisica
            result = await session.execute(text(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='exploracion_fisica'"
            ))
            count = result.scalar()
            
            if count > 0:
                print("✅ Tabla 'exploracion_fisica' existe")
            else:
                print("❌ Tabla 'exploracion_fisica' NO existe")
                return False
            
            # Verificar tabla antecedentes_no_patologicos
            result = await session.execute(text(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='antecedentes_no_patologicos'"
            ))
            count = result.scalar()
            
            if count > 0:
                print("✅ Tabla 'antecedentes_no_patologicos' existe")
            else:
                print("❌ Tabla 'antecedentes_no_patologicos' NO existe")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error al verificar tablas: {e}")
            return False


async def crear_historia_prueba():
    """Crear una historia clínica de prueba"""
    print("\n" + "="*70)
    print("CREANDO HISTORIA CLÍNICA DE PRUEBA")
    print("="*70)
    
    async with AsyncSessionLocal() as session:
        try:
            # Buscar un paciente existente
            result = await session.execute(select(Paciente).limit(1))
            paciente = result.scalar_one_or_none()
            
            if not paciente:
                print("❌ No hay pacientes en la base de datos")
                print("   Crea un paciente primero desde la aplicación")
                return False
            
            print(f"\n📋 Usando paciente: {paciente.nombre_completo}")
            print(f"   ID: {paciente.id}")
            
            # Crear historia clínica
            historia = HistoriaClinicaPediatrica(
                paciente_id=paciente.id,
                fecha=date.today(),
                numero_afiliacion="TEST-001",
                informante_parentesco="Madre",
                informante_edad=30,
                padecimiento_actual="Historia clínica de prueba automatizada",
                madre_vive=True,
                madre_edad=30,
                padre_vive=True,
                padre_edad=32,
                peso_nacimiento=3.5,
                talla_nacimiento=50.0,
                gestacion_semanas=39
            )
            
            session.add(historia)
            await session.commit()
            await session.refresh(historia)
            
            print(f"✅ Historia clínica creada con ID: {historia.id}")
            
            # Crear exploración física
            exploracion = ExploracionFisica(
                historia_clinica_id=historia.id,
                peso=15.5,
                talla=95.0,
                frecuencia_cardiaca=90,
                frecuencia_respiratoria=24,
                temperatura=36.8,
                tension_arterial="90/60"
            )
            
            session.add(exploracion)
            await session.commit()
            
            print("✅ Exploración física agregada")
            
            # Crear antecedentes no patológicos
            antecedentes = AntecedentesNoPatologicos(
                historia_clinica_id=historia.id,
                pecho_materno_duracion_meses=6,
                ablactacion_meses=6,
                destete_meses=12,
                desarrollo_sonrio_meses=2,
                desarrollo_sostuvo_cabeza_meses=3,
                desarrollo_se_sento_meses=6,
                desarrollo_camino_meses=12
            )
            
            session.add(antecedentes)
            await session.commit()
            
            print("✅ Antecedentes no patológicos agregados")
            
            # Verificar que se puede leer
            result = await session.execute(
                select(HistoriaClinicaPediatrica).where(
                    HistoriaClinicaPediatrica.id == historia.id
                )
            )
            historia_leida = result.scalar_one_or_none()
            
            if historia_leida:
                print("\n✅ Historia clínica verificada correctamente")
                print(f"   Fecha: {historia_leida.fecha}")
                print(f"   Paciente ID: {historia_leida.paciente_id}")
                return True
            else:
                print("❌ No se pudo leer la historia clínica creada")
                return False
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error al crear historia de prueba: {e}")
            import traceback
            traceback.print_exc()
            return False


async def contar_historias():
    """Contar historias clínicas existentes"""
    print("\n" + "="*70)
    print("ESTADÍSTICAS")
    print("="*70)
    
    async with AsyncSessionLocal() as session:
        try:
            # Contar historias
            result = await session.execute(select(HistoriaClinicaPediatrica))
            historias = result.scalars().all()
            
            print(f"\n📊 Total de historias clínicas: {len(historias)}")
            
            if historias:
                print("\nÚltimas 3 historias:")
                for i, h in enumerate(historias[-3:], 1):
                    print(f"   {i}. ID: {h.id[:8]}... | Fecha: {h.fecha} | Afiliación: {h.numero_afiliacion}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al contar historias: {e}")
            return False


async def main():
    """Función principal"""
    print("\n" + "="*70)
    print("🏥 PRUEBA DEL SISTEMA DE HISTORIA CLÍNICA PEDIÁTRICA")
    print("="*70)
    
    # Paso 1: Verificar tablas
    if not await verificar_tablas():
        print("\n❌ Las tablas no existen. Ejecuta la migración primero:")
        print("   python ejecutar_migracion.py")
        return False
    
    # Paso 2: Crear historia de prueba
    if not await crear_historia_prueba():
        print("\n❌ No se pudo crear la historia de prueba")
        return False
    
    # Paso 3: Mostrar estadísticas
    await contar_historias()
    
    print("\n" + "="*70)
    print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
    print("="*70)
    print("\n💡 Ahora puedes:")
    print("   1. Iniciar el backend: uvicorn app.main:app --reload --port=8612")
    print("   2. Iniciar el frontend: npm run dev")
    print("   3. Acceder a http://localhost:3000")
    print("   4. Ir a Pacientes → Seleccionar → Historia Clínica")
    print("\n" + "="*70 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        resultado = asyncio.run(main())
        sys.exit(0 if resultado else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
