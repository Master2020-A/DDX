import sys
import traceback

print("🔍 Probando importación de módulos N8N...\n")

# Test 1: Importar módulo n8n
print("1. Importando app.api.n8n...")
try:
    from app.api import n8n

    print(f"   ✅ Módulo importado")
    print(f"   ✅ Router existe: {hasattr(n8n, 'router')}")
    if hasattr(n8n, "router"):
        print(f"   ✅ Router type: {type(n8n.router)}")
        print(f"   ✅ Router prefix: {getattr(n8n.router, 'prefix', 'No prefix')}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    traceback.print_exc()

print()

# Test 2: Importar módulo n8n_workflows
print("2. Importando app.api.n8n_workflows...")
try:
    from app.api import n8n_workflows

    print(f"   ✅ Módulo importado")
    print(f"   ✅ Router existe: {hasattr(n8n_workflows, 'router')}")
    if hasattr(n8n_workflows, "router"):
        print(f"   ✅ Router type: {type(n8n_workflows.router)}")
        print(
            f"   ✅ Router prefix: {getattr(n8n_workflows.router, 'prefix', 'No prefix')}"
        )
except Exception as e:
    print(f"   ❌ Error: {e}")
    traceback.print_exc()

print()

# Test 3: Simular safe_include
print("3. Simulando safe_include...")
try:
    module_path = "app.api.n8n"
    module = __import__(module_path, fromlist=["router"])
    router = getattr(module, "router", None)
    if router is None:
        print(f"   ⚠️ {module_path} no exporta 'router'")
    else:
        print(f"   ✅ Router obtenido correctamente")
        print(f"   ✅ Prefix: {getattr(router, 'prefix', 'No prefix')}")
        print(f"   ✅ Tags: {getattr(router, 'tags', 'No tags')}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    traceback.print_exc()

print("\n✅ Pruebas completadas")
