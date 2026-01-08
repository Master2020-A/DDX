"""
Script para instalar dependencias de Groq
"""

import subprocess
import sys


def instalar_groq():
    print("=" * 60)
    print("INSTALANDO GROQ PARA IA MÉDICA")
    print("=" * 60)
    print()

    print("📦 Instalando paquete groq...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "groq"])
        print("✅ Groq instalado exitosamente")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar groq: {e}")
        return False

    print()
    print("=" * 60)
    print("✅ INSTALACIÓN COMPLETADA")
    print("=" * 60)
    print()
    print("📋 PRÓXIMOS PASOS:")
    print()
    print("1. Obtén tu API Key GRATIS:")
    print("   👉 https://console.groq.com/keys")
    print()
    print("2. Agrega a tu archivo .env:")
    print("   AI_PROVIDER=groq")
    print("   GROQ_API_KEY=gsk_tu-api-key-aqui")
    print()
    print("3. Reinicia el servidor backend")
    print()
    print("🎉 ¡Listo para usar IA médica GRATIS con Groq!")
    print()

    return True


if __name__ == "__main__":
    instalar_groq()
