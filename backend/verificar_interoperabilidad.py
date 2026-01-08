"""
Script para verificar que el módulo de interoperabilidad está correctamente configurado
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("VERIFICACIÓN DEL MÓDULO DE INTEROPERABILIDAD")
print("=" * 60)

# 1. Verificar que el módulo se puede importar
print("\n1. Verificando importación del router...")
try:
    from app.api.interoperabilidad import router

    print("   ✅ Router importado correctamente")
    print(f"   📍 Rutas registradas: {len(router.routes)}")
except Exception as e:
    print(f"   ❌ Error importando router: {e}")
    sys.exit(1)

# 2. Verificar modelos
print("\n2. Verificando modelos...")
try:
    from app.models.interoperabilidad import (
        InstitucionExterna,
        SolicitudIntercambio,
        HistoriaClinicaUnificada,
        ConsentimientoIntercambio,
    )

    print("   ✅ Modelos de interoperabilidad importados")
except Exception as e:
    print(f"   ❌ Error importando modelos: {e}")

try:
    from app.models.notificacion_interoperabilidad import NotificacionInteroperabilidad

    print("   ✅ Modelo de notificaciones importado")
except Exception as e:
    print(f"   ❌ Error importando notificaciones: {e}")

try:
    from app.models.webhook_interoperabilidad import WebhookSuscripcion, WebhookEntrega

    print("   ✅ Modelos de webhooks importados")
except Exception as e:
    print(f"   ❌ Error importando webhooks: {e}")

# 3. Verificar servicios
print("\n3. Verificando servicios...")
try:
    from app.services.intercambio_expedientes import ServicioIntercambioExpedientes

    print("   ✅ Servicio de intercambio de expedientes importado")
except Exception as e:
    print(f"   ❌ Error: {e}")

try:
    from app.services.metricas_interoperabilidad import MetricasInteroperabilidadService

    print("   ✅ Servicio de métricas importado")
except Exception as e:
    print(f"   ❌ Error: {e}")

try:
    from app.services.notificaciones_interoperabilidad import (
        NotificacionesInteroperabilidadService,
    )

    print("   ✅ Servicio de notificaciones importado")
except Exception as e:
    print(f"   ❌ Error: {e}")

try:
    from app.services.webhook_service import WebhookService

    print("   ✅ Servicio de webhooks importado")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 4. Listar endpoints
print("\n4. Endpoints disponibles:")
print("   " + "-" * 56)
for route in router.routes:
    if hasattr(route, "methods") and hasattr(route, "path"):
        methods = ", ".join(route.methods)
        print(f"   {methods:10} {route.path}")
print("   " + "-" * 56)

# 5. Verificar que está en main.py
print("\n5. Verificando registro en main.py...")
try:
    with open("app/main.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "interoperabilidad" in content and "/api/interoperabilidad" in content:
            print("   ✅ Router configurado en main.py")
        else:
            print("   ⚠️  Router NO encontrado en main.py")
except Exception as e:
    print(f"   ❌ Error leyendo main.py: {e}")

print("\n" + "=" * 60)
print("VERIFICACIÓN COMPLETADA")
print("=" * 60)
print("\n📝 PRÓXIMOS PASOS:")
print("   1. Reiniciar el servidor backend (Ctrl+C y volver a ejecutar)")
print("   2. Verificar que el servidor esté corriendo en http://localhost:8612")
print("   3. Acceder a http://localhost:8612/docs para ver la documentación")
print("   4. Probar los endpoints desde el frontend")
print("\n")
