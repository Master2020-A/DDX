"""
Script de prueba para servicios de IA
"""

import asyncio
import sys
from uuid import UUID


async def test_services():
    print("=" * 60)
    print("PRUEBA DE SERVICIOS DE IA")
    print("=" * 60)
    print()

    # Test 1: Import de servicios
    print("1. IMPORTANDO SERVICIOS...")
    try:
        from app.services.prediccion_riesgo_service import PrediccionRiesgoService

        print("   ✅ PrediccionRiesgoService")
    except Exception as e:
        print(f"   ❌ PrediccionRiesgoService: {e}")
        return

    try:
        from app.services.asistente_ia_service import AsistenteIAService

        print("   ✅ AsistenteIAService")
    except Exception as e:
        print(f"   ❌ AsistenteIAService: {e}")

    try:
        from app.services.recomendacion_tratamiento_service import (
            RecomendacionTratamientoService,
        )

        print("   ✅ RecomendacionTratamientoService")
    except Exception as e:
        print(f"   ❌ RecomendacionTratamientoService: {e}")

    try:
        from app.services.interacciones_medicamentosas_service import (
            InteraccionesMedicamentosasService,
        )

        print("   ✅ InteraccionesMedicamentosasService")
    except Exception as e:
        print(f"   ❌ InteraccionesMedicamentosasService: {e}")

    try:
        from app.services.deteccion_anomalias_service import DeteccionAnomaliasService

        print("   ✅ DeteccionAnomaliasService")
    except Exception as e:
        print(f"   ❌ DeteccionAnomaliasService: {e}")

    print()
    print("2. VERIFICANDO OPENAI CLIENT...")
    try:
        from app.services.openai_client import chat_completion

        print("   ✅ openai_client importado correctamente")
    except Exception as e:
        print(f"   ❌ openai_client: {e}")
        return

    print()
    print("3. VERIFICANDO MODELOS...")
    try:
        from app.models.paciente import Paciente
        from app.models.expediente import ExpedienteClinico
        from app.models.consulta import Consulta
        from app.models.laboratorio import PruebaLaboratorio

        print("   ✅ Todos los modelos importados correctamente")
    except Exception as e:
        print(f"   ❌ Error en modelos: {e}")
        return

    print()
    print("4. VERIFICANDO CONFIGURACIÓN...")
    try:
        from app.core.config import settings

        if settings.OPENAI_API_KEY:
            print(f"   ✅ OPENAI_API_KEY configurada")
        else:
            print(f"   ❌ OPENAI_API_KEY no configurada")
    except Exception as e:
        print(f"   ❌ Error en configuración: {e}")

    print()
    print("5. INSTANCIANDO SERVICIOS...")
    try:
        service = PrediccionRiesgoService()
        print("   ✅ PrediccionRiesgoService instanciado")
    except Exception as e:
        print(f"   ❌ Error al instanciar PrediccionRiesgoService: {e}")
        import traceback

        traceback.print_exc()

    print()
    print("=" * 60)
    print("PRUEBA COMPLETADA")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_services())
