#!/usr/bin/env python
"""Script para diagnosticar por qué los routers de N8N no se cargan"""

import sys
import traceback
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 60)
print("DIAGNÓSTICO DE ROUTERS N8N")
print("=" * 60)
print()

# Test 1: Verificar que los archivos existen
print("1. Verificando archivos...")
import os

n8n_file = "app/api/n8n.py"
n8n_workflows_file = "app/api/n8n_workflows.py"

if os.path.exists(n8n_file):
    print(f"   ✅ {n8n_file} existe")
else:
    print(f"   ❌ {n8n_file} NO existe")

if os.path.exists(n8n_workflows_file):
    print(f"   ✅ {n8n_workflows_file} existe")
else:
    print(f"   ❌ {n8n_workflows_file} NO existe")

print()

# Test 2: Intentar importar app.api.n8n
print("2. Importando app.api.n8n...")
try:
    from app.api import n8n

    print("   ✅ Módulo importado exitosamente")

    if hasattr(n8n, "router"):
        print("   ✅ Tiene atributo 'router'")
        print(f"   📋 Tipo de router: {type(n8n.router)}")
        print(f"   📋 Prefix: {getattr(n8n.router, 'prefix', 'Sin prefix')}")
        print(f"   📋 Tags: {getattr(n8n.router, 'tags', 'Sin tags')}")
    else:
        print("   ❌ NO tiene atributo 'router'")
        print(f"   📋 Atributos disponibles: {dir(n8n)}")

except Exception as e:
    print(f"   ❌ Error al importar: {e}")
    print("\n   Traceback completo:")
    traceback.print_exc()

print()

# Test 3: Intentar importar app.api.n8n_workflows
print("3. Importando app.api.n8n_workflows...")
try:
    from app.api import n8n_workflows

    print("   ✅ Módulo importado exitosamente")

    if hasattr(n8n_workflows, "router"):
        print("   ✅ Tiene atributo 'router'")
        print(f"   📋 Tipo de router: {type(n8n_workflows.router)}")
        print(f"   📋 Prefix: {getattr(n8n_workflows.router, 'prefix', 'Sin prefix')}")
        print(f"   📋 Tags: {getattr(n8n_workflows.router, 'tags', 'Sin tags')}")
    else:
        print("   ❌ NO tiene atributo 'router'")
        print(f"   📋 Atributos disponibles: {dir(n8n_workflows)}")

except Exception as e:
    print(f"   ❌ Error al importar: {e}")
    print("\n   Traceback completo:")
    traceback.print_exc()

print()

# Test 4: Simular safe_include
print("4. Simulando safe_include (como en main.py)...")
try:
    module_path = "app.api.n8n"
    print(f"   Importando {module_path}...")
    module = __import__(module_path, fromlist=["router"])
    print(f"   ✅ Módulo importado")

    router = getattr(module, "router", None)
    if router is None:
        print(f"   ❌ {module_path} no exporta 'router'")
    else:
        print(f"   ✅ Router obtenido correctamente")
        print(f"   📋 Prefix: {getattr(router, 'prefix', 'Sin prefix')}")
        print(f"   📋 Tags: {getattr(router, 'tags', 'Sin tags')}")

except Exception as e:
    print(f"   ❌ Error: {e}")
    print("\n   Traceback completo:")
    traceback.print_exc()

print()
print("=" * 60)
print("FIN DEL DIAGNÓSTICO")
print("=" * 60)
