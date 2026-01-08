"""
Script para inicializar rangos de referencia de laboratorio clínico
Basado en valores estándar internacionales
"""
import sys
import asyncio
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.laboratorio import RangoReferencia


# Rangos de referencia por área
RANGOS_HEMATOLOGIA = [
    # BIOMETRÍA HEMÁTICA
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'hemoglobina',
        'sexo': 'M',
        'valor_min': 13.5,
        'valor_max': 17.5,
        'critico_bajo': 7.0,
        'critico_alto': 20.0,
        'unidad': 'g/dL',
        'descripcion': 'Proteína que transporta oxígeno en la sangre',
        'interpretacion_bajo': 'Anemia - puede indicar pérdida de sangre, deficiencia nutricional o enfermedad crónica',
        'interpretacion_alto': 'Policitemia - puede indicar deshidratación o trastorno de médula ósea'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'hemoglobina',
        'sexo': 'F',
        'valor_min': 12.0,
        'valor_max': 16.0,
        'critico_bajo': 7.0,
        'critico_alto': 20.0,
        'unidad': 'g/dL',
        'descripcion': 'Proteína que transporta oxígeno en la sangre',
        'interpretacion_bajo': 'Anemia - puede indicar pérdida de sangre, deficiencia nutricional o enfermedad crónica',
        'interpretacion_alto': 'Policitemia - puede indicar deshidratación o trastorno de médula ósea'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'hematocrito',
        'sexo': 'M',
        'valor_min': 40.0,
        'valor_max': 54.0,
        'critico_bajo': 20.0,
        'critico_alto': 60.0,
        'unidad': '%',
        'descripcion': 'Porcentaje de volumen de eritrocitos en la sangre'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'hematocrito',
        'sexo': 'F',
        'valor_min': 36.0,
        'valor_max': 48.0,
        'critico_bajo': 20.0,
        'critico_alto': 60.0,
        'unidad': '%',
        'descripcion': 'Porcentaje de volumen de eritrocitos en la sangre'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'eritrocitos',
        'sexo': 'M',
        'valor_min': 4.5,
        'valor_max': 5.9,
        'critico_bajo': 2.5,
        'critico_alto': 7.0,
        'unidad': 'millones/μL',
        'descripcion': 'Glóbulos rojos - transportan oxígeno'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'eritrocitos',
        'sexo': 'F',
        'valor_min': 4.0,
        'valor_max': 5.2,
        'critico_bajo': 2.5,
        'critico_alto': 7.0,
        'unidad': 'millones/μL',
        'descripcion': 'Glóbulos rojos - transportan oxígeno'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'leucocitos',
        'valor_min': 4.5,
        'valor_max': 11.0,
        'critico_bajo': 2.0,
        'critico_alto': 30.0,
        'unidad': 'mil/μL',
        'descripcion': 'Glóbulos blancos - defensa del organismo',
        'interpretacion_bajo': 'Leucopenia - puede indicar infección viral, deficiencia de médula ósea o efecto de medicamentos',
        'interpretacion_alto': 'Leucocitosis - puede indicar infección bacteriana, inflamación o leucemia'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'plaquetas',
        'valor_min': 150.0,
        'valor_max': 450.0,
        'critico_bajo': 50.0,
        'critico_alto': 1000.0,
        'unidad': 'mil/μL',
        'descripcion': 'Células de coagulación',
        'interpretacion_bajo': 'Trombocitopenia - riesgo de sangrado, evaluar causa',
        'interpretacion_alto': 'Trombocitosis - riesgo de trombosis, evaluar causa'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'neutrofilos',
        'valor_min': 40.0,
        'valor_max': 70.0,
        'unidad': '%',
        'descripcion': 'Principal tipo de leucocitos, combaten infecciones bacterianas'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'linfocitos',
        'valor_min': 20.0,
        'valor_max': 45.0,
        'unidad': '%',
        'descripcion': 'Leucocitos que combaten infecciones virales y producen anticuerpos'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'monocitos',
        'valor_min': 2.0,
        'valor_max': 10.0,
        'unidad': '%',
        'descripcion': 'Leucocitos que eliminan células muertas y combaten infecciones crónicas'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'eosinofilos',
        'valor_min': 1.0,
        'valor_max': 4.0,
        'unidad': '%',
        'descripcion': 'Leucocitos relacionados con alergias y parásitos'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'basofilos',
        'valor_min': 0.0,
        'valor_max': 2.0,
        'unidad': '%',
        'descripcion': 'Leucocitos relacionados con reacciones alérgicas'
    },
    # ÍNDICES ERITROCITARIOS
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'vcm',
        'valor_min': 80.0,
        'valor_max': 100.0,
        'unidad': 'fL',
        'descripcion': 'Volumen Corpuscular Medio - tamaño promedio de los eritrocitos',
        'interpretacion_bajo': 'Microcitosis - puede indicar anemia ferropénica o talasemia',
        'interpretacion_alto': 'Macrocitosis - puede indicar deficiencia de B12/folato o alcoholismo'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'hcm',
        'valor_min': 27.0,
        'valor_max': 31.0,
        'unidad': 'pg',
        'descripcion': 'Hemoglobina Corpuscular Media - cantidad promedio de Hb por eritrocito',
        'interpretacion_bajo': 'Hipocromía - asociada a anemia ferropénica',
        'interpretacion_alto': 'Hipercromía - asociada a macrocitosis'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'chcm',
        'valor_min': 32.0,
        'valor_max': 36.0,
        'unidad': 'g/dL',
        'descripcion': 'Concentración de Hemoglobina Corpuscular Media',
        'interpretacion_bajo': 'Hipocromía - anemia ferropénica',
        'interpretacion_alto': 'Puede indicar esferocitosis o error técnico'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'rdw',
        'valor_min': 11.5,
        'valor_max': 14.5,
        'unidad': '%',
        'descripcion': 'Amplitud de Distribución Eritrocitaria - variación en tamaño de eritrocitos',
        'interpretacion_alto': 'Anisocitosis - puede indicar anemia ferropénica, deficiencia de B12 o hemoglobinopatías'
    },
    # VALORES ABSOLUTOS DE LEUCOCITOS
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'neutrofilos_abs',
        'valor_min': 1.8,
        'valor_max': 7.7,
        'critico_bajo': 0.5,
        'critico_alto': 20.0,
        'unidad': 'x10³/μL',
        'descripcion': 'Neutrófilos absolutos',
        'interpretacion_bajo': 'Neutropenia - riesgo de infecciones bacterianas',
        'interpretacion_alto': 'Neutrofilia - infección bacteriana, inflamación o estrés'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'linfocitos_abs',
        'valor_min': 1.0,
        'valor_max': 4.8,
        'critico_bajo': 0.5,
        'unidad': 'x10³/μL',
        'descripcion': 'Linfocitos absolutos',
        'interpretacion_bajo': 'Linfopenia - inmunodeficiencia',
        'interpretacion_alto': 'Linfocitosis - infección viral o leucemia linfocítica'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'monocitos_abs',
        'valor_min': 0.2,
        'valor_max': 1.0,
        'unidad': 'x10³/μL',
        'descripcion': 'Monocitos absolutos',
        'interpretacion_alto': 'Monocitosis - infecciones crónicas, tuberculosis'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'eosinofilos_abs',
        'valor_min': 0.0,
        'valor_max': 0.5,
        'unidad': 'x10³/μL',
        'descripcion': 'Eosinófilos absolutos',
        'interpretacion_alto': 'Eosinofilia - alergias, parasitosis, asma'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'basofilos_abs',
        'valor_min': 0.0,
        'valor_max': 0.2,
        'unidad': 'x10³/μL',
        'descripcion': 'Basófilos absolutos'
    },
    # BANDAS (Neutrófilos inmaduros)
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'bandas',
        'valor_min': 0.0,
        'valor_max': 3.0,
        'unidad': '%',
        'descripcion': 'Neutrófilos en banda (inmaduros)',
        'interpretacion_alto': 'Desviación a la izquierda - infección bacteriana severa'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'biometria_hematica',
        'parametro': 'segmentados',
        'valor_min': 40.0,
        'valor_max': 70.0,
        'unidad': '%',
        'descripcion': 'Neutrófilos segmentados (maduros)'
    },
    # VELOCIDAD DE SEDIMENTACIÓN GLOBULAR
    {
        'area': 'hematologia',
        'tipo_prueba': 'vsg',
        'parametro': 'vsg',
        'sexo': 'M',
        'valor_min': 0.0,
        'valor_max': 15.0,
        'unidad': 'mm/h',
        'descripcion': 'Indicador de inflamación',
        'interpretacion_alto': 'Inflamación activa - evaluar causa (infección, enfermedad autoinmune, cáncer)'
    },
    {
        'area': 'hematologia',
        'tipo_prueba': 'vsg',
        'parametro': 'vsg',
        'sexo': 'F',
        'valor_min': 0.0,
        'valor_max': 20.0,
        'unidad': 'mm/h',
        'descripcion': 'Indicador de inflamación',
        'interpretacion_alto': 'Inflamación activa - evaluar causa (infección, enfermedad autoinmune, cáncer)'
    },
]

