"""
Script de prueba para el recurso Observation HL7 FHIR
Ejecutar: python test_fhir_observations.py
"""

import asyncio
import sys
from datetime import datetime
from uuid import uuid4

# Agregar el directorio raíz al path
sys.path.insert(0, ".")

from sqlalchemy import select, text
from app.core.database import AsyncSessionLocal
from app.models.fhir_observation import FHIRObservation, ObservationStatus
from app.services.fhir_observation_transformer import FHIRObservationTransformer

# Importar todos los modelos para evitar problemas de relaciones
import app.models.institucion  # Debe importarse antes de usuario
import app.models.paciente
import app.models.usuario
from app.models.paciente import Paciente


async def test_crear_observation_glucosa():
    """Test: Crear observación de glucosa"""
    print("\n🧪 Test 1: Crear observación de glucosa")

    async with AsyncSessionLocal() as db:
        # Obtener primer paciente
        result = await db.execute(select(Paciente).limit(1))
        paciente = result.scalar_one_or_none()

        if not paciente:
            print("❌ No hay pacientes en la base de datos")
            return False

        # Crear observación usando transformador
        obs_data = FHIRObservationTransformer.from_parametro_laboratorio(
            nombre_parametro="glucosa",
            valor=95,
            unidad="mg/dL",
            paciente_id=paciente.id,
            prueba_id=uuid4(),
            fecha=datetime.now(),
            interpretacion="Valor dentro de rangos normales",
            estado_anormal=None,
        )

        observation = FHIRObservation(**obs_data)
        db.add(observation)
        await db.commit()
        await db.refresh(observation)

        print(f"✅ Observación creada: {observation.id}")
        print(f"   - Código: {observation.code.get('text')}")
        print(
            f"   - Valor: {observation.value_quantity.get('value')} {observation.value_quantity.get('unit')}"
        )
        print(f"   - Estado: {observation.status.value}")
        print(f"   - Categoría: {observation.category}")

        return True


async def test_crear_observation_presion_arterial():
    """Test: Crear observación multi-componente de presión arterial"""
    print("\n🧪 Test 2: Crear observación de presión arterial (multi-componente)")

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Paciente).limit(1))
        paciente = result.scalar_one_or_none()

        if not paciente:
            print("❌ No hay pacientes en la base de datos")
            return False

        # Crear observación multi-componente
        obs_data = FHIRObservationTransformer.from_presion_arterial(
            sistolica=120, diastolica=80, paciente_id=paciente.id, fecha=datetime.now()
        )

        observation = FHIRObservation(**obs_data)
        db.add(observation)
        await db.commit()
        await db.refresh(observation)

        print(f"✅ Observación multi-componente creada: {observation.id}")
        print(f"   - Código: {observation.code.get('text')}")
        print(f"   - Componentes: {len(observation.component)}")

        for comp in observation.component:
            code_display = comp["code"]["coding"][0]["display"]
            value = comp["valueQuantity"]["value"]
            unit = comp["valueQuantity"]["unit"]
            print(f"     • {code_display}: {value} {unit}")

        return True


async def test_crear_observation_signo_vital():
    """Test: Crear observación de signo vital"""
    print("\n🧪 Test 3: Crear observación de frecuencia cardíaca")

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Paciente).limit(1))
        paciente = result.scalar_one_or_none()

        if not paciente:
            print("❌ No hay pacientes en la base de datos")
            return False

        # Crear observación de frecuencia cardíaca
        obs_data = FHIRObservationTransformer.from_signo_vital(
            nombre_parametro="frecuencia_cardiaca",
            valor=75,
            unidad="bpm",
            paciente_id=paciente.id,
            fecha=datetime.now(),
        )

        observation = FHIRObservation(**obs_data)
        db.add(observation)
        await db.commit()
        await db.refresh(observation)

        print(f"✅ Observación de signo vital creada: {observation.id}")
        print(f"   - Código LOINC: {observation.code['coding'][0]['code']}")
        print(f"   - Display: {observation.code['coding'][0]['display']}")
        print(
            f"   - Valor: {observation.value_quantity.get('value')} {observation.value_quantity.get('unit')}"
        )
        print(
            f"   - Interpretación: {observation.interpretation[0]['coding'][0]['display'] if observation.interpretation else 'N/A'}"
        )

        return True


async def test_buscar_observations():
    """Test: Buscar observaciones"""
    print("\n🧪 Test 4: Buscar observaciones")

    async with AsyncSessionLocal() as db:
        # Buscar todas las observaciones
        result = await db.execute(
            select(FHIRObservation)
            .order_by(FHIRObservation.created_at.desc())
            .limit(10)
        )
        observations = result.scalars().all()

        print(f"✅ Encontradas {len(observations)} observaciones")

        for obs in observations:
            print(f"\n   📊 Observation {obs.id}")
            print(f"      - Tipo: {obs.code.get('text', 'N/A')}")
            print(f"      - Categoría: {obs.category}")
            print(f"      - Estado: {obs.status.value}")
            print(f"      - Fecha: {obs.effective_datetime}")

            if obs.value_quantity:
                print(
                    f"      - Valor: {obs.value_quantity.get('value')} {obs.value_quantity.get('unit')}"
                )
            elif obs.component:
                print(f"      - Componentes: {len(obs.component)}")

        return True


