"""
Script para poblar catálogos iniciales del sistema
"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.catalogos import (
    InstitucionSalud, Parentesco, NivelEscolaridad,
    TipoExamenLaboratorio, SustanciaToxica
)


async def poblar_instituciones():
    """Poblar catálogo de instituciones de salud de México"""
    instituciones = [
        {"nombre": "IMSS - Instituto Mexicano del Seguro Social", "tipo": "Seguridad Social", "nivel_atencion": "Todos los niveles"},
        {"nombre": "ISSSTE - Instituto de Seguridad y Servicios Sociales de los Trabajadores del Estado", "tipo": "Seguridad Social", "nivel_atencion": "Todos los niveles"},
        {"nombre": "SSA - Secretaría de Salud", "tipo": "Pública", "nivel_atencion": "Todos los niveles"},
        {"nombre": "IMSS-Bienestar (antes IMSS-Oportunidades)", "tipo": "Pública", "nivel_atencion": "Primer y Segundo nivel"},
        {"nombre": "SEDENA - Servicios de Salud Militar", "tipo": "Militar", "nivel_atencion": "Todos los niveles"},
        {"nombre": "SEMAR - Servicios de Salud Naval", "tipo": "Militar", "nivel_atencion": "Todos los niveles"},
        {"nombre": "Pemex - Petróleos Mexicanos", "tipo": "Seguridad Social", "nivel_atencion": "Todos los niveles"},
        {"nombre": "Cruz Roja Mexicana", "tipo": "Privada", "nivel_atencion": "Urgencias"},
        {"nombre": "Clínica Particular", "tipo": "Privada", "nivel_atencion": "Variable"},
        {"nombre": "Hospital Privado", "tipo": "Privada", "nivel_atencion": "Todos los niveles"},
        {"nombre": "Centro de Salud Comunitario", "tipo": "Pública", "nivel_atencion": "Primer nivel"},
        {"nombre": "Otro", "tipo": "Otro", "nivel_atencion": "Variable"}
    ]
    
    async with AsyncSessionLocal() as session:
        for inst_data in instituciones:
            institucion = InstitucionSalud(
                nombre=inst_data["nombre"],
                tipo=inst_data["tipo"],
                pais="México",
                nivel_atencion=inst_data["nivel_atencion"]
            )
            session.add(institucion)
        await session.commit()
        print(f"✅ {len(instituciones)} instituciones de salud creadas")


async def poblar_parentescos():
    """Poblar catálogo de parentescos"""
    parentescos = [
        {"nombre": "Madre", "orden": 1},
        {"nombre": "Padre", "orden": 2},
        {"nombre": "Tutor(a) legal", "orden": 3},
        {"nombre": "Abuelo(a) materno(a)", "orden": 4},
        {"nombre": "Abuelo(a) paterno(a)", "orden": 5},
        {"nombre": "Tío(a)", "orden": 6},
        {"nombre": "Hermano(a)", "orden": 7},
        {"nombre": "Hijo(a)", "orden": 8},
        {"nombre": "Amigo(a)", "orden": 9},
        {"nombre": "Vecino(a)", "orden": 10},
        {"nombre": "Otro", "orden": 11}
    ]
    
    async with AsyncSessionLocal() as session:
        for p_data in parentescos:
            parentesco = Parentesco(
                nombre=p_data["nombre"],
                orden=p_data["orden"]
            )
            session.add(parentesco)
        await session.commit()
        print(f"✅ {len(parentescos)} tipos de parentesco creados")


async def poblar_escolaridades():
    """Poblar catálogo de niveles de escolaridad para México"""
    niveles = [
        {"nombre": "Sin escolaridad", "orden": 0},
        {"nombre": "Preescolar", "orden": 1},
        {"nombre": "Primaria incompleta", "orden": 2},
        {"nombre": "Primaria completa", "orden": 3},
        {"nombre": "Secundaria incompleta", "orden": 4},
        {"nombre": "Secundaria completa", "orden": 5},
        {"nombre": "Preparatoria o bachillerato incompleto", "orden": 6},
        {"nombre": "Preparatoria o bachillerato completo", "orden": 7},
        {"nombre": "Técnico o comercial", "orden": 8},
        {"nombre": "Universidad incompleta", "orden": 9},
        {"nombre": "Universidad completa", "orden": 10},
        {"nombre": "Posgrado", "orden": 11}
    ]
    
    async with AsyncSessionLocal() as session:
        for n_data in niveles:
            nivel = NivelEscolaridad(
                nombre=n_data["nombre"],
                pais="México",
                orden=n_data["orden"]
            )
            session.add(nivel)
        await session.commit()
        print(f"✅ {len(niveles)} niveles de escolaridad creados")


async def poblar_examenes():
    """Poblar catálogo de exámenes de laboratorio"""
    examenes = [
        {"nombre": "Biometría hemática completa", "categoria": "Laboratorio", "orden": 1},
        {"nombre": "Química sanguínea", "categoria": "Laboratorio", "orden": 2},
        {"nombre": "Examen general de orina (EGO)", "categoria": "Laboratorio", "orden": 3},
        {"nombre": "Urocultivo", "categoria": "Laboratorio", "orden": 4},
        {"nombre": "Coproparasitoscópico", "categoria": "Laboratorio", "orden": 5},
        {"nombre": "Coprocultivo", "categoria": "Laboratorio", "orden": 6},
        {"nombre": "Perfil de lípidos", "categoria": "Laboratorio", "orden": 7},
        {"nombre": "Perfil tiroideo", "categoria": "Laboratorio", "orden": 8},
        {"nombre": "Hemoglobina glucosilada (HbA1c)", "categoria": "Laboratorio", "orden": 9},
        {"nombre": "Pruebas de función hepática", "categoria": "Laboratorio", "orden": 10},
        {"nombre": "Pruebas de función renal", "categoria": "Laboratorio", "orden": 11},
        {"nombre": "Tiempos de coagulación", "categoria": "Laboratorio", "orden": 12},
        {"nombre": "Grupo sanguíneo y Rh", "categoria": "Laboratorio", "orden": 13},
        {"nombre": "Radiografía de tórax", "categoria": "Gabinete", "orden": 14},
        {"nombre": "Ultrasonido", "categoria": "Gabinete", "orden": 15},
        {"nombre": "Tomografía computarizada", "categoria": "Gabinete", "orden": 16},
        {"nombre": "Resonancia magnética", "categoria": "Gabinete", "orden": 17},
        {"nombre": "Electrocardiograma", "categoria": "Gabinete", "orden": 18},
        {"nombre": "Ecocardiograma", "categoria": "Gabinete", "orden": 19}
    ]
    
    async with AsyncSessionLocal() as session:
        for e_data in examenes:
            examen = TipoExamenLaboratorio(
                nombre=e_data["nombre"],
                categoria=e_data["categoria"],
                orden=e_data["orden"]
            )
            session.add(examen)
        await session.commit()
        print(f"✅ {len(examenes)} tipos de examen creados")


async def poblar_sustancias():
    """Poblar catálogo de sustancias tóxicas"""
    sustancias = [
        {"nombre": "Tabaco", "categoria": "Legal", "nivel": "Medio", "orden": 1},
        {"nombre": "Alcohol", "categoria": "Legal", "nivel": "Medio", "orden": 2},
        {"nombre": "Cannabis (Marihuana)", "categoria": "Droga", "nivel": "Medio", "orden": 3},
        {"nombre": "Cocaína", "categoria": "Droga", "nivel": "Alto", "orden": 4},
        {"nombre": "Crack", "categoria": "Droga", "nivel": "Alto", "orden": 5},
        {"nombre": "Heroína", "categoria": "Droga", "nivel": "Alto", "orden": 6},
        {"nombre": "Metanfetaminas (Cristal)", "categoria": "Droga", "nivel": "Alto", "orden": 7},
        {"nombre": "Éxtasis (MDMA)", "categoria": "Droga", "nivel": "Alto", "orden": 8},
        {"nombre": "LSD (Ácido)", "categoria": "Droga", "nivel": "Alto", "orden": 9},
        {"nombre": "Inhalables (Thinner, solventes)", "categoria": "Inhalante", "nivel": "Alto", "orden": 10},
        {"nombre": "Pegamento", "categoria": "Inhalante", "nivel": "Alto", "orden": 11},
        {"nombre": "Benzodiacepinas (sin prescripción)", "categoria": "Medicamento", "nivel": "Medio", "orden": 12},
        {"nombre": "Opioides (sin prescripción)", "categoria": "Medicamento", "nivel": "Alto", "orden": 13},
        {"nombre": "Esteroides anabólicos", "categoria": "Medicamento", "nivel": "Medio", "orden": 14},
        {"nombre": "Plomo", "categoria": "Metal pesado", "nivel": "Alto", "orden": 15},
        {"nombre": "Mercurio", "categoria": "Metal pesado", "nivel": "Alto", "orden": 16},
        {"nombre": "Arsénico", "categoria": "Metal pesado", "nivel": "Alto", "orden": 17},
        {"nombre": "Pesticidas", "categoria": "Químico", "nivel": "Alto", "orden": 18},
        {"nombre": "Otros", "categoria": "Otro", "nivel": "Variable", "orden": 19}
    ]
    
    async with AsyncSessionLocal() as session:
        for s_data in sustancias:
            sustancia = SustanciaToxica(
                nombre=s_data["nombre"],
                categoria=s_data["categoria"],
                nivel_peligrosidad=s_data["nivel"],
                orden=s_data["orden"]
            )
            session.add(sustancia)
        await session.commit()
        print(f"✅ {len(sustancias)} sustancias tóxicas creadas")


async def main():
    """Poblar todos los catálogos"""
    print("\n" + "="*70)
    print("POBLANDO CATÁLOGOS DEL SISTEMA")
    print("="*70 + "\n")
    
    await poblar_instituciones()
    await poblar_parentescos()
    await poblar_escolaridades()
    await poblar_examenes()
    await poblar_sustancias()
    
    print("\n" + "="*70)
    print("✅ CATÁLOGOS POBLADOS EXITOSAMENTE")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
