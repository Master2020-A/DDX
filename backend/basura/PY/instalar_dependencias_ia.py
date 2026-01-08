"""
Script para instalar dependencias del módulo de IA Médica
"""

import subprocess
import sys


def instalar_paquete(paquete):
    """Instala un paquete usando pip"""
    print(f"\n📦 Instalando {paquete}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", paquete])
        print(f"✅ {paquete} instalado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar {paquete}: {e}")
        return False


def main():
    print("=" * 60)
    print("🤖 INSTALACIÓN DE DEPENDENCIAS - IA MÉDICA")
    print("=" * 60)

    dependencias = [
        "jiter",  # Dependencia de OpenAI
        "openai>=1.0.0",  # Cliente de OpenAI actualizado
    ]

    exitos = 0
    fallos = 0

    for dep in dependencias:
        if instalar_paquete(dep):
            exitos += 1
        else:
            fallos += 1

    print("\n" + "=" * 60)
    print(f"✅ Instalación completada: {exitos} éxitos, {fallos} fallos")
    print("=" * 60)

    if fallos == 0:
        print("\n✅ Todas las dependencias instaladas correctamente")
        print("🔄 Puedes reiniciar el servidor backend ahora")
    else:
        print(f"\n⚠️  {fallos} dependencias no se pudieron instalar")
        print("Por favor, instálalas manualmente")


if __name__ == "__main__":
    main()
