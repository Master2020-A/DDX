"""
Script para generar datos de prueba completos para Historia Clínica Pediátrica
"""
import asyncio
import sys
from datetime import date, datetime, timedelta
from random import choice, randint, uniform
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.historia_clinica import (
    HistoriaClinicaPediatrica, 
    ExploracionFisica, 
    AntecedentesNoPatologicos
)
from app.models.paciente import Paciente
from app.models.consulta import Consulta
from app.models.diagnostico import Diagnostico
from app.models.tratamiento import Tratamiento, Prescripcion
from app.models.expediente import ExpedienteClinico
from app.models.usuario import Usuario


# Datos de ejemplo realistas
NOMBRES_MADRE = ["María", "Ana", "Laura", "Carmen", "Rosa", "Patricia", "Guadalupe", "Leticia"]
NOMBRES_PADRE = ["José", "Juan", "Carlos", "Miguel", "Antonio", "Luis", "Fernando", "Roberto"]
OCUPACIONES = ["Ama de casa", "Empleada", "Comerciante", "Profesionista", "Docente", "Enfermera"]
ESCOLARIDADES = ["Primaria", "Secundaria", "Preparatoria", "Universidad", "Posgrado"]
PARENTESCOS = ["Madre", "Padre", "Abuela", "Tía", "Tutor legal"]

PADECIMIENTOS_ACTUALES = [
    """El paciente presenta desde hace 3 días cuadro de fiebre de 38.5°C, predominantemente vespertina, 
    acompañada de tos productiva con expectoración blanquecina. Refiere también rinorrea hialina y 
    estornudos frecuentes. No ha presentado dificultad respiratoria ni cianosis. Ha recibido tratamiento 
    con paracetamol sin mejoría significativa.""",
    
    """Inicia padecimiento actual hace 2 días con evacuaciones líquidas en número de 6-8 por día, 
    sin moco ni sangre, acompañadas de dolor abdominal tipo cólico. Presenta náuseas y vómitos 
    alimentarios en 3 ocasiones. Refiere disminución del apetito. Ha recibido vida suero oral 
    con regular tolerancia.""",
    
    """Paciente refiere desde hace 1 semana dolor de garganta que se intensifica con la deglución, 
    acompañado de fiebre de hasta 39°C. Presenta adenopatías cervicales dolorosas bilaterales. 
    Se agrega tos seca no productiva. Ha recibido tratamiento sintomático sin mejoría.""",
    
    """Madre refiere que el paciente presenta desde hace 5 días erupciones en piel que iniciaron 
    en cara y se generalizaron a tronco y extremidades. Las lesiones son maculopapulares, no pruriginosas. 
    Acompañado de fiebre de 38°C los primeros 3 días. Antecedente de contacto con familiar con varicela."""
]

DIAGNOSTICOS_PRINCIPALES = [
    "Faringoamigdalitis aguda",
    "Gastroenteritis aguda",
    "Rinofaringitis aguda (Resfriado común)",
    "Bronquitis aguda",
    "Otitis media aguda",
    "Exantema viral",
    "Parasitosis intestinal",
    "Dermatitis atópica"
]

TRATAMIENTOS = [
    """1. Amoxicilina 500mg VO cada 8 horas por 7 días
2. Paracetamol 250mg VO cada 6 horas en caso de fiebre (>38°C)
3. Abundantes líquidos orales
4. Reposo relativo""",
    
    """1. Vida Suero Oral: 1 sobre en 1 litro de agua, tomar frecuentemente
2. Trimetoprima/Sulfametoxazol suspensión 5ml VO cada 12 horas por 5 días
3. Probióticos: 1 sobre al día por 7 días
4. Dieta blanda astringente""",
    
    """1. Loratadina jarabe 5ml VO cada 24 horas por 7 días
2. Crema de hidrocortisona 1% aplicar en lesiones 2 veces al día
3. Baños con avena coloidal
4. Evitar rascado de lesiones"""
]

