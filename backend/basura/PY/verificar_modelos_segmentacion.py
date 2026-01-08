#!/usr/bin/env python3
"""
Script de Verificación de Modelos de Segmentación Avanzada
Sistema DDX - Diagnóstico Diferencial Inteligente
"""
import sys
from pathlib import Path

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent))

def verificar_modelos():
    """Verifica la disponibilidad de todos los modelos de segmentación"""
    
    print("=" * 80)
    print("🔍 VERIFICACIÓN DE MODELOS DE SEGMENTACIÓN AVANZADA - SISTEMA DDX")
    print("=" * 80)
    
    try:
        # 1. Importar servicio
        print("\n📦 1. Importando servicio de segmentación...")
        from app.services.segmentacion_avanzada_service import get_servicio_segmentacion
        print("   ✅ Servicio importado correctamente")
        
        # 2. Obtener instancia
        print("\n🔧 2. Inicializando servicio...")
        servicio = get_servicio_segmentacion()
        print("   ✅ Servicio inicializado")
        
        # 3. Verificar disponibilidad
        print("\n📊 3. Verificando disponibilidad de modelos...")
        disponibilidad = servicio.obtener_disponibilidad()
        
        modelos = {
            'lungmask': '🫁 LungMask (Segmentación Pulmonar)',
            'totalsegmentator': '🦴 TotalSegmentator (104 Estructuras)',
            'nnunet': '🎯 nnU-Net (Framework Universal)',
            'swin_unetr': '🔬 Swin UNETR (Vision Transformer)',
            'torchio': '📦 TorchIO (Preprocessing)',
            'paddleseg': '🌊 PaddleSeg (Framework Baidu)',
            'deeplision': '🔍 DeepLesion (Detección Lesiones)',
            'gpu_disponible': '🖥️ GPU CUDA'
        }
        
        disponibles = 0
        no_disponibles = 0
        
        for key, nombre in modelos.items():
            estado = disponibilidad.get(key, False)
            if estado:
                print(f"   ✅ {nombre}")
                disponibles += 1
            else:
                print(f"   ⚠️ {nombre} - NO DISPONIBLE")
                no_disponibles += 1
        
        # 4. Obtener info detallada
        print("\n📋 4. Información detallada de modelos...")
        info_modelos = servicio.obtener_info_modelos()
        
        for modelo_key, info in info_modelos.items():
            if disponibilidad.get(modelo_key, False):
                print(f"\n   📌 {info.get('nombre', modelo_key)}:")
                # Buscar descripción con o sin tilde
                descripcion = info.get('descripcion') or info.get('descripción', 'N/A')
                print(f"      Descripción: {descripcion}")
                print(f"      Modalidad: {info.get('modalidad', 'N/A')}")
                if 'estructuras' in info:
                    print(f"      Estructuras: {info['estructuras']}")
                if 'arquitectura' in info:
                    print(f"      Arquitectura: {info['arquitectura']}")
                if 'organos' in info:
                    print(f"      Órganos: {', '.join(info['organos']) if isinstance(info['organos'], list) else info['organos']}")
        
        # 5. Resumen final
        print("\n" + "=" * 80)
        print("📊 RESUMEN DE VERIFICACIÓN")
        print("=" * 80)
        print(f"✅ Modelos disponibles: {disponibles}/{len(modelos)}")
        print(f"⚠️ Modelos no disponibles: {no_disponibles}/{len(modelos)}")
        
        if disponibles > 0:
            print("\n🎉 ¡Sistema de segmentación avanzada parcialmente funcional!")
            
            # Advertencia sobre GPU
            if not disponibilidad.get('gpu_disponible'):
                print("\n⚠️ GPU CUDA NO DISPONIBLE - El sistema funcionará con CPU")
                print("   • El procesamiento será más lento")
                print("   • Para mejor rendimiento, instala PyTorch con CUDA:")
                print("     pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
            
            print("\n📌 MODELOS FALTANTES:")
            if not disponibilidad.get('lungmask'):
                print("   • LungMask: pip install lungmask")
            if not disponibilidad.get('totalsegmentator'):
                print("   • TotalSegmentator: pip install totalsegmentator")
            if not disponibilidad.get('nnunet'):
                print("   • nnU-Net: pip install nnunetv2")
            if not disponibilidad.get('torchio'):
                print("   • TorchIO: pip install torchio")
            if not disponibilidad.get('paddleseg'):
                print("   • PaddleSeg: pip install paddlepaddle paddleseg")
            
            print("\n💡 INSTALACIÓN RÁPIDA (todos a la vez):")
            print("   pip install -r requirements_segmentacion_avanzada.txt")
        else:
            print("\n⚠️ No hay modelos disponibles")
            print("\n📌 INSTALACIÓN REQUERIDA:")
            print("   cd backend")
            print("   pip install -r requirements_segmentacion_avanzada.txt")
        
        # 6. Verificar integración con servicio multimodal
        print("\n" + "=" * 80)
        print("🔗 VERIFICACIÓN DE INTEGRACIÓN")
        print("=" * 80)
        
        try:
            from app.services.imagen_ia_multimodal_service import get_servicio_multimodal
            servicio_multi = get_servicio_multimodal()
            
            # Obtener disponibilidad completa
            disp_completa = servicio_multi.obtener_disponibilidad()
            
            if 'segmentacion_avanzada' in disp_completa:
                print("   ✅ Segmentación avanzada integrada al servicio multimodal")
                print("\n   📊 Capacidades del sistema completo:")
                
                # Contar modelos multimodales
                modelos_multimodales = sum(1 for k, v in disp_completa.items() 
                                          if isinstance(v, bool) and v and k != 'segmentacion_avanzada')
                
                # Contar modelos de segmentación
                modelos_seg = sum(1 for v in disponibilidad.values() if v)
                
                print(f"      • Modelos multimodales: {modelos_multimodales}")
                print(f"      • Modelos de segmentación: {modelos_seg}")
                print(f"      • TOTAL: {modelos_multimodales + modelos_seg} modelos de IA")
            else:
                print("   ⚠️ Segmentación avanzada NO integrada completamente")
                
        except Exception as e:
            print(f"   ⚠️ Error verificando integración: {e}")
        
        # 7. Endpoints API
        print("\n" + "=" * 80)
        print("🌐 ENDPOINTS API DISPONIBLES")
        print("=" * 80)
        print("\n   📍 Segmentación:")
        print("      POST /api/imagenes/{id}/segmentar?tipo_segmentacion=auto")
        print("      POST /api/imagenes/{id}/segmentar?tipo_segmentacion=pulmones")
        print("      POST /api/imagenes/{id}/segmentar?tipo_segmentacion=total")
        print("      POST /api/imagenes/{id}/segmentar?tipo_segmentacion=lesiones")
        print("\n   📍 Información:")
        print("      GET  /api/imagenes/segmentacion/info")
        print("      GET  /api/imagenes/ia/capacidades")
        
        print("\n" + "=" * 80)
        print("✅ VERIFICACIÓN COMPLETADA")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR durante verificación: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    verificar_modelos()