RANGOS_QUIMICA_CLINICA = [
    # GLUCOSA
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'glucosa',
        'parametro': 'glucosa',
        'valor_min': 70.0,
        'valor_max': 100.0,
        'critico_bajo': 40.0,
        'critico_alto': 500.0,
        'unidad': 'mg/dL',
        'descripcion': 'Glucosa en sangre en ayunas',
        'interpretacion_bajo': 'Hipoglucemia - requiere atención inmediata, puede causar pérdida de conciencia',
        'interpretacion_alto': 'Hiperglucemia - descartar diabetes mellitus, prediabetes o resistencia a la insulina'
    },
    # FUNCIÓN RENAL
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_renal',
        'parametro': 'creatinina',
        'sexo': 'M',
        'valor_min': 0.7,
        'valor_max': 1.3,
        'critico_alto': 5.0,
        'unidad': 'mg/dL',
        'descripcion': 'Producto de desecho muscular, indicador de función renal',
        'interpretacion_alto': 'Función renal disminuida - puede indicar enfermedad renal crónica'
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_renal',
        'parametro': 'creatinina',
        'sexo': 'F',
        'valor_min': 0.6,
        'valor_max': 1.1,
        'critico_alto': 5.0,
        'unidad': 'mg/dL',
        'descripcion': 'Producto de desecho muscular, indicador de función renal',
        'interpretacion_alto': 'Función renal disminuida - puede indicar enfermedad renal crónica'
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_renal',
        'parametro': 'urea',
        'valor_min': 15.0,
        'valor_max': 40.0,
        'critico_alto': 100.0,
        'unidad': 'mg/dL',
        'descripcion': 'Producto final del metabolismo de proteínas',
        'interpretacion_alto': 'Puede indicar deshidratación, dieta alta en proteínas o insuficiencia renal'
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_renal',
        'parametro': 'acido_urico',
        'sexo': 'M',
        'valor_min': 3.4,
        'valor_max': 7.0,
        'unidad': 'mg/dL',
        'descripcion': 'Producto del metabolismo de purinas',
        'interpretacion_alto': 'Hiperuricemia - riesgo de gota, cálculos renales'
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_renal',
        'parametro': 'acido_urico',
        'sexo': 'F',
        'valor_min': 2.4,
        'valor_max': 6.0,
        'unidad': 'mg/dL',
        'descripcion': 'Producto del metabolismo de purinas',
        'interpretacion_alto': 'Hiperuricemia - riesgo de gota, cálculos renales'
    },
    # PERFIL LIPÍDICO
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'perfil_lipidico',
        'parametro': 'colesterol_total',
        'valor_min': 0.0,
        'valor_max': 200.0,
        'unidad': 'mg/dL',
        'descripcion': 'Colesterol total en sangre',
        'interpretacion_alto': 'Hipercolesterolemia - riesgo cardiovascular aumentado'
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'perfil_lipidico',
        'parametro': 'trigliceridos',
        'valor_min': 0.0,
        'valor_max': 150.0,
        'critico_alto': 500.0,
        'unidad': 'mg/dL',
        'descripcion': 'Grasa en sangre',
        'interpretacion_alto': 'Hipertrigliceridemia - riesgo de pancreatitis y enfermedad cardiovascular'
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'perfil_lipidico',
        'parametro': 'hdl',
        'sexo': 'M',
        'valor_min': 40.0,
        'valor_max': 200.0,
        'unidad': 'mg/dL',
        'descripcion': 'Colesterol "bueno"',
        'interpretacion_bajo': 'HDL bajo - riesgo cardiovascular aumentado'
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'perfil_lipidico',
        'parametro': 'hdl',
        'sexo': 'F',
        'valor_min': 50.0,
        'valor_max': 200.0,
        'unidad': 'mg/dL',
        'descripcion': 'Colesterol "bueno"',
        'interpretacion_bajo': 'HDL bajo - riesgo cardiovascular aumentado'
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'perfil_lipidico',
        'parametro': 'ldl',
        'valor_min': 0.0,
        'valor_max': 100.0,
        'unidad': 'mg/dL',
        'descripcion': 'Colesterol "malo"',
        'interpretacion_alto': 'LDL elevado - principal factor de riesgo cardiovascular'
    },
    # FUNCIÓN HEPÁTICA
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_hepatica',
        'parametro': 'tgo',
        'valor_min': 5.0,
        'valor_max': 40.0,
        'critico_alto': 1000.0,
        'unidad': 'U/L',
        'descripcion': 'Transaminasa glutámico oxalacética (AST)',
        'interpretacion_alto': 'Daño hepático o muscular'
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_hepatica',
        'parametro': 'tgp',
        'valor_min': 7.0,
        'valor_max': 56.0,
        'critico_alto': 1000.0,
        'unidad': 'U/L',
        'descripcion': 'Transaminasa glutámico pirúvica (ALT)',
        'interpretacion_alto': 'Daño hepático - más específico que TGO'
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_hepatica',
        'parametro': 'bilirrubina_total',
        'valor_min': 0.1,
        'valor_max': 1.2,
        'critico_alto': 12.0,
        'unidad': 'mg/dL',
        'descripcion': 'Pigmento producto de degradación de hemoglobina',
        'interpretacion_alto': 'Ictericia - puede indicar enfermedad hepática o hemólisis'
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_hepatica',
        'parametro': 'fosfatasa_alcalina',
        'valor_min': 30.0,
        'valor_max': 120.0,
        'unidad': 'U/L',
        'descripcion': 'Enzima presente en hígado y hueso',
        'interpretacion_alto': 'Puede indicar enfermedad hepática, ósea o biliar'
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_hepatica',
        'parametro': 'albumina',
        'valor_min': 3.5,
        'valor_max': 5.0,
        'critico_bajo': 2.0,
        'unidad': 'g/dL',
        'descripcion': 'Principal proteína producida por el hígado',
        'interpretacion_bajo': 'Puede indicar enfermedad hepática, renal o desnutrición'
    },
    {
        'area': 'quimica_clinica',
        'tipo_prueba': 'funcion_hepatica',
        'parametro': 'proteinas_totales',
        'valor_min': 6.0,
        'valor_max': 8.3,
        'unidad': 'g/dL',
        'descripcion': 'Suma de albúmina y globulinas'
    },
]