RECOMENDACIONES = [
    """- Vigilar datos de alarma: fiebre persistente >3 días, dificultad respiratoria, rechazo al alimento
- Mantener hidratación adecuada
- Lavado de manos frecuente
- Aislamiento respiratorio mientras persistan síntomas
- Acudir a urgencias si presenta datos de alarma""",
    
    """- Continuar con hidratación oral abundante
- Vigilar datos de deshidratación: llanto sin lágrimas, ojos hundidos, boca seca
- Llevar control de evacuaciones y vómitos
- Evitar alimentos irritantes, lácteos y grasas
- Regresar a consulta si no hay mejoría en 48 horas""",
    
    """- Mantener piel hidratada con cremas emolientes
- Evitar baños con agua muy caliente
- Usar ropa de algodón suave
- Identificar y evitar desencadenantes (polvo, pelo de animales)
- Cortar uñas para evitar lesiones por rascado"""
]


async def crear_paciente_prueba(session, index):
    """Crear un paciente de prueba"""
    nombres = ["Sofía", "Mateo", "Valentina", "Santiago", "Isabella", "Sebastián", "Camila", "Diego"]
    apellidos = ["García", "Rodríguez", "Martínez", "López", "González", "Pérez", "Sánchez", "Ramírez"]
    
    nombre = f"{choice(nombres)} {choice(apellidos)} {choice(apellidos)}"
    
    # Fecha de nacimiento: entre 1 y 15 años
    edad_años = randint(1, 15)
    fecha_nac = date.today() - timedelta(days=edad_años*365 + randint(0, 364))
    
    paciente = Paciente(
        numero_expediente=f"EXP-{10000 + index}",
        nombre_completo=nombre,
        fecha_nacimiento=fecha_nac,
        genero=choice(["masculino", "femenino"]),
        tipo_sangre=choice(["O+", "A+", "B+", "AB+", "O-", "A-"]),
        telefono=f"55{randint(1000, 9999)}{randint(1000, 9999)}",
        email=f"paciente{index}@email.com",
        direccion=f"Calle {randint(1, 100)}, Col. Ejemplo, CDMX",
        contacto_emergencia_nombre=f"{choice(NOMBRES_MADRE)} {choice(apellidos)}",
        contacto_emergencia_telefono=f"55{randint(1000, 9999)}{randint(1000, 9999)}",
        alergias=choice([[], ["Penicilina"], ["Polen"], ["Penicilina", "Mariscos"], []])
    )
    
    session.add(paciente)
    await session.flush()
    return paciente


