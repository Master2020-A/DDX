"""
Verificar que bcrypt funciona correctamente
"""
print("="*70)
print("VERIFICANDO BCRYPT")
print("="*70)

try:
    import bcrypt
    print("✅ bcrypt importado correctamente")
    print(f"   Version: {bcrypt.__version__}")
    
    # Test hash y verify
    print("\n[TEST] Generando hash de password...")
    password = b"Test123!"
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    print(f"✅ Hash generado: {hashed.decode()[:50]}...")
    
    print("\n[TEST] Verificando password...")
    is_valid = bcrypt.checkpw(password, hashed)
    print(f"✅ Verificacion: {'CORRECTA' if is_valid else 'FALLO'}")
    
    # Test con passlib (lo que usa la app)
    print("\n[TEST] Probando con passlib (usado en la app)...")
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed2 = pwd_context.hash("Admin123!")
    is_valid2 = pwd_context.verify("Admin123!", hashed2)
    
    print(f"✅ passlib + bcrypt: {'FUNCIONA' if is_valid2 else 'FALLO'}")
    
    print("\n" + "="*70)
    print("✅ BCRYPT FUNCIONA CORRECTAMENTE")
    print("="*70)
    print("\nAhora puedes:")
    print("1. Reiniciar el backend")
    print("2. Ejecutar: python crear_admin.py")
    print("3. Intentar login en el frontend")
    print("="*70)
    
except ImportError as e:
    print(f"\n❌ ERROR: No se puede importar bcrypt")
    print(f"   {e}")
    print("\n💡 SOLUCIÓN: pip install bcrypt==4.1.2")
    
except AttributeError as e:
    print(f"\n❌ ERROR: bcrypt está corrupto")
    print(f"   {e}")
    print("\n💡 SOLUCIÓN: Ejecuta reparar_bcrypt.bat")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