RANGOS_INMUNOLOGIA = [
    {
        'area': 'inmunologia',
        'tipo_prueba': 'marcadores_inflamatorios',
        'parametro': 'proteina_c_reactiva',
        'valor_min': 0.0,
        'valor_max': 0.5,
        'critico_alto': 10.0,
        'unidad': 'mg/dL',
        'descripcion': 'Marcador de inflamación aguda',
        'interpretacion_alto': 'Inflamación activa - infección, trauma o enfermedad autoinmune'
    },
]


async def inicializar_rangos():
    """Inicializa rangos de referencia en la base de datos"""
    print("="*80)
    print("🔬 INICIALIZACIÓN DE RANGOS DE REFERENCIA DE LABORATORIO")
    print("="*80)
    print()
    
    todos_rangos = RANGOS_HEMATOLOGIA + RANGOS_QUIMICA_CLINICA + RANGOS_INMUNOLOGIA
    
    async with AsyncSessionLocal() as session:
        try:
            print(f"📊 Insertando {len(todos_rangos)} rangos de referencia...")
            print()
            
            for rango_data in todos_rangos:
                rango = RangoReferencia(**rango_data)
                session.add(rango)
                
                print(f"  ✅ {rango_data['area']} - {rango_data['parametro']}")
            
            await session.commit()
            
            print()
            print("="*80)
            print("✅ RANGOS DE REFERENCIA INICIALIZADOS CORRECTAMENTE")
            print("="*80)
            print()
            print("📋 Resumen:")
            print(f"  • Hematología: {len(RANGOS_HEMATOLOGIA)} rangos")
            print(f"  • Química Clínica: {len(RANGOS_QUIMICA_CLINICA)} rangos")
            print(f"  • Inmunología: {len(RANGOS_INMUNOLOGIA)} rangos")
            print(f"  • Total: {len(todos_rangos)} rangos")
            print()
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(inicializar_rangos())
