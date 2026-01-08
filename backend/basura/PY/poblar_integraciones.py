"""
Script para poblar datos de prueba del módulo de Integraciones
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent))


async def main():
    print("=" * 70)
    print(" POBLANDO DATOS DE PRUEBA - MÓDULO DE INTEGRACIONES")
    print("=" * 70)

    from sqlalchemy import select
    from app.core.database import AsyncSessionLocal

    # Importar TODOS los modelos para evitar errores de relaciones
    import app.models.telemedicina  # Debe importarse ANTES de Usuario
    import app.models.ia_medica  # Debe importarse ANTES de Paciente
    import app.models.paciente
    import app.models.usuario
    import app.models.integraciones

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
                f"\n✅ Encontrados {len(usuarios)} usuarios y {len(pacientes)} pacientes"
            )

            if not usuarios or not pacientes:
                print("⚠️  Se requieren usuarios y pacientes en la BD")
                return

            # 1. Configuraciones de Integración
            print("\n⚙️ Verificando configuraciones de integración...")

            # Verificar si ya existen configuraciones
            result = await db.execute(select(ConfiguracionIntegracion))
            configs_existentes = result.scalars().all()

            if configs_existentes:
                print(
                    f"⚠️  Ya existen {len(configs_existentes)} configuraciones. Eliminando..."
                )
                for config in configs_existentes:
                    await db.delete(config)
                await db.flush()

            print("⚙️ Creando configuraciones de integración...")
            configs = [
                {
                    "nombre": "PACS Principal",
                    "tipo_sistema": "PACS",
                    "descripcion": "Servidor PACS para imágenes DICOM",
                    "url_base": "192.168.1.100",
                    "puerto": 11112,
                    "protocolo": "DICOM",
                    "activo": True,
                },
                {
                    "nombre": "LIS Laboratorio",
                    "tipo_sistema": "LIS",
                    "descripcion": "Sistema de información de laboratorio",
                    "url_base": "http://lis.hospital.local",
                    "puerto": 8080,
                    "protocolo": "HL7",
                    "activo": True,
                },
                {
                    "nombre": "PAC Timbrado",
                    "tipo_sistema": "CFDI",
                    "descripcion": "Proveedor de timbrado CFDI 4.0",
                    "url_base": "https://api.finkok.com",
                    "puerto": 443,
                    "protocolo": "HTTPS",
                    "activo": True,
                },
            ]

            for config_data in configs:
                config = ConfiguracionIntegracion(**config_data)
                db.add(config)

            await db.flush()
            print(f"✅ {len(configs)} configuraciones creadas")

            # 2. Recetas Electrónicas
            print("\n💊 Verificando recetas electrónicas...")

            # Verificar si ya existen recetas
            result = await db.execute(select(RecetaElectronica))
            recetas_existentes = result.scalars().all()

            if recetas_existentes:
                print(f"⚠️  Ya existen {len(recetas_existentes)} recetas. Eliminando...")
                for receta in recetas_existentes:
                    await db.delete(receta)
                await db.flush()

            print("💊 Creando recetas electrónicas...")
            recetas_data = [
                {
                    "medicamentos": [
                        {
                            "nombre_generico": "Losartán",
                            "nombre_comercial": "Cozaar",
                            "presentacion": "50mg tabletas",
                            "dosis": "50mg",
                            "frecuencia": "cada 24 horas",
                            "via": "oral",
                            "duracion_dias": 30,
                            "cantidad": 30,
                            "indicaciones": "Tomar 1 tableta cada mañana con alimentos",
                        },
                        {
                            "nombre_generico": "Metformina",
                            "nombre_comercial": "Glucophage",
                            "presentacion": "850mg tabletas",
                            "dosis": "850mg",
                            "frecuencia": "cada 12 horas",
                            "via": "oral",
                            "duracion_dias": 30,
                            "cantidad": 60,
                            "indicaciones": "Tomar 1 tableta cada 12 horas con alimentos",
                        },
                    ],
                    "estado": "ACTIVA",
                    "dias_atras": 2,
                },
                {
                    "medicamentos": [
                        {
                            "nombre_generico": "Amoxicilina",
                            "presentacion": "500mg cápsulas",
                            "dosis": "500mg",
                            "frecuencia": "cada 8 horas",
                            "via": "oral",
                            "duracion_dias": 7,
                            "cantidad": 21,
                            "indicaciones": "Tomar 1 cápsula cada 8 horas",
                        }
                    ],
                    "estado": "SURTIDA",
                    "dias_atras": 10,
                },
                {
                    "medicamentos": [
                        {
                            "nombre_generico": "Omeprazol",
                            "presentacion": "20mg cápsulas",
                            "dosis": "20mg",
                            "frecuencia": "cada 24 horas",
                            "via": "oral",
                            "duracion_dias": 30,
                            "cantidad": 30,
                            "indicaciones": "Tomar 1 cápsula en ayunas",
                        }
                    ],
                    "estado": "ACTIVA",
                    "dias_atras": 5,
                },
            ]

            for idx, receta_data in enumerate(recetas_data):
                receta = RecetaElectronica(
                    folio=f"RX-{datetime.now().strftime('%Y%m%d')}-{100000 + idx:06d}",
                    codigo_verificacion=f"ABC{idx:05d}",
                    paciente_id=pacientes[idx % len(pacientes)].id,
                    medico_id=usuarios[0].id,
                    diagnostico_cie10="I10" if idx == 0 else "J06.9",
                    medicamentos=receta_data["medicamentos"],
                    fecha_emision=datetime.now()
                    - timedelta(days=receta_data["dias_atras"]),
                    fecha_vencimiento=datetime.now()
                    + timedelta(days=30 - receta_data["dias_atras"]),
                    estado=receta_data["estado"],
                    fecha_surtido=(
                        datetime.now() - timedelta(days=receta_data["dias_atras"] - 1)
                        if receta_data["estado"] == "SURTIDA"
                        else None
                    ),
                )
                db.add(receta)

            await db.flush()
            print(f"✅ {len(recetas_data)} recetas electrónicas creadas")

            # 3. Solicitudes de Farmacia
            print("\n🏥 Verificando solicitudes de farmacia...")

            # Verificar si ya existen solicitudes
            result = await db.execute(select(SolicitudFarmacia))
            solicitudes_existentes = result.scalars().all()

            if solicitudes_existentes:
                print(
                    f"⚠️  Ya existen {len(solicitudes_existentes)} solicitudes. Eliminando..."
                )
                for solicitud in solicitudes_existentes:
                    await db.delete(solicitud)
                await db.flush()

            print("🏥 Creando solicitudes de farmacia...")
            solicitudes_data = [
                {
                    "medicamentos": [
                        {
                            "codigo": "MED-001",
                            "nombre": "Losartán 50mg",
                            "cantidad": 30,
                            "urgente": False,
                        }
                    ],
                    "destino": "AMBULATORIO",
                    "estado": "DISPENSADO",
                    "dias_atras": 2,
                },
                {
                    "medicamentos": [
                        {
                            "codigo": "MED-002",
                            "nombre": "Morfina 10mg",
                            "cantidad": 10,
                            "urgente": True,
                        }
                    ],
                    "destino": "HOSPITALIZACION",
                    "estado": "DISPENSADO",
                    "dias_atras": 1,
                },
                {
                    "medicamentos": [
                        {
                            "codigo": "MED-003",
                            "nombre": "Paracetamol 500mg",
                            "cantidad": 20,
                            "urgente": False,
                        }
                    ],
                    "destino": "URGENCIAS",
                    "estado": "PENDIENTE",
                    "dias_atras": 0,
                },
            ]

            for idx, sol_data in enumerate(solicitudes_data):
                solicitud = SolicitudFarmacia(
                    folio=f"SF-{datetime.now().strftime('%Y%m%d')}-{200000 + idx:06d}",
                    paciente_id=pacientes[idx % len(pacientes)].id,
                    medico_id=usuarios[0].id,
                    medicamentos_solicitados=sol_data["medicamentos"],
                    urgente=sol_data["medicamentos"][0]["urgente"],
                    destino=sol_data["destino"],
                    ubicacion=(
                        "Cama 201-A"
                        if sol_data["destino"] == "HOSPITALIZACION"
                        else None
                    ),
                    fecha_solicitud=datetime.now()
                    - timedelta(days=sol_data["dias_atras"]),
                    estado=sol_data["estado"],
                    fecha_dispensacion=(
                        datetime.now() - timedelta(days=sol_data["dias_atras"])
                        if sol_data["estado"] == "DISPENSADO"
                        else None
                    ),
                    farmaceutico_id=(
                        usuarios[1].id
                        if len(usuarios) > 1 and sol_data["estado"] == "DISPENSADO"
                        else None
                    ),
                    costo_total=75.00 if sol_data["estado"] == "DISPENSADO" else None,
                    verificado=sol_data["estado"] == "DISPENSADO",
                )
                db.add(solicitud)

            await db.flush()
            print(f"✅ {len(solicitudes_data)} solicitudes de farmacia creadas")

            # 4. Facturas Electrónicas
            print("\n💰 Verificando facturas electrónicas...")

            # Verificar si ya existen facturas
            result = await db.execute(select(FacturaElectronica))
            facturas_existentes = result.scalars().all()

            if facturas_existentes:
                print(
                    f"⚠️  Ya existen {len(facturas_existentes)} facturas. Eliminando..."
                )
                for factura in facturas_existentes:
                    await db.delete(factura)
                await db.flush()

            print("💰 Creando facturas electrónicas...")
            facturas_data = [
                {
                    "conceptos": [
                        {
                            "clave_prod_serv": "85121800",
                            "cantidad": 1,
                            "unidad": "E48",
                            "descripcion": "Consulta médica general",
                            "valor_unitario": 500.00,
                            "importe": 500.00,
                        }
                    ],
                    "subtotal": 500.00,
                    "total": 580.00,
                    "estado": "TIMBRADA",
                    "dias_atras": 3,
                },
                {
                    "conceptos": [
                        {
                            "clave_prod_serv": "85121801",
                            "cantidad": 1,
                            "unidad": "E48",
                            "descripcion": "Consulta de especialidad",
                            "valor_unitario": 800.00,
                            "importe": 800.00,
                        }
                    ],
                    "subtotal": 800.00,
                    "total": 928.00,
                    "estado": "TIMBRADA",
                    "dias_atras": 7,
                },
                {
                    "conceptos": [
                        {
                            "clave_prod_serv": "85121802",
                            "cantidad": 1,
                            "unidad": "E48",
                            "descripcion": "Estudios de laboratorio",
                            "valor_unitario": 350.00,
                            "importe": 350.00,
                        }
                    ],
                    "subtotal": 350.00,
                    "total": 406.00,
                    "estado": "PENDIENTE",
                    "dias_atras": 0,
                },
            ]

            for idx, fact_data in enumerate(facturas_data):
                factura = FacturaElectronica(
                    serie="A",
                    folio=f"F-{datetime.now().strftime('%Y%m%d')}-{300000 + idx:06d}",
                    paciente_id=pacientes[idx % len(pacientes)].id,
                    tipo_comprobante="I",
                    uso_cfdi="G03",
                    metodo_pago="PUE",
                    forma_pago="01",
                    receptor_rfc="XAXX010101000",
                    receptor_nombre="Público General",
                    receptor_cp="01000",
                    receptor_regimen="605",
                    conceptos=fact_data["conceptos"],
                    subtotal=fact_data["subtotal"],
                    total=fact_data["total"],
                    fecha_emision=datetime.now()
                    - timedelta(days=fact_data["dias_atras"]),
                    estado=fact_data["estado"],
                    uuid_sat=(
                        str(uuid4()) if fact_data["estado"] == "TIMBRADA" else None
                    ),
                    fecha_timbrado=(
                        datetime.now() - timedelta(days=fact_data["dias_atras"])
                        if fact_data["estado"] == "TIMBRADA"
                        else None
                    ),
                    pac_proveedor=(
                        "FINKOK" if fact_data["estado"] == "TIMBRADA" else None
                    ),
                )
                db.add(factura)

            await db.flush()
            print(f"✅ {len(facturas_data)} facturas electrónicas creadas")

            # Commit
            await db.commit()

            print("\n" + "=" * 70)
            print("✅ ¡DATOS CREADOS EXITOSAMENTE!")
            print("=" * 70)
            print("\n📊 Resumen:")
            print(f"   ✓ {len(configs)} configuraciones de integración")
            print(f"   ✓ {len(recetas_data)} recetas electrónicas")
            print(f"   ✓ {len(solicitudes_data)} solicitudes de farmacia")
            print(f"   ✓ {len(facturas_data)} facturas electrónicas")
            print("\n🎉 ¡El módulo de Integraciones está listo!")
            print("   Accede a: http://localhost:5173/integraciones")
            print("=" * 70)

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
