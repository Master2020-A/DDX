import sys
import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.usuario import Usuario


async def main(email: str, new_password: str) -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Usuario).where(Usuario.email == email))
        user = result.scalar_one_or_none()
        if not user:
            print(f"No existe usuario con email: {email}")
            return

        user.password_hash = get_password_hash(new_password)
        await session.commit()
        print(f"Password actualizado para: {email}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python reset_password.py <email> <new_password>")
        raise SystemExit(1)

    asyncio.run(main(sys.argv[1], sys.argv[2]))
