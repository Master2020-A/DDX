from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioLogin, Token

router = APIRouter()


@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UsuarioCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Registrar un nuevo usuario en el sistema.
    """
    # Check if email already exists
    result = await db.execute(select(Usuario).where(Usuario.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado",
        )
    
    # Create new user
    new_user = Usuario(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        nombre_completo=user_data.nombre_completo,
        rol=user_data.rol,
        especialidad=user_data.especialidad,
        cedula_profesional=user_data.cedula_profesional,
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    credentials: UsuarioLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Iniciar sesión y obtener token de acceso.
    """
    # Find user by email
    result = await db.execute(select(Usuario).where(Usuario.email == credentials.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        user=UsuarioResponse.model_validate(user)
    )