async def crear_historia_completa(session, paciente, index):
    """Crear una historia clínica completa con todos los datos"""
    
    # Historia Clínica Principal
    historia = HistoriaClinicaPediatrica(
        paciente_id=paciente.id,
        fecha=date.today() - timedelta(days=randint(0, 180)),
        numero_afiliacion=f"IMSS-{randint(100000, 999999)}",
        
        # Datos generales
        informante_parentesco=choice(PARENTESCOS),
        informante_edad=randint(25, 45),
        escolaridad_paciente=choice(ESCOLARIDADES[:3]) if randint(0, 10) > 3 else None,
        
        # Padecimiento Actual
        padecimiento_actual=choice(PADECIMIENTOS_ACTUALES),
        diagnosticos_previos="Ninguno de importancia" if randint(0, 1) else "Amigdalitis recurrente",
        examenes_previos="Biometría hemática: dentro de parámetros normales\nExamen general de orina: normal",
        terapeutica_previa="Paracetamol 250mg PRN",
        
        # Antecedentes Familiares - Madre
        madre_vive=True if randint(0, 10) > 1 else False,
        madre_edad=randint(25, 45),
        madre_escolaridad=choice(ESCOLARIDADES),
        madre_ocupacion=choice(OCUPACIONES),
        madre_gesta=randint(1, 4),
        madre_parto=randint(1, 3),
        madre_abortos=randint(0, 1),
        madre_cesareas=randint(0, 2),
        madre_toxicomanias="Negadas",
        
        # Antecedentes Familiares - Padre
        padre_vive=True if randint(0, 10) > 1 else False,
        padre_edad=randint(28, 50),
        padre_escolaridad=choice(ESCOLARIDADES),
        padre_ocupacion=choice(["Empleado", "Comerciante", "Obrero", "Profesionista", "Chofer"]),
        padre_toxicomanias="Tabaquismo ocasional" if randint(0, 3) == 0 else "Negadas",
        
        # Hermanos
        hermanos_numero=randint(0, 3),
        hermanos_vivos=randint(0, 3),
        hermanos_muertos=0,
        
        # Padecimientos Heredofamiliares
        heredofam_diabeticos=choice(["Abuela materna", "Abuelo paterno", "Negados"]),
        heredofam_hipertension=choice(["Abuelo materno", "Padre", "Negados"]),
        heredofam_neurologicos="Negados",
        heredofam_cardiopatas="Negados",
        heredofam_nefropatias="Negados",
        heredofam_oncologicos="Negados",
        heredofam_alergicos=choice(["Madre - asma", "Hermano - rinitis", "Negados"]),
        
        contacto_enfermedades_infecciosas="Negado" if randint(0, 2) else "Primo con varicela hace 2 semanas",
        
        # Antecedentes Perinatales
        embarazo_numero=randint(1, 4),
        embarazo_curso_normal=True if randint(0, 3) else False,
        embarazo_causa="Sin complicaciones" if randint(0, 3) else "Amenaza de aborto en primer trimestre",
        gestacion_semanas=randint(37, 41),
        sitio_atencion_parto=choice(["Hospital General", "IMSS", "ISSSTE", "Privado"]),
        parto_eutocico=True if randint(0, 2) else False,
        peso_nacimiento=round(uniform(2.5, 4.0), 2),
        talla_nacimiento=round(uniform(45, 53), 1),
        ruptura_membranas_horas=round(uniform(2, 12), 1),
        anestesia="Bloqueo epidural" if randint(0, 2) == 0 else None,
        apnea_neonatal=False,
        convulsiones_neonatales=False,
        hemorragias_neonatales=False,
        ictericia_neonatal=True if randint(0, 4) == 0 else False,
        cianosis_neonatal=False,
        informacion_adicional_perinatal="APGAR 8/9, llanto y respiración espontáneos",
        
        # Vivienda
        num_cuartos_casa=randint(2, 5),
        num_personas_duermen_casa=randint(3, 7),
        tiene_refrigerador=True,
        tiene_telefono=True,
        tiene_automovil=True if randint(0, 2) else False,
        exposicion_sustancias_toxicas="Negada",
        
        # Personales Patológicos
        personales_patologicos=choice([
            "Sarampión a los 3 años",
            "Varicela a los 5 años",
            "Sin antecedentes patológicos de importancia",
            "Amigdalitis recurrente"
        ])
    )
    
    session.add(historia)
    await session.flush()
    
    # Exploración Física
    edad_meses = (date.today() - paciente.fecha_nacimiento).days / 30
    
    exploracion = ExploracionFisica(
        historia_clinica_id=historia.id,
        
        # Signos vitales y medidas
        peso=round(uniform(10, 45), 1),
        talla=round(uniform(75, 165), 1),
        perimetro_cefalico=round(uniform(45, 55), 1) if edad_meses < 36 else None,
        perimetro_braquial=round(uniform(14, 22), 1),
        frecuencia_cardiaca=randint(70, 120),
        frecuencia_respiratoria=randint(18, 30),
        temperatura=round(uniform(36.5, 37.8), 1),
        tension_arterial=f"{randint(90, 110)}/{randint(60, 75)}",
        
        # Examen físico
        piel_faneras="Hidratada, elástica, sin lesiones aparentes. Llenado capilar <2 segundos.",
        cabeza="Normocéfala, sin presencia de exostosis ni hundimientos.",
        ojos="Pupilas isocóricas, normorreflécticas. Conjuntivas rosadas, escleras blancas.",
        oidos="Conductos auditivos externos permeables. Membranas timpánicas íntegras, translúcidas.",
        boca_faringe=choice([
            "Mucosa oral hidratada. Faringe hiperémica con exudado purulento en amígdalas.",
            "Mucosa oral y faríngea sin alteraciones. Amígdalas no hipertróficas.",
            "Faringe levemente hiperémica. Amígdalas grado II sin exudado."
        ]),
        cuello="Cilíndrico, simétrico, sin adenopatías palpables.",
        torax_ap_respiratorio="Tórax simétrico, murmullo vesicular audible en ambos campos pulmonares, sin estertores.",
        torax_ap_cardiovascular="Ruidos cardiacos rítmicos, de buen tono e intensidad, sin soplos audibles.",
        abdomen="Blando, depresible, no doloroso a la palpación. Peristalsis presente. No visceromegalias.",
        extremidades="Íntegras, simétricas, pulsos periféricos presentes y simétricos. Sin edema.",
        genitales="Acordes a edad y sexo, sin alteraciones.",
        neurologico="Consciente, orientado, reactivo. Reflejos osteotendinosos normales. Marcha normal.",
        columna_vertebral="Sin desviaciones aparentes. Movilidad conservada.",
        
        # Médicos
        medico_realizo_nombre=choice(["Dr. Pedro Ramírez", "Dra. Ana López", "Dr. Carlos Méndez"]),
        medico_realizo_firma="Firma electrónica validada",
        medico_reviso_nombre=choice(["Dr. Miguel Ángel Torres", "Dra. Patricia Vega"]),
        medico_reviso_firma="Firma electrónica validada"
    )
    
    session.add(exploracion)
    
    # Antecedentes No Patológicos
    antecedentes = AntecedentesNoPatologicos(
        historia_clinica_id=historia.id,
        
        # Alimentación
        pecho_materno_duracion_meses=randint(3, 24),
        ablactacion_meses=randint(4, 8),
        destete_meses=randint(12, 30),
        alimentacion_actual={
            "carne": randint(3, 7),
            "leche": 7,
            "huevo": randint(2, 5),
            "frutas": randint(5, 7),
            "verduras": randint(4, 7),
            "cereales": 7,
            "leguminosas": randint(2, 4)
        },
        
        # Inmunizaciones
        inmunizaciones={
            "BCG": [{"dosis": 1, "edad_meses": 0, "fecha": "2020-01-15"}],
            "Hepatitis_B": [
                {"dosis": 1, "edad_meses": 0, "fecha": "2020-01-15"},
                {"dosis": 2, "edad_meses": 2, "fecha": "2020-03-15"},
                {"dosis": 3, "edad_meses": 6, "fecha": "2020-07-15"}
            ],
            "Pentavalente": [
                {"dosis": 1, "edad_meses": 2, "fecha": "2020-03-15"},
                {"dosis": 2, "edad_meses": 4, "fecha": "2020-05-15"},
                {"dosis": 3, "edad_meses": 6, "fecha": "2020-07-15"},
                {"dosis": 4, "edad_meses": 18, "fecha": "2021-07-15"}
            ],
            "Rotavirus": [
                {"dosis": 1, "edad_meses": 2, "fecha": "2020-03-15"},
                {"dosis": 2, "edad_meses": 4, "fecha": "2020-05-15"}
            ],
            "Neumococo": [
                {"dosis": 1, "edad_meses": 2, "fecha": "2020-03-15"},
                {"dosis": 2, "edad_meses": 4, "fecha": "2020-05-15"},
                {"dosis": 3, "edad_meses": 12, "fecha": "2021-01-15"}
            ],
            "SRP": [
                {"dosis": 1, "edad_meses": 12, "fecha": "2021-01-15"},
                {"dosis": 2, "edad_meses": 72, "fecha": "2026-01-15"}
            ]
        },
        
        # Desarrollo Psicomotor
        desarrollo_siguio_objetos_meses=randint(1, 3),
        desarrollo_sonrio_meses=randint(1, 3),
        desarrollo_sostuvo_cabeza_meses=randint(2, 4),
        desarrollo_se_sento_meses=randint(5, 8),
        desarrollo_camino_meses=randint(10, 16),
        desarrollo_control_esfinteres_vesical_meses=randint(24, 36),
        desarrollo_control_esfinteres_anal_meses=randint(24, 36),
        escolaridad_actual=choice(["Kinder", "Primaria", "Secundaria", "No aplica"]),
        años_escolares_reprobados=0,
        datos_anormales_desarrollo="Desarrollo psicomotor acorde a la edad",
        
        # Desarrollo Puberal (solo si aplica)
        inicio_telarca_edad=randint(9, 13) if paciente.genero == "femenino" and edad_meses > 108 else None,
        inicio_pubarca_edad=randint(10, 14) if edad_meses > 120 else None,
        
        # Habitación
        eliminacion_excretas_fecalismo=False,
        eliminacion_excretas_letrina=False,
        eliminacion_excretas_tipo_ingles=True,
        agua_intradomiciliaria=True,
        baño_familiar=True,
        baño_comunal=False,
        convivencia_animales=choice(["Perro", "Gato", "Ninguno", "Perro y gato"]),
        piso_casa_tierra=False,
        piso_casa_cemento=True if randint(0, 2) else False,
        piso_casa_recubrimiento="Loseta" if randint(0, 2) else "Cemento pulido"
    )
    
    session.add(antecedentes)
    await session.flush()
    
    return historia


