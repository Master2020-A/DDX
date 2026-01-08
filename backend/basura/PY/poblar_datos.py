import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent))


async def poblar_datos():
    print("=" * 70)
    print("📊 POBLANDO DATOS DE PRUEBA")
    print("=" * 70)

    from sqlalchemy import select, delete
    from app.core.database import AsyncSessionLocal
    from app.models.usuario import Usuario
    from app.models.paciente import Paciente
    from app.models.integraciones import (
        ConfiguracionIntegracion,
        RecetaElectronica,
        SolicitudFarmacia,
        FacturaElectronica,
    )

    async with AsyncSessionLocal() as db:
        try:
            # Obtener usuarios y pacientes
            result = await db.execute(select(Usuario).limit(3))
            usuarios = list(result.scalars().all())

            result = await db.execute(select(Paciente).limit(5))
            pacientes = list(result.scalars().all())

            print(
                f"\n Encontrados {len(usuarios)} usuarios y {len(pacientes)} pacientes"
            )

            if not usuarios or not pacientes:
                print("  Se requieren usuarios y pacientes en la BD")
                return

            # Verificar si ya existen configuraciones
            result = await db.execute(select(ConfiguracionIntegracion))
            configs_existentes = result.scalars().all()

            if configs_existentes:
                print(f"\n  Ya existen {len(configs_existentes)} configuraciones")
                print("   Eliminando datos existentes...")

                # Eliminar datos existentes en orden correcto (por dependencias)
                await db.execute(delete(FacturaElectronica))
                await db.execute(delete(SolicitudFarmacia))
                await db.execute(delete(RecetaElectronica))
                await db.execute(delete(ConfiguracionIntegracion))
                await db.commit()
                print("   Datos existentes eliminados")

            # Configuraciones
            print("\n Creando configuraciones...")
            configs = [
                ConfiguracionIntegracion(
                    nombre="PACS Principal",
                    tipo_sistema="PACS",
                    descripcion="Servidor PACS para imágenes DICOM",
                    url_base="192.168.1.100",
                    puerto=11112,
                    protocolo="DICOM",
                    activo=True,
                ),
                ConfiguracionIntegracion(
                    nombre="LIS Laboratorio",
                    tipo_sistema="LIS",
                    descripcion="Sistema de información de laboratorio",
                    url_base="http://lis.hospital.local",
                    puerto=8080,
                    protocolo="HL7",
                    activo=True,
                ),
                ConfiguracionIntegracion(
                    nombre="PAC Timbrado",
                    tipo_sistema="CFDI",
                    descripcion="Proveedor de timbrado CFDI 4.0",
                    url_base="https://api.finkok.com",
                    puerto=443,
                    protocolo="HTTPS",
                    activo=True,
                ),
            ]

            for config in configs:
                db.add(config)
            await db.flush()
            print(f"✅ {len(configs)} configuraciones creadas")

            # Recetas
            print("\n💊 Creando recetas...")
            recetas = [
                RecetaElectronica(
                    folio=f"RX-{datetime.now().strftime('%Y%m%d')}-100000",
                    codigo_verificacion="ABC00000",
                    paciente_id=pacientes[0].id,
                    medico_id=usuarios[0].id,
                    diagnostico_cie10="I10",
                    medicamentos=[
                        {
                            "nombre_generico": "Losartán",
                            "presentacion": "50mg tabletas",
                            "dosis": "50mg",
                            "frecuencia": "cada 24 horas",
                            "via": "oral",
                            "duracion_dias": 30,
                            "cantidad": 30,
                        }
                    ],
                    fecha_emision=datetime.now() - timedelta(days=2),
                    fecha_vencimiento=datetime.now() + timedelta(days=28),
                    estado="ACTIVA",
                ),
                RecetaElectronica(
                    folio=f"RX-{datetime.now().strftime('%Y%m%d')}-100001",
                    codigo_verificacion="ABC00001",
                    paciente_id=pacientes[1].id,
                    medico_id=usuarios[0].id,
                    medicamentos=[
                        {
                            "nombre_generico": "Amoxicilina",
                            "presentacion": "500mg cápsulas",
                            "dosis": "500mg",
                            "frecuencia": "cada 8 horas",
                            "via": "oral",
                            "duracion_dias": 7,
                            "cantidad": 21,
                        }
                    ],
                    fecha_emision=datetime.now() - timedelta(days=10),
                    fecha_vencimiento=datetime.now() + timedelta(days=20),
                    estado="SURTIDA",
                    fecha_surtido=datetime.now() - timedelta(days=9),
                ),
            ]

            for receta in recetas:
                db.add(receta)
            await db.flush()
            print(f"✅ {len(recetas)} recetas creadas")

            # Solicitudes farmacia
            print("\n🏥 Creando solicitudes...")
            solicitudes = [
                SolicitudFarmacia(
                    folio=f"SF-{datetime.now().strftime('%Y%m%d')}-200000",
                    paciente_id=pacientes[0].id,
                    medico_id=usuarios[0].id,
                    medicamentos_solicitados=[
                        {
                            "codigo": "MED-001",
                            "nombre": "Losartán 50mg",
                            "cantidad": 30,
                            "urgente": False,
                        }
                    ],
                    urgente=False,
                    destino="AMBULATORIO",
                    fecha_solicitud=datetime.now() - timedelta(days=2),
                    estado="DISPENSADO",
                    fecha_dispensacion=datetime.now() - timedelta(days=2),
                    farmaceutico_id=usuarios[0].id,
                    costo_total=75.00,
                    verificado=True,
                )
            ]

            for sol in solicitudes:
                db.add(sol)
            await db.flush()
            print(f"✅ {len(solicitudes)} solicitudes creadas")

            # Facturas
            print("\n💰 Creando facturas...")
            facturas = [
                FacturaElectronica(
                    serie="A",
                    folio=f"F-{datetime.now().strftime('%Y%m%d')}-300000",
                    paciente_id=pacientes[0].id,
                    tipo_comprobante="I",
                    uso_cfdi="G03",
                    metodo_pago="PUE",
                    forma_pago="01",
                    receptor_rfc="XAXX010101000",
                    receptor_nombre="Público General",
                    receptor_cp="01000",
                    receptor_regimen="605",
                    conceptos=[
                        {
                            "clave_prod_serv": "85121800",
                            "cantidad": 1,
                            "unidad": "E48",
                            "descripcion": "Consulta médica general",
                            "valor_unitario": 500.00,
                            "importe": 500.00,
                        }
                    ],
                    subtotal=500.00,
                    total=580.00,
                    fecha_emision=datetime.now() - timedelta(days=3),
                    estado="TIMBRADA",
                    uuid_sat=str(uuid4()),
                    fecha_timbrado=datetime.now() - timedelta(days=3),
                    pac_proveedor="FINKOK",
                )
            ]

            for factura in facturas:
                db.add(factura)
            await db.flush()
            print(f"✅ {len(facturas)} facturas creadas")

            await db.commit()

            print("\n" + "=" * 70)
            print("✅ ¡DATOS CREADOS EXITOSAMENTE!")
            print("=" * 70)
            print(
                f"\n📊 Total: {len(configs)} configs, {len(recetas)} recetas, {len(solicitudes)} solicitudes, {len(facturas)} facturas"
            )

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(poblar_datos())
