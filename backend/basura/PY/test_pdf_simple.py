#!/usr/bin/env python3
"""
Script simple para probar si el generador de PDF funciona
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Intentar importar el generador
    from app.services.generador_reportes_pdf import get_generador_pdf
    print("✅ Importación exitosa")

    # Obtener instancia
    generador = get_generador_pdf()
    print("✅ Generador creado")

    # Datos de prueba
    datos_prueba = {
        'titulo': 'Prueba PDF',
        'tipo_imagen': 'rayos_x',
        'analisis_ia_completado': True,
        'resultados_ia': {
            'modelo': 'Test',
            'hallazgos': ['Hallazgo de prueba']
        }
    }

    # Generar PDF
    pdf_buffer = generador.generar_reporte_ia(datos_prueba)
    print("✅ PDF generado exitosamente")

    # Guardar para verificar
    with open('test_pdf_output.pdf', 'wb') as f:
        f.write(pdf_buffer.getvalue())
    print("✅ PDF guardado como test_pdf_output.pdf")

    print("\n🎉 ¡PRUEBA EXITOSA!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
