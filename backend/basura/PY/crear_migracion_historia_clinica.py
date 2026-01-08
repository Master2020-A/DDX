"""
Script para generar la migración de Historia Clínica Pediátrica
"""
import os
import sys

print("="*70)
print("CREAR MIGRACIÓN PARA HISTORIA CLÍNICA PEDIÁTRICA")
print("="*70)

print("\n📝 Generando migración con Alembic...")
print("\nEjecuta este comando en tu terminal:\n")
print("alembic revision --autogenerate -m \"Add historia clinica pediatrica tables\"")
print("\nLuego ejecuta:")
print("alembic upgrade head")
print("\n" + "="*70)
