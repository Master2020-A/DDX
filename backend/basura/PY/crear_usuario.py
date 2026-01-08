"""
Script interactivo para crear usuarios del sistema
Ejecutar: python crear_usuario.py
"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.usuario import Usuario, RolEnum
from app.core.security import get_password_hash


async def create_user():
    """Crear usuario interactivamente"""
    
    print('='*60)
    print('CREAR NUEVO USUARIO DEL SISTEMA')
    print('='*60)
    print()
    
    # Solicitar datos básicos
    email = input('Email: ').strip()
    
    # Verificar si ya existe
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(Usuario).where(Usuario.email == email)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f'\n[ERROR] El email {email} ya esta registrado')
            return
    
    password = input('Password: ').strip()
    nombre = input('Nombre completo: ').strip()
    
    # Seleccionar rol
    print('\nRoles disponibles:')
    print('1. medico       - Medico general')
    print('2. enfermero    - Personal de enfermeria')
    print('3. administrativo - Personal administrativo')
    print('4. especialista - Medico especialista')
    print('5. admin        - Administrador del sistema')
    
    while True:
        rol_num = input('\nSelecciona rol (1-5): ').strip()
        if rol_num in ['1', '2', '3', '4', '5']:
            break
        print('[ERROR] Opcion invalida, intenta de nuevo')
    
    roles = ['medico', 'enfermero', 'administrativo', 'especialista', 'admin']
    rol = roles[int(rol_num) - 1]
    
    # Datos adicionales para médicos
    especialidad = None
    cedula = None
    
    if rol in ['medico', 'especialista']:
        print()
        especialidad = input('Especialidad: ').strip()
        cedula = input('Cedula profesional: ').strip()
    
    # Confirmar datos
    print('\n' + '='*60)
    print('CONFIRMAR DATOS')
    print('='*60)
    print(f'Email:        {email}')
    print(f'Nombre:       {nombre}')
    print(f'Rol:          {rol}')
    if especialidad:
        print(f'Especialidad: {especialidad}')
    if cedula:
        print(f'Cedula:       {cedula}')
    print('='*60)
    
    confirmar = input('\nCrear usuario? (s/n): ').strip().lower()
    if confirmar != 's':
        print('[INFO] Operacion cancelada')
        return
    
    # Crear usuario
    async with AsyncSessionLocal() as session:
        nuevo_usuario = Usuario(
            email=email,
            password_hash=get_password_hash(password),
            nombre_completo=nombre,
            rol=rol,
            especialidad=especialidad,
            cedula_profesional=cedula,
            activo=True
        )
        
        session.add(nuevo_usuario)
        await session.commit()
        
        print('\n' + '='*60)
        print('[OK] USUARIO CREADO EXITOSAMENTE')
        print('='*60)
        print(f'Email:    {email}')
        print(f'Nombre:   {nombre}')
        print(f'Rol:      {rol}')
        print('='*60)


async def listar_usuarios():
    """Listar todos los usuarios del sistema"""
    
    print('='*60)
    print('USUARIOS REGISTRADOS')
    print('='*60)
    
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(Usuario))
        usuarios = result.scalars().all()
        
        if not usuarios:
            print('[INFO] No hay usuarios registrados')
            return
        
        for i, usuario in enumerate(usuarios, 1):
            print(f'\n{i}. {usuario.nombre_completo}')
            print(f'   Email: {usuario.email}')
            print(f'   Rol: {usuario.rol}')
            if usuario.especialidad:
                print(f'   Especialidad: {usuario.especialidad}')
            print(f'   Activo: {"Si" if usuario.activo else "No"}')
    
    print('\n' + '='*60)


async def main():
    """Menu principal"""
    
    while True:
        print('\n' + '='*60)
        print('GESTION DE USUARIOS - Sistema DDX')
        print('='*60)
        print('1. Crear nuevo usuario')
        print('2. Listar usuarios registrados')
        print('3. Salir')
        print('='*60)
        
        opcion = input('\nSelecciona una opcion (1-3): ').strip()
        
        if opcion == '1':
            await create_user()
        elif opcion == '2':
            await listar_usuarios()
        elif opcion == '3':
            print('\n[INFO] Saliendo...')
            break
        else:
            print('[ERROR] Opcion invalida')


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n\n[INFO] Operacion cancelada por el usuario')
    except Exception as e:
        print(f'\n[ERROR] Error: {e}')
        print('\nVerifica que:')
        print('1. PostgreSQL este corriendo')
        print('2. La base de datos ddx_db exista')
        print('3. El archivo .env este configurado correctamente')
        print('4. Las tablas esten creadas (ejecuta schema.sql)')
