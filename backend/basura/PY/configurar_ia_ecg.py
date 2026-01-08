"""
Script de configuración para IA de ECG
Ayuda a configurar la API key de OpenAI
"""
import os
import sys

def verificar_openai():
    """Verifica si OpenAI está instalado"""
    try:
        import openai
        print("✅ OpenAI instalado correctamente")
        print(f"   Versión: {openai.__version__}")
        return True
    except ImportError:
        print("❌ OpenAI NO está instalado")
        print("\n💡 Instala con: pip install openai")
        return False

def verificar_api_key():
    """Verifica si la API key está configurada"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if api_key:
        print("✅ API Key configurada")
        print(f"   Key: {api_key[:10]}...{api_key[-4:]}")
        return True
    else:
        print("❌ API Key NO configurada")
        print("\n💡 Configura con:")
        print("   Windows PowerShell:")
        print('   $env:OPENAI_API_KEY="sk-tu-key-aqui"')
        print("\n   Windows CMD:")
        print('   set OPENAI_API_KEY=sk-tu-key-aqui')
        print("\n   O crea archivo .env:")
        print('   echo OPENAI_API_KEY=sk-tu-key-aqui > .env')
        return False

def probar_conexion():
    """Prueba la conexión con OpenAI"""
    try:
        import openai
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            print("❌ No se puede probar: falta API key")
            return False
        
        print("\n🔄 Probando conexión con OpenAI...")
        client = openai.OpenAI(api_key=api_key)
        
        # Hacer una petición simple
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hola"}],
            max_tokens=10
        )
        
        print("✅ Conexión exitosa con OpenAI")
        print(f"   Modelo: gpt-4o")
        print(f"   Respuesta: {response.choices[0].message.content}")
        return True
    
    except Exception as e:
        print(f"❌ Error en conexión: {e}")
        return False

def probar_analisis_ecg():
    """Prueba el analizador de ECG con IA"""
    try:
        from app.services.analizador_ecg_ia import AnalizadorECGIA
        
        print("\n🔄 Probando analizador de ECG...")
        analizador = AnalizadorECGIA()
        print("✅ Analizador de ECG inicializado correctamente")
        return True
    
    except ImportError as e:
        print(f"❌ Error importando analizador: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def mostrar_instrucciones():
    """Muestra instrucciones para obtener API key"""
    print("\n" + "="*60)
    print("📖 CÓMO OBTENER API KEY DE OPENAI")
    print("="*60)
    print("\n1. Ir a: https://platform.openai.com/api-keys")
    print("2. Crear cuenta (si no tienes)")
    print("3. Click 'Create new secret key'")
    print("4. Copiar la key (empieza con 'sk-...')")
    print("\n5. Configurar en tu sistema:")
    print("\n   Windows PowerShell:")
    print('   $env:OPENAI_API_KEY="sk-tu-key-aqui"')
    print("\n   Windows CMD:")
    print('   set OPENAI_API_KEY=sk-tu-key-aqui')
    print("\n   O crear archivo .env en backend/:")
    print('   OPENAI_API_KEY=sk-tu-key-aqui')
    print("\n6. Reiniciar este script")
    print("="*60)

def main():
    """Función principal"""
    print("="*60)
    print("🤖 CONFIGURACIÓN DE IA PARA ECG")
    print("="*60)
    
    # Verificar OpenAI
    print("\n1️⃣ Verificando instalación de OpenAI...")
    openai_ok = verificar_openai()
    
    if not openai_ok:
        print("\n❌ Instala OpenAI primero: pip install openai")
        return
    
    # Verificar API key
    print("\n2️⃣ Verificando API Key...")
    api_key_ok = verificar_api_key()
    
    if not api_key_ok:
        mostrar_instrucciones()
        return
    
    # Probar conexión
    print("\n3️⃣ Probando conexión...")
    conexion_ok = probar_conexion()
    
    if not conexion_ok:
        print("\n❌ Verifica tu API key")
        return
    
    # Probar analizador
    print("\n4️⃣ Probando analizador de ECG...")
    analizador_ok = probar_analisis_ecg()
    
    if not analizador_ok:
        print("\n❌ Error en analizador")
        return
    
    # Todo OK
    print("\n" + "="*60)
    print("✅ ¡TODO CONFIGURADO CORRECTAMENTE!")
    print("="*60)
    print("\n📊 El sistema ahora puede analizar ECGs con IA")
    print("\n🚀 Próximos pasos:")
    print("   1. Reiniciar el servidor backend")
    print("   2. Subir una imagen de ECG")
    print("   3. El sistema usará IA automáticamente si OCR falla")
    print("\n💰 Costo: ~$0.01-0.03 por imagen")
    print("="*60)

if __name__ == "__main__":
    main()
