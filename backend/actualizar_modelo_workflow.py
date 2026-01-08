"""
Script para actualizar el modelo del workflow de triaje a un modelo open source
"""

import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal


async def actualizar_modelo():
    """Actualiza el modelo del agente de triaje a Qwen 2.5 7B"""

    async with AsyncSessionLocal() as db:
        # Verificar agente actual
        result = await db.execute(
            text("SELECT name, model FROM ai_agents WHERE agent_id = 'triaje-gpt4'")
        )
        agente = result.fetchone()

        if agente:
            print(f"📋 Agente actual:")
            print(f"   Nombre: {agente.name}")
            print(f"   Modelo actual: {agente.model}")
            print()

        # Actualizar a modelo open source
        nuevo_modelo = "qwen2.5:7b"  # Cambiar a: llama3.1:8b, mistral:7b, etc.

        await db.execute(
            text(
                """
                UPDATE ai_agents 
                SET model = :nuevo_modelo,
                    updated_at = CURRENT_TIMESTAMP
                WHERE agent_id = 'triaje-gpt4'
            """
            ),
            {"nuevo_modelo": nuevo_modelo},
        )

        await db.commit()

        print(f"✅ Modelo actualizado exitosamente!")
        print(f"   Nuevo modelo: {nuevo_modelo}")
        print()
        print("📝 Modelos disponibles:")
        print()
        print("   🏠 Ollama (Local - Gratis):")
        print("      - qwen2.5:7b          (Recomendado para español)")
        print("      - llama3.1:8b         (Muy popular)")
        print("      - mistral:7b          (Rápido)")
        print("      - phi3:mini           (Ligero)")
        print()
        print("   ☁️  Groq (Cloud - Rápido):")
        print("      - llama-3.1-70b-versatile")
        print("      - llama-3.1-8b-instant")
        print("      - mixtral-8x7b-32768")
        print()
        print(
            "💡 Para cambiar el modelo, edita la variable 'nuevo_modelo' en este script"
        )
        print()
        print("🚀 Próximos pasos:")
        print("   1. Asegúrate que Ollama está corriendo: ollama list")
        print("   2. Descarga el modelo: ollama pull qwen2.5:7b")
        print("   3. Ejecuta el workflow desde: http://localhost:3000/workflows")


if __name__ == "__main__":
    asyncio.run(actualizar_modelo())
