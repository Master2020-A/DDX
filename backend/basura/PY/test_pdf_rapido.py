#!/usr/bin/env python3
"""
Script de prueba simple para el generador de PDF
"""
import sys
sys.path.insert(0, r'C:\Users\Master\Documents\DDX\backend')

try:
    print("🧪 PROBANDO GENERADOR DE PDF...")
    print("=" * 60)
    
    # Importar generador
    print("\n1️⃣ Importando generador...")
    from app.services.generador_reportes_pdf_basico import get_generador_pdf
    print("   ✅ Importación exitosa")
    
    # Obtener instancia
    print("\n2️⃣ Obteniendo instancia...")
    generador = get_generador_pdf()
    print("   ✅ Instancia creada")
    
    # Datos de prueba simples
    print("\n3️⃣ Generando PDF de prueba...")
    datos_prueba = {
        'titulo': 'Torax',
        'tipo_imagen': 'rayos_x',
        'region_anatomica': 'torax',
        'analisis_ia_completado': True,
        'resultados_ia': {
            'modelo': 'TorchXRayVision',
            'hallazgos': ['Normal'],
            'confianza_global': 0.85
        },
        'hallazgos': ['Normal (85%)']
    }
    
    # Generar PDF
    pdf_buffer = generador.generar_reporte_ia(datos_prueba)
    print("   ✅ PDF generado")
    
    # Guardar para verificar
    print("\n4️⃣ Guardando PDF...")
    with open('test_reporte.pdf', 'wb') as f:
        f.write(pdf_buffer.getvalue())
    print("   ✅ PDF guardado como 'test_reporte.pdf'")
    
    print("\n" + "=" * 60)
    print("🎉 ¡PRUEBA EXITOSA!")
    print("\n📄 Abre 'test_reporte.pdf' para verificar el contenido")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
