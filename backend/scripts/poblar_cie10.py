"""
Script para poblar la base de datos con códigos CIE-10 comunes
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_maker
from app.models.cie10 import CIE10


# Códigos CIE-10 más comunes por categoría
CODIGOS_CIE10_COMUNES = [
    # Enfermedades infecciosas
    {
        "codigo": "A00.0",
        "descripcion": "Cólera debido a Vibrio cholerae 01, biotipo cholerae",
        "categoria": "Enfermedades infecciosas intestinales",
        "keywords": "colera, diarrea, vibrio",
    },
    {
        "codigo": "A09",
        "descripcion": "Diarrea y gastroenteritis de presunto origen infeccioso",
        "categoria": "Enfermedades infecciosas intestinales",
        "keywords": "diarrea, gastroenteritis, infeccion intestinal",
    },
    {
        "codigo": "A15.0",
        "descripcion": "Tuberculosis del pulmón, confirmada por hallazgo microscópico",
        "categoria": "Tuberculosis",
        "keywords": "tuberculosis, pulmonar, tos, tb",
    },
    {
        "codigo": "B34.9",
        "descripcion": "Infección viral, no especificada",
        "categoria": "Otras enfermedades virales",
        "keywords": "virus, viral, infeccion",
    },
    # Neoplasias
    {
        "codigo": "C50.9",
        "descripcion": "Tumor maligno de la mama, parte no especificada",
        "categoria": "Tumores malignos",
        "keywords": "cancer mama, tumor maligno, seno",
    },
    {
        "codigo": "C61",
        "descripcion": "Tumor maligno de la próstata",
        "categoria": "Tumores malignos",
        "keywords": "cancer prostata, tumor maligno",
    },
    {
        "codigo": "C34.9",
        "descripcion": "Tumor maligno de los bronquios o del pulmón, parte no especificada",
        "categoria": "Tumores malignos",
        "keywords": "cancer pulmon, tumor maligno",
    },
    # Enfermedades endocrinas
    {
        "codigo": "E10.9",
        "descripcion": "Diabetes mellitus insulinodependiente, sin mención de complicación",
        "categoria": "Diabetes mellitus",
        "keywords": "diabetes tipo 1, insulina, glucosa",
    },
    {
        "codigo": "E11.9",
        "descripcion": "Diabetes mellitus no insulinodependiente, sin mención de complicación",
        "categoria": "Diabetes mellitus",
        "keywords": "diabetes tipo 2, glucosa, azucar",
    },
    {
        "codigo": "E66.9",
        "descripcion": "Obesidad, no especificada",
        "categoria": "Obesidad",
        "keywords": "obesidad, sobrepeso, imc",
    },
    {
        "codigo": "E78.5",
        "descripcion": "Hiperlipidemia, no especificada",
        "categoria": "Trastornos del metabolismo",
        "keywords": "colesterol alto, trigliceridos, lipidos",
    },
    # Trastornos mentales
    {
        "codigo": "F32.9",
        "descripcion": "Episodio depresivo, no especificado",
        "categoria": "Trastornos del humor",
        "keywords": "depresion, tristeza, animo bajo",
    },
    {
        "codigo": "F41.1",
        "descripcion": "Trastorno de ansiedad generalizada",
        "categoria": "Trastornos de ansiedad",
        "keywords": "ansiedad, nerviosismo, preocupacion",
    },
    {
        "codigo": "F10.2",
        "descripcion": "Trastornos mentales y del comportamiento debidos al uso de alcohol, síndrome de dependencia",
        "categoria": "Trastornos por uso de sustancias",
        "keywords": "alcoholismo, dependencia alcohol",
    },
    # Sistema nervioso
    {
        "codigo": "G40.9",
        "descripcion": "Epilepsia, tipo no especificado",
        "categoria": "Epilepsia",
        "keywords": "epilepsia, convulsiones, crisis",
    },
    {
        "codigo": "G43.9",
        "descripcion": "Migraña, no especificada",
        "categoria": "Migraña",
        "keywords": "migrana, jaqueca, dolor cabeza",
    },
    {
        "codigo": "G47.0",
        "descripcion": "Trastornos del inicio y del mantenimiento del sueño [insomnio]",
        "categoria": "Trastornos del sueño",
        "keywords": "insomnio, no dormir, sueno",
    },
    # Sistema circulatorio
    {
        "codigo": "I10",
        "descripcion": "Hipertensión esencial (primaria)",
        "categoria": "Enfermedades hipertensivas",
        "keywords": "hipertension, presion alta, hta",
    },
    {
        "codigo": "I20.9",
        "descripcion": "Angina de pecho, no especificada",
        "categoria": "Cardiopatía isquémica",
        "keywords": "angina, dolor pecho, corazon",
    },
    {
        "codigo": "I21.9",
        "descripcion": "Infarto agudo del miocardio, sin otra especificación",
        "categoria": "Cardiopatía isquémica",
        "keywords": "infarto, iam, ataque cardiaco",
    },
    {
        "codigo": "I50.9",
        "descripcion": "Insuficiencia cardíaca, no especificada",
        "categoria": "Insuficiencia cardíaca",
        "keywords": "insuficiencia cardiaca, falla corazon",
    },
    {
        "codigo": "I63.9",
        "descripcion": "Infarto cerebral, no especificado",
        "categoria": "Enfermedades cerebrovasculares",
        "keywords": "derrame cerebral, ictus, avc",
    },
    # Sistema respiratorio
    {
        "codigo": "J00",
        "descripcion": "Rinofaringitis aguda [resfriado común]",
        "categoria": "Infecciones respiratorias agudas",
        "keywords": "resfriado, gripe, catarro",
    },
    {
        "codigo": "J02.9",
        "descripcion": "Faringitis aguda, no especificada",
        "categoria": "Infecciones respiratorias agudas",
        "keywords": "faringitis, dolor garganta",
    },
    {
        "codigo": "J06.9",
        "descripcion": "Infección aguda de las vías respiratorias superiores, no especificada",
        "categoria": "Infecciones respiratorias agudas",
        "keywords": "infeccion respiratoria, vias altas",
    },
    {
        "codigo": "J18.9",
        "descripcion": "Neumonía, no especificada",
        "categoria": "Neumonía",
        "keywords": "neumonia, pulmones, infeccion pulmonar",
    },
    {
        "codigo": "J20.9",
        "descripcion": "Bronquitis aguda, no especificada",
        "categoria": "Bronquitis",
        "keywords": "bronquitis, tos, bronquios",
    },
    {
        "codigo": "J44.9",
        "descripcion": "Enfermedad pulmonar obstructiva crónica, no especificada",
        "categoria": "EPOC",
        "keywords": "epoc, enfermedad pulmonar, cronica",
    },
    {
        "codigo": "J45.9",
        "descripcion": "Asma, no especificada",
        "categoria": "Asma",
        "keywords": "asma, broncoespasmo, sibilancias",
    },
    # Sistema digestivo
    {
        "codigo": "K21.9",
        "descripcion": "Enfermedad del reflujo gastroesofágico sin esofagitis",
        "categoria": "Enfermedades del esófago",
        "keywords": "reflujo, acidez, gastrico",
    },
    {
        "codigo": "K29.7",
        "descripcion": "Gastritis, no especificada",
        "categoria": "Gastritis",
        "keywords": "gastritis, estomago, dolor abdominal",
    },
    {
        "codigo": "K30",
        "descripcion": "Dispepsia",
        "categoria": "Dispepsia",
        "keywords": "dispepsia, indigestion, mala digestion",
    },
    {
        "codigo": "K80.2",
        "descripcion": "Cálculo de la vesícula biliar sin colecistitis",
        "categoria": "Colelitiasis",
        "keywords": "piedras vesicula, calculo biliar, colelitiasis",
    },
    # Sistema genitourinario
    {
        "codigo": "N18.9",
        "descripcion": "Enfermedad renal crónica, no especificada",
        "categoria": "Insuficiencia renal",
        "keywords": "insuficiencia renal, riñon, cronica",
    },
    {
        "codigo": "N39.0",
        "descripcion": "Infección de vías urinarias, sitio no especificado",
        "categoria": "Infecciones urinarias",
        "keywords": "infeccion urinaria, cistitis, itu",
    },
    {
        "codigo": "N40",
        "descripcion": "Hiperplasia de la próstata",
        "categoria": "Enfermedades de la próstata",
        "keywords": "prostata crecida, hiperplasia prostatica",
    },
    # Embarazo y parto
    {
        "codigo": "O80",
        "descripcion": "Parto único espontáneo",
        "categoria": "Parto",
        "keywords": "parto normal, nacimiento",
    },
    {
        "codigo": "O82",
        "descripcion": "Parto único por cesárea",
        "categoria": "Parto",
        "keywords": "cesarea, parto",
    },
    # Lesiones y traumatismos
    {
        "codigo": "S06.9",
        "descripcion": "Traumatismo intracraneal, no especificado",
        "categoria": "Traumatismos de la cabeza",
        "keywords": "traumatismo craneal, golpe cabeza",
    },
    {
        "codigo": "S52.5",
        "descripcion": "Fractura de la extremidad distal del radio",
        "categoria": "Fracturas",
        "keywords": "fractura radio, muneca, antebrazo",
    },
    {
        "codigo": "S72.0",
        "descripcion": "Fractura del cuello del fémur",
        "categoria": "Fracturas",
        "keywords": "fractura cadera, femur, cuello femoral",
    },
    {
        "codigo": "T14.9",
        "descripcion": "Traumatismo, no especificado",
        "categoria": "Traumatismos",
        "keywords": "trauma, lesion, golpe",
    },
    # Síntomas y signos
    {
        "codigo": "R05",
        "descripcion": "Tos",
        "categoria": "Síntomas respiratorios",
        "keywords": "tos, toser",
    },
    {
        "codigo": "R06.0",
        "descripcion": "Disnea",
        "categoria": "Síntomas respiratorios",
        "keywords": "disnea, falta aire, dificultad respirar",
    },
    {
        "codigo": "R07.4",
        "descripcion": "Dolor torácico, no especificado",
        "categoria": "Síntomas circulatorios",
        "keywords": "dolor pecho, toracico",
    },
    {
        "codigo": "R10.4",
        "descripcion": "Otros dolores abdominales y los no especificados",
        "categoria": "Síntomas digestivos",
        "keywords": "dolor abdominal, dolor estomago",
    },
    {
        "codigo": "R50.9",
        "descripcion": "Fiebre, no especificada",
        "categoria": "Síntomas generales",
        "keywords": "fiebre, temperatura, calentura",
    },
    {
        "codigo": "R51",
        "descripcion": "Cefalea",
        "categoria": "Síntomas neurológicos",
        "keywords": "cefalea, dolor cabeza",
    },
    {
        "codigo": "R53",
        "descripcion": "Malestar y fatiga",
        "categoria": "Síntomas generales",
        "keywords": "cansancio, fatiga, debilidad",
    },
    # Factores que influyen en el estado de salud
    {
        "codigo": "Z00.0",
        "descripcion": "Examen médico general",
        "categoria": "Exámenes",
        "keywords": "chequeo, revision, examen general",
    },
    {
        "codigo": "Z23",
        "descripcion": "Necesidad de inmunización contra enfermedad bacteriana única",
        "categoria": "Vacunación",
        "keywords": "vacuna, vacunacion, inmunizacion",
    },
]


async def poblar_cie10():
    """Pobla la base de datos con códigos CIE-10"""
    async with async_session_maker() as session:
        try:
            print("🔄 Poblando base de datos con códigos CIE-10...")

            for codigo_data in CODIGOS_CIE10_COMUNES:
                # Verificar si ya existe
                from sqlalchemy import select

                result = await session.execute(
                    select(CIE10).where(CIE10.codigo == codigo_data["codigo"])
                )
                existe = result.scalar_one_or_none()

                if not existe:
                    cie10 = CIE10(**codigo_data)
                    session.add(cie10)
                    print(
                        f"  ✓ Agregado: {codigo_data['codigo']} - {codigo_data['descripcion'][:50]}..."
                    )
                else:
                    print(f"  ⊙ Ya existe: {codigo_data['codigo']}")

            await session.commit()
            print(
                f"\n✅ Base de datos poblada con {len(CODIGOS_CIE10_COMUNES)} códigos CIE-10"
            )

        except Exception as e:
            await session.rollback()
            print(f"❌ Error poblando base de datos: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(poblar_cie10())
