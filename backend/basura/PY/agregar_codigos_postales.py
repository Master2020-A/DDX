"""
Script para agregar códigos postales comunes a la BD
Útil cuando las APIs externas están caídas
"""
import asyncio
import sys
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.catalogos import CodigoPostal


# Códigos postales comunes de México - 100+ ciudades principales
CODIGOS_POSTALES_COMUNES = [
    # Ciudad de México (20+ códigos)
    {"cp": "01000", "estado": "Ciudad de México", "municipio": "Álvaro Obregón", "ciudad": "CDMX", "colonia": "San Ángel"},
    {"cp": "03100", "estado": "Ciudad de México", "municipio": "Benito Juárez", "ciudad": "CDMX", "colonia": "Del Valle Centro"},
    {"cp": "03300", "estado": "Ciudad de México", "municipio": "Benito Juárez", "ciudad": "CDMX", "colonia": "Portales"},
    {"cp": "03400", "estado": "Ciudad de México", "municipio": "Benito Juárez", "ciudad": "CDMX", "colonia": "Álamos"},
    {"cp": "03800", "estado": "Ciudad de México", "municipio": "Benito Juárez", "ciudad": "CDMX", "colonia": "Del Valle Sur"},
    {"cp": "03900", "estado": "Ciudad de México", "municipio": "Benito Juárez", "ciudad": "CDMX", "colonia": "Narvarte"},
    {"cp": "04100", "estado": "Ciudad de México", "municipio": "Coyoacán", "ciudad": "CDMX", "colonia": "Del Carmen"},
    {"cp": "06000", "estado": "Ciudad de México", "municipio": "Cuauhtémoc", "ciudad": "CDMX", "colonia": "Centro"},
    {"cp": "06100", "estado": "Ciudad de México", "municipio": "Cuauhtémoc", "ciudad": "CDMX", "colonia": "Centro"},
    {"cp": "06140", "estado": "Ciudad de México", "municipio": "Cuauhtémoc", "ciudad": "CDMX", "colonia": "Condesa"},
    {"cp": "06700", "estado": "Ciudad de México", "municipio": "Cuauhtémoc", "ciudad": "CDMX", "colonia": "Roma Norte"},
    {"cp": "06760", "estado": "Ciudad de México", "municipio": "Cuauhtémoc", "ciudad": "CDMX", "colonia": "Roma Sur"},
    {"cp": "06800", "estado": "Ciudad de México", "municipio": "Cuauhtémoc", "ciudad": "CDMX", "colonia": "Florida"},
    {"cp": "07300", "estado": "Ciudad de México", "municipio": "Gustavo A. Madero", "ciudad": "CDMX", "colonia": "Lindavista"},
    {"cp": "07800", "estado": "Ciudad de México", "municipio": "Gustavo A. Madero", "ciudad": "CDMX", "colonia": "La Villa"},
    {"cp": "08000", "estado": "Ciudad de México", "municipio": "Iztacalco", "ciudad": "CDMX", "colonia": "Gabriel Ramos Millán"},
    {"cp": "09000", "estado": "Ciudad de México", "municipio": "Iztapalapa", "ciudad": "CDMX", "colonia": "Centro"},
    {"cp": "11000", "estado": "Ciudad de México", "municipio": "Miguel Hidalgo", "ciudad": "CDMX", "colonia": "Polanco"},
    {"cp": "11400", "estado": "Ciudad de México", "municipio": "Miguel Hidalgo", "ciudad": "CDMX", "colonia": "Polanco V Sección"},
    {"cp": "11800", "estado": "Ciudad de México", "municipio": "Miguel Hidalgo", "ciudad": "CDMX", "colonia": "Molino del Rey"},
    
    # Jalisco - Guadalajara y ZMG (15+ códigos)
    {"cp": "44100", "estado": "Jalisco", "municipio": "Guadalajara", "ciudad": "Guadalajara", "colonia": "Centro"},
    {"cp": "44130", "estado": "Jalisco", "municipio": "Guadalajara", "ciudad": "Guadalajara", "colonia": "Americana"},
    {"cp": "44140", "estado": "Jalisco", "municipio": "Guadalajara", "ciudad": "Guadalajara", "colonia": "Lafayette"},
    {"cp": "44150", "estado": "Jalisco", "municipio": "Guadalajara", "ciudad": "Guadalajara", "colonia": "Arcos Vallarta"},
    {"cp": "44160", "estado": "Jalisco", "municipio": "Guadalajara", "ciudad": "Guadalajara", "colonia": "Arcos Vallarta"},
    {"cp": "44200", "estado": "Jalisco", "municipio": "Guadalajara", "ciudad": "Guadalajara", "colonia": "Ladrón de Guevara"},
    {"cp": "44270", "estado": "Jalisco", "municipio": "Guadalajara", "ciudad": "Guadalajara", "colonia": "Jardines del Bosque"},
    {"cp": "44600", "estado": "Jalisco", "municipio": "Guadalajara", "ciudad": "Guadalajara", "colonia": "Jardines del Bosque"},
    {"cp": "44630", "estado": "Jalisco", "municipio": "Guadalajara", "ciudad": "Guadalajara", "colonia": "Jardines de Guadalupe"},
    {"cp": "44900", "estado": "Jalisco", "municipio": "Guadalajara", "ciudad": "Guadalajara", "colonia": "Chapalita"},
    {"cp": "45000", "estado": "Jalisco", "municipio": "Zapopan", "ciudad": "Zapopan", "colonia": "Centro"},
    {"cp": "45040", "estado": "Jalisco", "municipio": "Zapopan", "ciudad": "Zapopan", "colonia": "Tabachines"},
    {"cp": "45050", "estado": "Jalisco", "municipio": "Zapopan", "ciudad": "Zapopan", "colonia": "Arboledas"},
    {"cp": "45070", "estado": "Jalisco", "municipio": "Zapopan", "ciudad": "Zapopan", "colonia": "San Juan de Ocotán"},
    {"cp": "45100", "estado": "Jalisco", "municipio": "Zapopan", "ciudad": "Zapopan", "colonia": "Tesistán"},
    
    # Nuevo León - Monterrey y área metropolitana (15+ códigos)
    {"cp": "64000", "estado": "Nuevo León", "municipio": "Monterrey", "ciudad": "Monterrey", "colonia": "Centro"},
    {"cp": "64050", "estado": "Nuevo León", "municipio": "Monterrey", "ciudad": "Monterrey", "colonia": "Chepevera"},
    {"cp": "64100", "estado": "Nuevo León", "municipio": "Monterrey", "ciudad": "Monterrey", "colonia": "Del Valle"},
    {"cp": "64260", "estado": "Nuevo León", "municipio": "Monterrey", "ciudad": "Monterrey", "colonia": "Mirador"},
    {"cp": "64460", "estado": "Nuevo León", "municipio": "Monterrey", "ciudad": "Monterrey", "colonia": "Tecnológico"},
    {"cp": "64610", "estado": "Nuevo León", "municipio": "Monterrey", "ciudad": "Monterrey", "colonia": "Del Paseo Residencial"},
    {"cp": "64650", "estado": "Nuevo León", "municipio": "Monterrey", "ciudad": "Monterrey", "colonia": "Contry"},
    {"cp": "64700", "estado": "Nuevo León", "municipio": "Monterrey", "ciudad": "Monterrey", "colonia": "Valle de Chipinque"},
    {"cp": "66200", "estado": "Nuevo León", "municipio": "San Pedro Garza García", "ciudad": "San Pedro", "colonia": "Del Valle"},
    {"cp": "66220", "estado": "Nuevo León", "municipio": "San Pedro Garza García", "ciudad": "San Pedro", "colonia": "Del Valle Sector Fátima"},
    {"cp": "66230", "estado": "Nuevo León", "municipio": "San Pedro Garza García", "ciudad": "San Pedro", "colonia": "Del Valle Oriente"},
    {"cp": "66260", "estado": "Nuevo León", "municipio": "San Pedro Garza García", "ciudad": "San Pedro", "colonia": "Pedregal"},
    {"cp": "66450", "estado": "Nuevo León", "municipio": "San Nicolás de los Garza", "ciudad": "San Nicolás", "colonia": "Anáhuac"},
    {"cp": "66470", "estado": "Nuevo León", "municipio": "San Nicolás de los Garza", "ciudad": "San Nicolás", "colonia": "Las Puentes"},
    {"cp": "67000", "estado": "Nuevo León", "municipio": "Guadalupe", "ciudad": "Guadalupe", "colonia": "Guadalupe Centro"},
    
    # Puebla (10+ códigos)
    {"cp": "72000", "estado": "Puebla", "municipio": "Puebla", "ciudad": "Puebla", "colonia": "Centro"},
    {"cp": "72070", "estado": "Puebla", "municipio": "Puebla", "ciudad": "Puebla", "colonia": "Barrio de Santiago"},
    {"cp": "72080", "estado": "Puebla", "municipio": "Puebla", "ciudad": "Puebla", "colonia": "Barrio del Alto"},
    {"cp": "72090", "estado": "Puebla", "municipio": "Puebla", "ciudad": "Puebla", "colonia": "Barrio de Analco"},
    {"cp": "72400", "estado": "Puebla", "municipio": "Puebla", "ciudad": "Puebla", "colonia": "Angelópolis"},
    {"cp": "72410", "estado": "Puebla", "municipio": "Puebla", "ciudad": "Puebla", "colonia": "La Paz"},
    {"cp": "72420", "estado": "Puebla", "municipio": "Puebla", "ciudad": "Puebla", "colonia": "Residencial Boulevares"},
    {"cp": "72430", "estado": "Puebla", "municipio": "Puebla", "ciudad": "Puebla", "colonia": "Lomas de Angelópolis"},
    {"cp": "72530", "estado": "Puebla", "municipio": "Puebla", "ciudad": "Puebla", "colonia": "Bosques de San Sebastián"},
    {"cp": "72570", "estado": "Puebla", "municipio": "Puebla", "ciudad": "Puebla", "colonia": "Zavaleta"},
    
    # Otras ciudades principales (50+ códigos)
    {"cp": "76000", "estado": "Querétaro", "municipio": "Querétaro", "ciudad": "Querétaro", "colonia": "Centro"},
    {"cp": "76020", "estado": "Querétaro", "municipio": "Querétaro", "ciudad": "Querétaro", "colonia": "Alameda"},
    {"cp": "76050", "estado": "Querétaro", "municipio": "Querétaro", "ciudad": "Querétaro", "colonia": "Carretas"},
    {"cp": "76100", "estado": "Querétaro", "municipio": "Querétaro", "ciudad": "Querétaro", "colonia": "Jardines de Querétaro"},
    {"cp": "20000", "estado": "Aguascalientes", "municipio": "Aguascalientes", "ciudad": "Aguascalientes", "colonia": "Centro"},
    {"cp": "20100", "estado": "Aguascalientes", "municipio": "Aguascalientes", "ciudad": "Aguascalientes", "colonia": "San Marcos"},
    {"cp": "20110", "estado": "Aguascalientes", "municipio": "Aguascalientes", "ciudad": "Aguascalientes", "colonia": "Barrio de la Estación"},
    {"cp": "20200", "estado": "Aguascalientes", "municipio": "Aguascalientes", "ciudad": "Aguascalientes", "colonia": "Circunvalación Norte"},
    {"cp": "78000", "estado": "San Luis Potosí", "municipio": "San Luis Potosí", "ciudad": "San Luis Potosí", "colonia": "Centro"},
    {"cp": "78200", "estado": "San Luis Potosí", "municipio": "San Luis Potosí", "ciudad": "San Luis Potosí", "colonia": "Tequisquiapan"},
    {"cp": "78210", "estado": "San Luis Potosí", "municipio": "San Luis Potosí", "ciudad": "San Luis Potosí", "colonia": "Del Valle"},
    {"cp": "97000", "estado": "Yucatán", "municipio": "Mérida", "ciudad": "Mérida", "colonia": "Centro"},
    {"cp": "97070", "estado": "Yucatán", "municipio": "Mérida", "ciudad": "Mérida", "colonia": "Mejorada"},
    {"cp": "97100", "estado": "Yucatán", "municipio": "Mérida", "ciudad": "Mérida", "colonia": "San Sebastián"},
    {"cp": "97110", "estado": "Yucatán", "municipio": "Mérida", "ciudad": "Mérida", "colonia": "Itzimná"},
    {"cp": "22000", "estado": "Baja California", "municipio": "Tijuana", "ciudad": "Tijuana", "colonia": "Centro"},
    {"cp": "22010", "estado": "Baja California", "municipio": "Tijuana", "ciudad": "Tijuana", "colonia": "Altamira"},
    {"cp": "22100", "estado": "Baja California", "municipio": "Tijuana", "ciudad": "Tijuana", "colonia": "Zona Río"},
    {"cp": "22200", "estado": "Baja California", "municipio": "Tijuana", "ciudad": "Tijuana", "colonia": "Juárez"},
    {"cp": "37000", "estado": "Guanajuato", "municipio": "León", "ciudad": "León", "colonia": "Centro"},
    {"cp": "37100", "estado": "Guanajuato", "municipio": "León", "ciudad": "León", "colonia": "Jardines del Moral"},
    {"cp": "37110", "estado": "Guanajuato", "municipio": "León", "ciudad": "León", "colonia": "Valle del Campestre"},
    {"cp": "37150", "estado": "Guanajuato", "municipio": "León", "ciudad": "León", "colonia": "Panorama"},
    {"cp": "83000", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "Centro"},
    {"cp": "83100", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "Pimentel"},
    {"cp": "83140", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "San Benito"},
    # 83288 - Hermosillo (TODAS las colonias)
    {"cp": "83288", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "Aserradero Residencial"},
    {"cp": "83288", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "Centenario Residencial"},
    {"cp": "83288", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "FOVISSSTE"},
    {"cp": "83288", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "Gioconda Residencial"},
    {"cp": "83288", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "Jardines de México"},
    {"cp": "83288", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "Kino Viday"},
    {"cp": "83288", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "Las Veranos"},
    {"cp": "83288", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "Las Praderas"},
    {"cp": "83288", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "Mansión Residencial"},
    {"cp": "83288", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "Monaco Pléncora Residencias"},
    {"cp": "83288", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "Monte de Cantera Residencial"},
    {"cp": "83288", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "Montecarlo Residencial"},
    {"cp": "83288", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "Pinede Rosales"},
    {"cp": "83288", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "Real de Tabaco Residencial"},
    {"cp": "83288", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "Residencial Peñasco"},
    {"cp": "83288", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "Río Grande Residencial"},
    {"cp": "83288", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "San Benito Hispanorama"},
    {"cp": "83288", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "Sedona Residencial"},
    {"cp": "83288", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "Villa Bonita"},
    {"cp": "83288", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "Villa Lourdes"},
    {"cp": "83288", "estado": "Sonora", "municipio": "Hermosillo", "ciudad": "Hermosillo", "colonia": "Villa Residencial Bonita"},
    {"cp": "80000", "estado": "Sinaloa", "municipio": "Culiacán", "ciudad": "Culiacán", "colonia": "Centro"},
    {"cp": "80020", "estado": "Sinaloa", "municipio": "Culiacán", "ciudad": "Culiacán", "colonia": "Guadalupe"},
    {"cp": "80100", "estado": "Sinaloa", "municipio": "Culiacán", "ciudad": "Culiacán", "colonia": "Recursos Hidráulicos"},
    {"cp": "91000", "estado": "Veracruz", "municipio": "Xalapa", "ciudad": "Xalapa", "colonia": "Centro"},
    {"cp": "91020", "estado": "Veracruz", "municipio": "Xalapa", "ciudad": "Xalapa", "colonia": "Revolución"},
    {"cp": "91100", "estado": "Veracruz", "municipio": "Xalapa", "ciudad": "Xalapa", "colonia": "Progreso"},
    {"cp": "29000", "estado": "Chiapas", "municipio": "Tuxtla Gutiérrez", "ciudad": "Tuxtla Gutiérrez", "colonia": "Centro"},
    {"cp": "29020", "estado": "Chiapas", "municipio": "Tuxtla Gutiérrez", "ciudad": "Tuxtla Gutiérrez", "colonia": "San Roque"},
    {"cp": "29030", "estado": "Chiapas", "municipio": "Tuxtla Gutiérrez", "ciudad": "Tuxtla Gutiérrez", "colonia": "La Lomita"},
    {"cp": "68000", "estado": "Oaxaca", "municipio": "Oaxaca de Juárez", "ciudad": "Oaxaca", "colonia": "Centro"},
    {"cp": "68020", "estado": "Oaxaca", "municipio": "Oaxaca de Juárez", "ciudad": "Oaxaca", "colonia": "Xochimilco"},
    {"cp": "68040", "estado": "Oaxaca", "municipio": "Oaxaca de Juárez", "ciudad": "Oaxaca", "colonia": "Reforma"},
    {"cp": "31000", "estado": "Chihuahua", "municipio": "Chihuahua", "ciudad": "Chihuahua", "colonia": "Centro"},
    {"cp": "31020", "estado": "Chihuahua", "municipio": "Chihuahua", "ciudad": "Chihuahua", "colonia": "San Felipe"},
    {"cp": "31100", "estado": "Chihuahua", "municipio": "Chihuahua", "ciudad": "Chihuahua", "colonia": "Santo Niño"},
    {"cp": "32000", "estado": "Chihuahua", "municipio": "Juárez", "ciudad": "Cd. Juárez", "colonia": "Centro"},
    {"cp": "32310", "estado": "Chihuahua", "municipio": "Juárez", "ciudad": "Cd. Juárez", "colonia": "Partido Romero"},
    {"cp": "44700", "estado": "Jalisco", "municipio": "Guadalajara", "ciudad": "Guadalajara", "colonia": "Providencia"},
    {"cp": "45130", "estado": "Jalisco", "municipio": "Zapopan", "ciudad": "Zapopan", "colonia": "Paseos del Sol"},
    {"cp": "45200", "estado": "Jalisco", "municipio": "Zapopan", "ciudad": "Zapopan", "colonia": "Lomas del Valle"},
    {"cp": "45640", "estado": "Jalisco", "municipio": "Tlajomulco de Zúñiga", "ciudad": "Tlajomulco", "colonia": "Valle de los Molinos"},
    {"cp": "45645", "estado": "Jalisco", "municipio": "Tlajomulco de Zúñiga", "ciudad": "Tlajomulco", "colonia": "Hacienda Santa Fe"},
]


