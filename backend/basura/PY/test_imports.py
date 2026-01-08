#!/usr/bin/env python3
"""Script para verificar imports críticos"""

print("=" * 60)
print("VERIFICANDO IMPORTS CRÍTICOS")
print("=" * 60)

try:
    import asyncpg
    print("✓ asyncpg instalado correctamente")
except ImportError as e:
    print(f"✗ asyncpg NO ENCONTRADO: {e}")

try:
    import bcrypt
    print(f"✓ bcrypt instalado correctamente (versión: {bcrypt.__version__})")
except ImportError as e:
    print(f"✗ bcrypt NO ENCONTRADO: {e}")

try:
    from fastapi import FastAPI
    print("✓ FastAPI instalado correctamente")
except ImportError as e:
    print(f"✗ FastAPI NO ENCONTRADO: {e}")

try:
    from sqlalchemy.ext.asyncio import create_async_engine
    print("✓ SQLAlchemy async instalado correctamente")
except ImportError as e:
    print(f"✗ SQLAlchemy async NO ENCONTRADO: {e}")

print("=" * 60)
print("VERIFICACIÓN COMPLETADA")
print("=" * 60)