async def crear_consulta_completa(session, paciente, historia_id, medico_id, index):
    """Crear una consulta completa con diagnóstico y tratamiento"""
    
    # Consulta
    motivo = choice([
        "Control de niño sano",
        "Fiebre y tos",
        "Dolor abdominal",
        "Lesiones en piel",
        "Dolor de garganta",
        "Diarrea"
    ])
    
    sintomas_lista = choice([
        ["Fiebre", "Tos productiva", "Rinorrea"],
        ["Dolor abdominal", "Evacuaciones líquidas", "Vómito"],
        ["Odinofagia", "Fiebre", "Adenopatías cervicales"],
        ["Erupciones en piel", "Fiebre", "Malestar general"]
    ])
    
    consulta = Consulta(
        paciente_id=paciente.id,
        medico_id=medico_id,
        fecha_hora=datetime.now() - timedelta(days=randint(0, 30)),
        motivo_consulta=motivo,
        sintomas=sintomas_lista,
        tipo_consulta=choice(["primera_vez", "seguimiento"]),
        estado="completada"
    )
    
    session.add(consulta)
    await session.flush()
    
    # Expediente Clínico (signos vitales, exploración física, notas)
    expediente = ExpedienteClinico(
        paciente_id=paciente.id,
        consulta_id=consulta.id,
        signos_vitales={
            "temperatura": round(uniform(36.5, 38.5), 1),
            "presion_arterial": f"{randint(90, 110)}/{randint(60, 75)}",
            "frecuencia_cardiaca": randint(70, 120),
            "frecuencia_respiratoria": randint(18, 30),
            "saturacion_oxigeno": randint(95, 100),
            "peso": round(uniform(10, 45), 1),
            "talla": round(uniform(75, 165), 1)
        },
        exploracion_fisica=choice([
            "Faringe hiperémica, amígdalas con exudado purulento bilateral. Adenopatías cervicales dolorosas.",
            "Abdomen blando, depresible, peristalsis aumentada. Sin datos de irritación peritoneal.",
            "Lesiones maculopapulares en cara, tronco y extremidades. No pruriginosas.",
            "Campos pulmonares con estertores crepitantes bibasales. No sibilancias."
        ]),
        notas=choice([
            "Paciente en regulares condiciones generales. Alerta, hidratado.",
            "Paciente orientado, cooperador. Buen estado de hidratación.",
            "Se explican datos de alarma y signos de deshidratación a familiar.",
            "Se enfatiza importancia de completar tratamiento antibiótico."
        ])
    )
    
    session.add(expediente)
    await session.flush()
    
    # Diagnóstico
    diagnostico_texto = choice(DIAGNOSTICOS_PRINCIPALES)
    diagnostico = Diagnostico(
        consulta_id=consulta.id,
        medico_id=medico_id,
        descripcion=diagnostico_texto,
        tipo=choice(["diagnostico_presuntivo", "diagnostico_confirmado"]),
        codigo_cie10=choice(["J02.9", "A09", "J00", "J20.9", "H66.9", "B09", "B82.9", "L20.9"]),
        confianza_nivel=choice(["medio", "alto", "confirmado"]),
        justificacion=f"Diagnóstico basado en cuadro clínico y exploración física. {choice(['Requiere seguimiento.', 'Evolución favorable esperada.', 'Vigilar complicaciones.'])}",
        estado="activo"
    )
    
    session.add(diagnostico)
    await session.flush()
    
    # Tratamiento
    tratamiento_texto = choice(TRATAMIENTOS)
    recomendacion_texto = choice(RECOMENDACIONES)
    duracion = randint(5, 14)
    
    tratamiento = Tratamiento(
        consulta_id=consulta.id,
        diagnostico_id=diagnostico.id,
        tipo_tratamiento="farmacologico",
        descripcion=tratamiento_texto,
        objetivo="Control de síntomas y resolución del cuadro clínico",
        duracion_dias=duracion,
        fecha_inicio=consulta.fecha_hora.date(),
        fecha_fin=(consulta.fecha_hora + timedelta(days=duracion)).date(),
        estado="activo",
        prescrito_por=medico_id,
        notas=recomendacion_texto
    )
    
    session.add(tratamiento)
    await session.flush()
    
    # Prescripción (medicamento específico)
    medicamento_principal = tratamiento_texto.split('\n')[0].replace('1. ', '').split(' ')[0]
    prescripcion = Prescripcion(
        tratamiento_id=tratamiento.id,
        medicamento=medicamento_principal,
        dosis=tratamiento_texto.split('\n')[0].replace('1. ', ''),
        frecuencia="Según indicación médica",
        via_administracion="Oral",
        duracion_dias=duracion,
        instrucciones_especiales=recomendacion_texto[:200]
    )
    
    session.add(prescripcion)
    await session.commit()
    
    return consulta, expediente, diagnostico, tratamiento, prescripcion


