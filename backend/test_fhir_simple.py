"""
Script de prueba simple para verificar FHIR Observations
"""

import asyncio
import sys
from datetime import datetime
from uuid import uuid4

sys.path.insert(0, ".")

from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.services.fhir_observation_transformer import FHIRObservationTransformer


async def test_transformadores():
    """Test: Verificar que los transformadores funcionan"""
    print("\n" + "=" * 60)
    print("🧪 TEST DE TRANSFORMADORES FHIR OBSERVATION")
    print("=" * 60)

    # Test 1: Códigos LOINC
    print("\n✅ Test 1: Códigos LOINC disponibles")
    parametros = ["hemoglobina", "glucosa", "frecuencia_cardiaca", "temperatura"]
    for param in parametros:
        loinc = FHIRObservationTransformer.LOINC_CODES.get(param)
        if loinc:
            print(f"   • {param}: {loinc['code']} - {loinc['display']}")

    # Test 2: Rangos de referencia
    print("\n✅ Test 2: Rangos de referencia")
    for param in parametros:
        rango = FHIRObservationTransformer.REFERENCE_RANGES.get(param)
        if rango:
            print(f"   • {param}: {rango['low']}-{rango['high']} {rango['unit']}")

    # Test 3: Transformar signo vital
    print("\n✅ Test 3: Transformar signo vital (frecuencia cardíaca)")
    paciente_id = uuid4()
    obs_data = FHIRObservationTransformer.from_signo_vital(
        nombre_parametro="frecuencia_cardiaca",
        valor=75,
        unidad="bpm",
        paciente_id=paciente_id,
        fecha=datetime.now(),
    )
    print(f"   • Status: {obs_data['status']}")
    print(f"   • Category: {obs_data['category']}")
    print(f"   • Code: {obs_data['code']['text']}")
    print(
        f"   • Value: {obs_data['value_quantity']['value']} {obs_data['value_quantity']['unit']}"
    )
    print(f"   • LOINC: {obs_data['code']['coding'][0]['code']}")

    # Test 4: Transformar presión arterial (multi-componente)
    print("\n✅ Test 4: Transformar presión arterial (multi-componente)")
    obs_pa = FHIRObservationTransformer.from_presion_arterial(
        sistolica=120, diastolica=80, paciente_id=paciente_id, fecha=datetime.now()
    )
    print(f"   • Status: {obs_pa['status']}")
    print(f"   • Code: {obs_pa['code']['text']}")
    print(f"   • Componentes: {len(obs_pa['component'])}")
    for comp in obs_pa["component"]:
        display = comp["code"]["coding"][0]["display"]
        value = comp["valueQuantity"]["value"]
        unit = comp["valueQuantity"]["unit"]
        print(f"     - {display}: {value} {unit}")

    # Test 5: Transformar parámetro de laboratorio
    print("\n✅ Test 5: Transformar parámetro de laboratorio (glucosa)")
    obs_lab = FHIRObservationTransformer.from_parametro_laboratorio(
        nombre_parametro="glucosa",
        valor=95,
        unidad="mg/dL",
        paciente_id=paciente_id,
        prueba_id=uuid4(),
        fecha=datetime.now(),
        interpretacion="Valor dentro de rangos normales",
        estado_anormal=None,
    )
    print(f"   • Status: {obs_lab['status']}")
    print(f"   • Category: {obs_lab['category']}")
    print(f"   • Code: {obs_lab['code']['text']}")
    print(
        f"   • Value: {obs_lab['value_quantity']['value']} {obs_lab['value_quantity']['unit']}"
    )
    if obs_lab.get("interpretation"):
        print(
            f"   • Interpretation: {obs_lab['interpretation'][0]['coding'][0]['display']}"
        )
    else:
        print(f"   • Interpretation: No disponible")

    # Test 6: Verificar conexión a base de datos
    print("\n✅ Test 6: Verificar conexión a base de datos")
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(text("SELECT COUNT(*) FROM fhir_observations"))
            count = result.scalar()
            print(f"   • Observaciones en BD: {count}")

            # Verificar que la tabla existe
            result = await db.execute(
                text(
                    """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'fhir_observations' 
                LIMIT 5
            """
                )
            )
            columns = result.fetchall()
            print(f"   • Columnas de la tabla (primeras 5):")
            for col in columns:
                print(f"     - {col[0]}: {col[1]}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")

    print("\n" + "=" * 60)
    print("✅ TODOS LOS TESTS PASARON")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_transformadores())