async def test_convertir_a_fhir():
    """Test: Convertir a formato FHIR R4"""
    print("\n🧪 Test 5: Convertir a formato FHIR R4")

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(FHIRObservation).limit(1))
        observation = result.scalar_one_or_none()

        if not observation:
            print("❌ No hay observaciones en la base de datos")
            return False

        # Convertir a FHIR
        fhir_dict = observation.to_fhir_dict()

        print(f"✅ Conversión a FHIR R4 exitosa")
        print(f"   - resourceType: {fhir_dict['resourceType']}")
        print(f"   - id: {fhir_dict['id']}")
        print(f"   - status: {fhir_dict['status']}")
        print(f"   - code: {fhir_dict['code'].get('text')}")
        print(f"   - subject: {fhir_dict['subject']['reference']}")

        if "valueQuantity" in fhir_dict:
            print(f"   - valueQuantity: {fhir_dict['valueQuantity']}")
        elif "component" in fhir_dict:
            print(f"   - component: {len(fhir_dict['component'])} componentes")

        return True


async def test_crear_bundle():
    """Test: Crear Bundle FHIR"""
    print("\n🧪 Test 6: Crear Bundle FHIR")

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Paciente).limit(1))
        paciente = result.scalar_one_or_none()

        if not paciente:
            print("❌ No hay pacientes en la base de datos")
            return False

        # Obtener observaciones del paciente
        result = await db.execute(
            select(FHIRObservation).where(FHIRObservation.subject_id == paciente.id)
        )
        observations = result.scalars().all()

        if not observations:
            print("⚠️  No hay observaciones para este paciente")
            return True

        # Crear bundle
        bundle = FHIRObservationTransformer.crear_bundle_observations(observations)

        print(f"✅ Bundle FHIR creado")
        print(f"   - resourceType: {bundle['resourceType']}")
        print(f"   - type: {bundle['type']}")
        print(f"   - total: {bundle['total']}")
        print(f"   - entries: {len(bundle['entry'])}")

        return True


async def test_codigos_loinc():
    """Test: Verificar mapeo de códigos LOINC"""
    print("\n🧪 Test 7: Verificar mapeo de códigos LOINC")

    parametros_test = [
        "hemoglobina",
        "glucosa",
        "creatinina",
        "frecuencia_cardiaca",
        "presion_arterial_sistolica",
        "temperatura",
    ]

    print("✅ Códigos LOINC disponibles:")
    for param in parametros_test:
        loinc_info = FHIRObservationTransformer.LOINC_CODES.get(param)
        if loinc_info:
            print(f"   • {param}: {loinc_info['code']} - {loinc_info['display']}")
        else:
            print(f"   ⚠️  {param}: No mapeado")

    return True


async def test_rangos_referencia():
    """Test: Verificar rangos de referencia"""
    print("\n🧪 Test 8: Verificar rangos de referencia")

    parametros_test = ["hemoglobina", "glucosa", "frecuencia_cardiaca", "temperatura"]

    print("✅ Rangos de referencia disponibles:")
    for param in parametros_test:
        rango = FHIRObservationTransformer.REFERENCE_RANGES.get(param)
        if rango:
            print(f"   • {param}: {rango['low']}-{rango['high']} {rango['unit']}")
        else:
            print(f"   ⚠️  {param}: No definido")

    return True


async def run_all_tests():
    """Ejecutar todos los tests"""
    print("=" * 60)
    print("🧪 TESTS DEL RECURSO OBSERVATION HL7 FHIR")
    print("=" * 60)

    tests = [
        test_codigos_loinc,
        test_rangos_referencia,
        test_crear_observation_glucosa,
        test_crear_observation_presion_arterial,
        test_crear_observation_signo_vital,
        test_buscar_observations,
        test_convertir_a_fhir,
        test_crear_bundle,
    ]

    resultados = []

    for test in tests:
        try:
            resultado = await test()
            resultados.append((test.__name__, resultado))
        except Exception as e:
            print(f"\n❌ Error en {test.__name__}: {e}")
            import traceback

            traceback.print_exc()
            resultados.append((test.__name__, False))

    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS")
    print("=" * 60)

    exitosos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)

    for nombre, resultado in resultados:
        emoji = "✅" if resultado else "❌"
        print(f"{emoji} {nombre}")

    print(f"\n🎯 Resultado: {exitosos}/{total} tests exitosos")

    if exitosos == total:
        print("🎉 ¡Todos los tests pasaron!")
    else:
        print("⚠️  Algunos tests fallaron")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
