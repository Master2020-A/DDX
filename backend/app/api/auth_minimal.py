"""
Router mínimo de autenticación para probar
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pydantic import BaseModel
from app.schemas.usuario import UsuarioLogin, Token
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.models.usuario import Usuario
from fastapi import Response
from app.api.dependencies import get_current_user

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=Token)
async def login(
    credentials: UsuarioLogin, response: Response, db: AsyncSession = Depends(get_db)
):
    """Login endpoint"""
    result = await db.execute(select(Usuario).where(Usuario.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )

    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo"
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )

    from app.schemas.usuario import UsuarioResponse

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UsuarioResponse(
            id=user.id,
            email=user.email,
            nombre_completo=user.nombre_completo,
            rol=user.rol,
            especialidad=user.especialidad,
            cedula_profesional=user.cedula_profesional,
            activo=user.activo,
            created_at=user.created_at,
            updated_at=user.updated_at,
        ),
    )


@router.get("/me")
async def me(current_user: Usuario = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "rol": current_user.rol,
        "activo": current_user.activo,
    }
