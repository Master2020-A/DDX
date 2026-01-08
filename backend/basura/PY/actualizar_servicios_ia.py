"""
Script para actualizar todos los servicios de IA para usar el nuevo cliente de OpenAI
"""

import os
import re


def actualizar_servicio(filepath):
    """Actualizar un servicio para usar el nuevo cliente de OpenAI"""

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Verificar si ya está actualizado
    if "from app.services.openai_client import chat_completion" in content:
        print(f"✓ {os.path.basename(filepath)} ya está actualizado")
        return False

    # Verificar si usa OpenAI
    if "import openai" not in content and "openai.ChatCompletion" not in content:
        print(f"- {os.path.basename(filepath)} no usa OpenAI")
        return False

    print(f"📝 Actualizando {os.path.basename(filepath)}...")

    # Actualizar imports
    content = re.sub(r"import openai\n", "", content)

    content = re.sub(r"from app\.core\.config import settings\n", "", content)

    # Agregar import de json si no existe
    if "import json" not in content:
        # Buscar la sección de imports
        import_section = re.search(r"(from typing.*?\n)", content)
        if import_section:
            content = content.replace(
                import_section.group(1), import_section.group(1) + "import json\n"
            )

    # Agregar nuevo import
    if "from app.services.openai_client import chat_completion" not in content:
        # Buscar el último import de app.*
        last_app_import = None
        for match in re.finditer(r"from app\..*?\n", content):
            last_app_import = match

        if last_app_import:
            insert_pos = last_app_import.end()
            content = (
                content[:insert_pos]
                + "from app.services.openai_client import chat_completion\n"
                + content[insert_pos:]
            )

    # Actualizar __init__
    content = re.sub(
        r"def __init__\(self\):\s+openai\.api_key = settings\.OPENAI_API_KEY",
        "def __init__(self):\n        pass",
        content,
    )

    # Actualizar llamadas a OpenAI
    content = re.sub(
        r'response = await openai\.ChatCompletion\.acreate\(\s*model="([^"]+)",\s*messages=',
        r"response = await chat_completion(\n            messages=",
        content,
    )

    # Agregar model después de messages
    content = re.sub(
        r"(response = await chat_completion\(\s*messages=\[.*?\],)\s*temperature=",
        r'\1\n            model="gpt-4o",\n            temperature=',
        content,
        flags=re.DOTALL,
    )

    # Remover import json duplicados después de response
    content = re.sub(
        r"\n\s+import json\n\s+return json\.loads",
        r"\n\n        return json.loads",
        content,
    )

    content = re.sub(
        r"\n\s+import json\n\s+analisis = json\.loads",
        r"\n\n        analisis = json.loads",
        content,
    )

    # Guardar archivo actualizado
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ {os.path.basename(filepath)} actualizado")
    return True


def main():
    print("=" * 60)
    print("ACTUALIZAR SERVICIOS DE IA PARA NUEVO CLIENTE OPENAI")
    print("=" * 60)
    print()

    services_dir = os.path.join(os.path.dirname(__file__), "app", "services")

    servicios_ia = [
        "interacciones_medicamentosas_service.py",
        "deteccion_anomalias_service.py",
    ]

    actualizados = 0

    for servicio in servicios_ia:
        filepath = os.path.join(services_dir, servicio)
        if os.path.exists(filepath):
            if actualizar_servicio(filepath):
                actualizados += 1
        else:
            print(f"⚠️  No se encontró: {servicio}")

    print()
    print("=" * 60)
    print(f"✅ ACTUALIZACIÓN COMPLETADA: {actualizados} servicios actualizados")
    print("=" * 60)
    print()
    print("🔄 El servidor se reiniciará automáticamente")
    print("🌐 Prueba el módulo de IA en: http://localhost:5173/ia-medica")


if __name__ == "__main__":
    main()