async def agregar_codigos_postales():
    """Agregar códigos postales a la BD"""
    print("="*70)
    print("AGREGANDO CÓDIGOS POSTALES A LA BASE DE DATOS")
    print("="*70)
    print()
    
    async with AsyncSessionLocal() as session:
        try:
            agregados = 0
            existentes = 0
            
            for cp_data in CODIGOS_POSTALES_COMUNES:
                # Verificar si ya existe
                result = await session.execute(
                    select(CodigoPostal).where(
                        CodigoPostal.codigo_postal == cp_data["cp"]
                    )
                )
                cp_existente = result.scalar_one_or_none()
                
                if cp_existente:
                    print(f"⏭️  {cp_data['cp']} - Ya existe ({cp_data['estado']}, {cp_data['municipio']})")
                    existentes += 1
                else:
                    # Crear nuevo código postal
                    nuevo_cp = CodigoPostal(
                        codigo_postal=cp_data["cp"],
                        pais="México",
                        estado=cp_data["estado"],
                        municipio=cp_data["municipio"],
                        ciudad=cp_data["ciudad"],
                        colonia=cp_data["colonia"],
                        activo=True
                    )
                    session.add(nuevo_cp)
                    print(f"✅ {cp_data['cp']} - Agregado ({cp_data['estado']}, {cp_data['municipio']}, {cp_data['colonia']})")
                    agregados += 1
            
            await session.commit()
            
            print()
            print("="*70)
            print("RESUMEN:")
            print("="*70)
            print(f"✅ Códigos postales agregados: {agregados}")
            print(f"⏭️  Códigos postales que ya existían: {existentes}")
            print(f"📊 Total procesados: {len(CODIGOS_POSTALES_COMUNES)}")
            print()
            print("Ahora puedes probar el código postal en el frontend.")
            print("="*70)
            
            return True
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False


async def listar_codigos_postales():
    """Listar todos los códigos postales en la BD"""
    print("="*70)
    print("CÓDIGOS POSTALES EN LA BASE DE DATOS")
    print("="*70)
    print()
    
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(CodigoPostal)
                .where(CodigoPostal.activo == True)
                .order_by(CodigoPostal.codigo_postal)
            )
            codigos = result.scalars().all()
            
            if not codigos:
                print("❌ No hay códigos postales en la base de datos")
                return
            
            print(f"Total: {len(codigos)} códigos postales\n")
            print(f"{'CP':<8} {'Estado':<20} {'Municipio':<25} {'Colonia':<30}")
            print("-"*90)
            
            for cp in codigos:
                print(f"{cp.codigo_postal:<8} {cp.estado:<20} {cp.municipio:<25} {cp.colonia or '':<30}")
            
            print()
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")


async def main():
    """Función principal"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--listar":
        await listar_codigos_postales()
    else:
        await agregar_codigos_postales()


if __name__ == "__main__":
    try:
        asyncio.run(main())
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso cancelado")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
