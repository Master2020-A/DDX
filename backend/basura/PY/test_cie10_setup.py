"""
Script para verificar y configurar tabla CIE-10
"""

import asyncio
import sys
from sqlalchemy import text
from app.core.database import engine, AsyncSessionLocal
from app.models.cie10 import CIE10
import uuid


async def verificar_y_crear_tabla():
    """Verifica si la tabla existe y la crea si no"""
    async with engine.begin() as conn:
        # Verificar si la tabla existe
        result = await conn.execute(
            text(
                """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'cie10'
            );
        """
            )
        )
        existe = result.scalar()

        if existe:
            print("✅ La tabla 'cie10' ya existe")

            # Contar registros
            result = await conn.execute(text("SELECT COUNT(*) FROM cie10"))
            count = result.scalar()
            print(f"📊 Registros actuales: {count}")

            if count > 0:
                print("✅ La tabla ya tiene datos")
                return True
            else:
                print("⚠️ La tabla existe pero está vacía")
                return False
        else:
            print("❌ La tabla 'cie10' NO existe")
            print("🔧 Ejecutando migración...")

            # Crear tabla manualmente (cada comando por separado)
            await conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS cie10 (
                    id UUID PRIMARY KEY,
                    codigo VARCHAR(10) NOT NULL,
                    descripcion TEXT NOT NULL,
                    categoria VARCHAR(100),
                    subcategoria VARCHAR(200),
                    keywords TEXT,
                    sinonimos TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """
                )
            )

            await conn.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS ix_cie10_codigo ON cie10(codigo)"
                )
            )
            await conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_cie10_categoria ON cie10(categoria)"
                )
            )
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
            await conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_cie10_descripcion_trgm ON cie10 USING gin (descripcion gin_trgm_ops)"
                )
            )
            await conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_cie10_keywords_trgm ON cie10 USING gin (keywords gin_trgm_ops)"
                )
            )

            print("✅ Tabla creada exitosamente")
            return False


async def poblar_datos():
    """Pobla la tabla con códigos CIE-10 comunes"""
    codigos_cie10 = [
        # Enfermedades infecciosas
        (
            "A00.0",
            "Cólera debido a Vibrio cholerae 01, biotipo cholerae",
            "Enfermedades infecciosas",
            "infección, diarrea, vibrio",
        ),
        (
            "A09",
            "Diarrea y gastroenteritis de presunto origen infeccioso",
            "Enfermedades infecciosas",
            "diarrea, gastroenteritis, infección intestinal",
        ),
        (
            "A15.0",
            "Tuberculosis del pulmón",
            "Enfermedades infecciosas",
            "tuberculosis, pulmón, TBC, bacilo de Koch",
        ),
        # Enfermedades cardiovasculares
        (
            "I10",
            "Hipertensión esencial (primaria)",
            "Enfermedades cardiovasculares",
            "presión alta, hipertensión arterial, HTA",
        ),
        (
            "I20.0",
            "Angina inestable",
            "Enfermedades cardiovasculares",
            "angina, dolor torácico, corazón",
        ),
        (
            "I21.0",
            "Infarto agudo del miocardio",
            "Enfermedades cardiovasculares",
            "infarto, IAM, ataque cardíaco",
        ),
        (
            "I50.0",
            "Insuficiencia cardíaca congestiva",
            "Enfermedades cardiovasculares",
            "insuficiencia cardíaca, ICC, corazón",
        ),
        # Enfermedades respiratorias
        (
            "J00",
            "Rinofaringitis aguda (resfriado común)",
            "Enfermedades respiratorias",
            "resfriado, catarro, gripe común",
        ),
        (
            "J02.9",
            "Faringitis aguda",
            "Enfermedades respiratorias",
            "dolor de garganta, faringitis",
        ),
        (
            "J03.9",
            "Amigdalitis aguda",
            "Enfermedades respiratorias",
            "anginas, amígdalas inflamadas",
        ),
        (
            "J06.9",
            "Infección aguda de las vías respiratorias superiores",
            "Enfermedades respiratorias",
            "IVRS, infección respiratoria",
        ),
        (
            "J18.9",
            "Neumonía",
            "Enfermedades respiratorias",
            "pulmonía, infección pulmonar",
        ),
        (
            "J45.0",
            "Asma",
            "Enfermedades respiratorias",
            "asma bronquial, broncoespasmo",
        ),
        # Enfermedades digestivas
        (
            "K21.0",
            "Enfermedad por reflujo gastroesofágico",
            "Enfermedades digestivas",
            "reflujo, ERGE, acidez",
        ),
        (
            "K29.0",
            "Gastritis aguda",
            "Enfermedades digestivas",
            "gastritis, inflamación estómago",
        ),
        (
            "K35.8",
            "Apendicitis aguda",
            "Enfermedades digestivas",
            "apendicitis, apéndice inflamado",
        ),
        (
            "K80.0",
            "Colelitiasis",
            "Enfermedades digestivas",
            "piedras vesícula, cálculos biliares",
        ),
        # Enfermedades endocrinas
        (
            "E10.9",
            "Diabetes mellitus tipo 1",
            "Enfermedades endocrinas",
            "diabetes tipo 1, insulinodependiente",
        ),
        (
            "E11.9",
            "Diabetes mellitus tipo 2",
            "Enfermedades endocrinas",
            "diabetes tipo 2, no insulinodependiente",
        ),
        ("E66.0", "Obesidad", "Enfermedades endocrinas", "sobrepeso, obesidad"),
        (
            "E78.0",
            "Hipercolesterolemia",
            "Enfermedades endocrinas",
            "colesterol alto, dislipidemia",
        ),
        # Enfermedades neurológicas
        (
            "G40.9",
            "Epilepsia",
            "Enfermedades neurológicas",
            "convulsiones, crisis epiléptica",
        ),
        ("G43.9", "Migraña", "Enfermedades neurológicas", "jaqueca, cefalea migrañosa"),
        (
            "G44.2",
            "Cefalea tensional",
            "Enfermedades neurológicas",
            "dolor de cabeza, cefalea",
        ),
        # Enfermedades musculoesqueléticas
        (
            "M10.0",
            "Gota",
            "Enfermedades musculoesqueléticas",
            "gota, ácido úrico elevado",
        ),
        (
            "M15.0",
            "Artrosis",
            "Enfermedades musculoesqueléticas",
            "osteoartritis, desgaste articular",
        ),
        (
            "M54.5",
            "Lumbalgia",
            "Enfermedades musculoesqueléticas",
            "dolor lumbar, dolor de espalda baja",
        ),
        # Enfermedades genitourinarias
        (
            "N18.9",
            "Enfermedad renal crónica",
            "Enfermedades genitourinarias",
            "insuficiencia renal, ERC",
        ),
        (
            "N30.0",
            "Cistitis aguda",
            "Enfermedades genitourinarias",
            "infección urinaria, cistitis",
        ),
        (
            "N39.0",
            "Infección de vías urinarias",
            "Enfermedades genitourinarias",
            "IVU, infección urinaria",
        ),
        # Embarazo y parto
        (
            "O00.0",
            "Embarazo ectópico",
            "Embarazo y parto",
            "embarazo extrauterino, embarazo tubárico",
        ),
        (
            "O80",
            "Parto único espontáneo",
            "Embarazo y parto",
            "parto normal, parto vaginal",
        ),
        # Traumatismos
        (
            "S06.0",
            "Conmoción cerebral",
            "Traumatismos",
            "traumatismo craneal, golpe en la cabeza",
        ),
        (
            "S52.5",
            "Fractura de radio",
            "Traumatismos",
            "fractura antebrazo, fractura muñeca",
        ),
        (
            "S82.0",
            "Fractura de tibia",
            "Traumatismos",
            "fractura pierna, fractura tibia",
        ),
        # Síntomas y signos
        ("R05", "Tos", "Síntomas y signos", "tos seca, tos productiva"),
        (
            "R06.0",
            "Disnea",
            "Síntomas y signos",
            "dificultad respiratoria, falta de aire",
        ),
        ("R10.0", "Abdomen agudo", "Síntomas y signos", "dolor abdominal agudo"),
        ("R50.9", "Fiebre", "Síntomas y signos", "temperatura elevada, hipertermia"),
        ("R51", "Cefalea", "Síntomas y signos", "dolor de cabeza"),
        # Factores de riesgo
        ("Z72.0", "Uso de tabaco", "Factores de riesgo", "tabaquismo, fumador"),
        (
            "Z86.7",
            "Historia personal de enfermedades del sistema circulatorio",
            "Factores de riesgo",
            "antecedente cardiovascular",
        ),
    ]

    async with AsyncSessionLocal() as session:
        try:
            for codigo, descripcion, categoria, keywords in codigos_cie10:
                # Verificar si ya existe
                result = await session.execute(
                    text("SELECT id FROM cie10 WHERE codigo = :codigo"),
                    {"codigo": codigo},
                )
                existe = result.scalar()

                if not existe:
                    await session.execute(
                        text(
                            """
                            INSERT INTO cie10 (id, codigo, descripcion, categoria, keywords)
                            VALUES (:id, :codigo, :descripcion, :categoria, :keywords)
                        """
                        ),
                        {
                            "id": str(uuid.uuid4()),
                            "codigo": codigo,
                            "descripcion": descripcion,
                            "categoria": categoria,
                            "keywords": keywords,
                        },
                    )
                    print(f"✅ Agregado: {codigo} - {descripcion}")
                else:
                    print(f"⏭️ Ya existe: {codigo}")

            await session.commit()
            print(
                f"\n✅ Proceso completado. Total de códigos procesados: {len(codigos_cie10)}"
            )

        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()
            raise


async def main():
    print("🔍 Verificando configuración de CIE-10...\n")

    try:
        tabla_poblada = await verificar_y_crear_tabla()

        if not tabla_poblada:
            print("\n📝 Poblando base de datos con códigos CIE-10...\n")
            await poblar_datos()

        print("\n✅ ¡Configuración completada exitosamente!")

    except Exception as e:
        print(f"\n❌ Error durante la configuración: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