async def generar_datos_prueba(cantidad=5):
    """Generar datos de prueba completos"""
    print("\n" + "="*70)
    print(f"🏥 GENERANDO {cantidad} HISTORIAS CLÍNICAS DE PRUEBA")
    print("="*70 + "\n")
    
    async with AsyncSessionLocal() as session:
        try:
            # Obtener un médico para asignar a las consultas
            result = await session.execute(select(Usuario).where(Usuario.rol == "medico").limit(1))
            medico = result.scalar_one_or_none()
            
            if not medico:
                # Si no hay médicos, usar cualquier usuario
                result = await session.execute(select(Usuario).limit(1))
                medico = result.scalar_one_or_none()
            
            if not medico:
                print("⚠️  No hay usuarios en la base de datos. Creando sin consultas...")
                medico_id = None
            else:
                medico_id = medico.id
                print(f"👨‍⚕️ Usando médico: {medico.nombre_completo if hasattr(medico, 'nombre_completo') else medico.email}")
            
            # Verificar pacientes existentes
            result = await session.execute(select(Paciente))
            pacientes_existentes = result.scalars().all()
            
            print(f"📊 Pacientes existentes en BD: {len(pacientes_existentes)}")
            
            historias_creadas = 0
            
            # Crear historias para pacientes existentes primero
            for i, paciente in enumerate(pacientes_existentes[:cantidad], 1):
                print(f"\n[{i}/{min(len(pacientes_existentes), cantidad)}] Creando historia para: {paciente.nombre_completo}")
                
                # Verificar si ya tiene historias
                result = await session.execute(
                    select(HistoriaClinicaPediatrica).where(
                        HistoriaClinicaPediatrica.paciente_id == paciente.id
                    )
                )
                historias_existentes = result.scalars().all()
                
                if len(historias_existentes) >= 2:
                    print(f"   ⚠️  Ya tiene {len(historias_existentes)} historias, omitiendo...")
                    continue
                
                historia = await crear_historia_completa(session, paciente, historias_creadas)
                historias_creadas += 1
                
                print(f"   ✅ Historia creada: {historia.id}")
                print(f"   📋 Número de afiliación: {historia.numero_afiliacion}")
                print(f"   📅 Fecha: {historia.fecha}")
                
                # Crear 1-2 consultas con diagnósticos y tratamientos (solo si hay médico)
                if medico_id:
                    num_consultas = randint(1, 2)
                    for j in range(num_consultas):
                        consulta, expediente, diag, trat, presc = await crear_consulta_completa(session, paciente, historia.id, medico_id, j)
                        print(f"   📝 Consulta {j+1}: {diag.descripcion}")
            
            # Si necesitamos más, crear nuevos pacientes
            if historias_creadas < cantidad:
                print(f"\n📝 Creando {cantidad - historias_creadas} pacientes nuevos con historias...\n")
                
                for i in range(cantidad - historias_creadas):
                    num = len(pacientes_existentes) + i + 1
                    print(f"[{historias_creadas + i + 1}/{cantidad}] Creando paciente y historia {num}...")
                    
                    paciente = await crear_paciente_prueba(session, num)
                    print(f"   ✅ Paciente creado: {paciente.nombre_completo}")
                    
                    historia = await crear_historia_completa(session, paciente, historias_creadas + i)
                    print(f"   ✅ Historia creada: {historia.numero_afiliacion}")
                    
                    # Crear 1-2 consultas con diagnósticos y tratamientos (solo si hay médico)
                    if medico_id:
                        num_consultas = randint(1, 2)
                        for j in range(num_consultas):
                            consulta, expediente, diag, trat, presc = await crear_consulta_completa(session, paciente, historia.id, medico_id, j)
                            print(f"   📝 Consulta {j+1}: {diag.descripcion}")
                    
                    historias_creadas += 1
            
            print("\n" + "="*70)
            print(f"✅ PROCESO COMPLETADO")
            print("="*70)
            print(f"\n📊 Estadísticas:")
            print(f"   • Historias clínicas creadas: {historias_creadas}")
            print(f"   • Exploraciones físicas: {historias_creadas}")
            print(f"   • Antecedentes completos: {historias_creadas}")
            
            # Contar totales
            result_hist = await session.execute(select(HistoriaClinicaPediatrica))
            total_historias = len(result_hist.scalars().all())
            
            result_cons = await session.execute(select(Consulta))
            total_consultas = len(result_cons.scalars().all())
            
            result_exp = await session.execute(select(ExpedienteClinico))
            total_expedientes = len(result_exp.scalars().all())
            
            result_diag = await session.execute(select(Diagnostico))
            total_diagnosticos = len(result_diag.scalars().all())
            
            result_trat = await session.execute(select(Tratamiento))
            total_tratamientos = len(result_trat.scalars().all())
            
            result_presc = await session.execute(select(Prescripcion))
            total_prescripciones = len(result_presc.scalars().all())
            
            print(f"\n   📈 Total en base de datos:")
            print(f"      • {total_historias} historias clínicas")
            print(f"      • {total_consultas} consultas médicas")
            print(f"      • {total_expedientes} expedientes clínicos")
            print(f"      • {total_diagnosticos} diagnósticos")
            print(f"      • {total_tratamientos} tratamientos")
            print(f"      • {total_prescripciones} prescripciones médicas")
            
            print("\n💡 Ahora puedes:")
            print("   1. Iniciar el backend y frontend")
            print("   2. Acceder a http://localhost:3000")
            print("   3. Ver las historias clínicas con datos completos")
            print("   4. Consultar diagnósticos y tratamientos de cada paciente")
            print("\n" + "="*70 + "\n")
            
            return True
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Función principal"""
    import sys
    
    cantidad = 5
    if len(sys.argv) > 1:
        try:
            cantidad = int(sys.argv[1])
        except:
            print("Uso: python generar_datos_prueba.py [cantidad]")
            cantidad = 5
    
    resultado = await generar_datos_prueba(cantidad)
    return resultado


if __name__ == "__main__":
    try:
        resultado = asyncio.run(main())
        sys.exit(0 if resultado else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
