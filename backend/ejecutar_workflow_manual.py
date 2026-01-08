"""
Script para ejecutar workflows manualmente con OpenAI
Ejecutar: python ejecutar_workflow_manual.py
"""

import asyncio
import json
from app.core.database import AsyncSessionLocal
from app.services.workflow_engine import WorkflowEngine


async def ejecutar_workflow():
    """Ejecutar el workflow de triaje inteligente"""

    # Datos de entrada del paciente
    input_data = {
        "nombre": "María García",
        "edad": 35,
        "sintomas": "Fiebre alta, tos seca, dolor de garganta",
        "presion": "120/80",
        "frecuencia_cardiaca": 85,
        "temperatura": "38.5",
        "antecedentes": "Ninguno",
    }

    print("🏥 Ejecutando Workflow de Triaje Inteligente")
    print("=" * 60)
    print(f"\n📋 Datos del Paciente:")
    print(json.dumps(input_data, indent=2, ensure_ascii=False))
    print("\n" + "=" * 60)
    print("⏳ Procesando con GPT-4...\n")

    async with AsyncSessionLocal() as db:
        # Importar aquí para evitar problemas de relaciones
        from sqlalchemy import text

        # Verificar que el workflow existe
        result = await db.execute(
            text("SELECT id FROM workflows WHERE workflow_id = :wid"),
            {"wid": "triaje-inteligente-demo"},
        )
        workflow = result.fetchone()

        if not workflow:
            print("❌ Workflow 'triaje-inteligente-demo' no encontrado")
            print("   Ejecuta primero: python crear_workflow_ejemplo.py")
            return

        engine = WorkflowEngine(db)

        try:
            execution = await engine.execute_workflow(
                workflow_id="triaje-inteligente-demo",
                input_data=input_data,
                triggered_by="manual",
                user_id=None,  # Sin usuario para evitar problemas de relaciones
            )

            print("=" * 60)
            print(f"✅ Ejecución Completada")
            print("=" * 60)
            print(f"\n📊 Estado: {execution.status.value}")
            print(f"⏱️  Duración: {execution.duration_ms}ms")

            if execution.output_data:
                print(f"\n📤 Resultado:")
                print(json.dumps(execution.output_data, indent=2, ensure_ascii=False))

            if execution.logs:
                print(f"\n📝 Logs de Ejecución:")
                for log in execution.logs:
                    print(
                        f"\n  [{log.get('node_type', 'unknown')}] {log.get('node_id', '')}"
                    )
                    if "result" in log:
                        result = log["result"]
                        if "output" in result:
                            print(
                                f"  Respuesta: {json.dumps(result['output'], indent=4, ensure_ascii=False)}"
                            )

            if execution.error:
                print(f"\n❌ Error: {execution.error}")

            print("\n" + "=" * 60)

        except Exception as e:
            print(f"\n❌ Error ejecutando workflow: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    print("\n🤖 Sistema de Workflows con IA")
    print("Asegúrate de tener OPENAI_API_KEY configurada en .env\n")

    asyncio.run(ejecutar_workflow())
