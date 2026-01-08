"""
Servicio de despliegue de módulos DDX Studio
Escribe archivos físicos y registra módulos dinámicamente
"""

import os
import importlib
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.services.code_generator import CodeGenerator

logger = logging.getLogger(__name__)


class ModuleDeployer:
    """Despliega módulos generados por DDX Studio"""

    def __init__(self, base_path: str = None):
        if base_path is None:
            # Directorio raíz del proyecto
            self.base_path = Path(__file__).parent.parent.parent
        else:
            self.base_path = Path(base_path)

        # Directorios para módulos generados
        self.models_dir = self.base_path / "app" / "models" / "generated"
        self.api_dir = self.base_path / "app" / "api" / "generated"
        self.frontend_dir = (
            self.base_path.parent / "frontend" / "src" / "pages" / "generated"
        )

        # Crear directorios si no existen
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.api_dir.mkdir(parents=True, exist_ok=True)

        # Crear __init__.py en directorios generados solo si no existen
        models_init = self.models_dir / "__init__.py"
        api_init = self.api_dir / "__init__.py"

        if not models_init.exists():
            models_init.write_text("# Generated models\n")
        if not api_init.exists():
            api_init.write_text("# Generated API endpoints\n")

    async def deploy_module(
        self, module_definition: Dict[str, Any], db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Despliega un módulo completo:
        1. Genera código
        2. Escribe archivos
        3. Ejecuta migraciones
        4. Registra rutas
        """
        module_name = module_definition.get("module_id", "custom_module")
        results = {
            "module_id": module_name,
            "models": [],
            "endpoints": [],
            "components": [],
            "migrations": [],
            "errors": [],
        }

        try:
            # 1. Generar y escribir modelos
            for model_def_raw in module_definition.get("models", []):
                try:
                    model_result = await self._deploy_model(
                        model_def_raw, module_definition, db
                    )
                    results["models"].append(model_result)
                except Exception as e:
                    logger.error(
                        f"Error desplegando modelo {model_def_raw.get('name')}: {e}"
                    )
                    results["errors"].append(
                        f"Modelo {model_def_raw.get('name')}: {str(e)}"
                    )

            # 2. Generar y escribir endpoints
            for model_def_raw in module_definition.get("models", []):
                try:
                    endpoint_result = await self._deploy_endpoint(
                        model_def_raw, module_definition
                    )
                    results["endpoints"].append(endpoint_result)
                except Exception as e:
                    logger.error(
                        f"Error desplegando endpoint para {model_def_raw.get('name')}: {e}"
                    )
                    results["errors"].append(
                        f"Endpoint {model_def_raw.get('name')}: {str(e)}"
                    )

            # 3. Generar componentes frontend (opcional)
            if self.frontend_dir.exists():
                self.frontend_dir.mkdir(parents=True, exist_ok=True)
                for model_def_raw in module_definition.get("models", []):
                    try:
                        component_result = self._deploy_component(
                            model_def_raw, module_definition
                        )
                        results["components"].append(component_result)
                    except Exception as e:
                        logger.error(
                            f"Error desplegando componente para {model_def_raw.get('name')}: {e}"
                        )
                        results["errors"].append(
                            f"Componente {model_def_raw.get('name')}: {str(e)}"
                        )

            logger.info(f"Módulo {module_name} desplegado exitosamente")
            return results

        except Exception as e:
            logger.error(f"Error general desplegando módulo {module_name}: {e}")
            results["errors"].append(f"Error general: {str(e)}")
            return results

    async def _deploy_model(
        self,
        model_def_raw: Dict[str, Any],
        module_definition: Dict[str, Any],
        db: AsyncSession,
    ) -> Dict[str, str]:
        """Genera y escribe archivo de modelo + ejecuta migración"""
        model_def = {
            "module_name": module_definition.get("name", "CustomModule"),
            "name": model_def_raw["name"],
            "table_name": model_def_raw["table_name"],
            "description": model_def_raw.get("description", ""),
            "fields": model_def_raw["fields"],
            "relationships": model_def_raw.get("relationships", []),
        }

        # Generar código del modelo
        model_code = CodeGenerator.generate_model_code(model_def)

        # Escribir archivo
        model_filename = f"{model_def_raw['name'].lower()}.py"
        model_path = self.models_dir / model_filename

        with open(model_path, "w", encoding="utf-8") as f:
            f.write(model_code)

        # Generar y ejecutar migración SQL
        migration_sql = CodeGenerator.generate_migration_sql(model_def)

        try:
            # Ejecutar migración
            await db.execute(text(migration_sql))
            await db.commit()
            logger.info(f"Migración ejecutada para tabla {model_def_raw['table_name']}")
        except Exception as e:
            logger.warning(
                f"Error ejecutando migración para {model_def_raw['table_name']}: {e}"
            )
            # No fallar si la tabla ya existe

        return {
            "name": model_def_raw["name"],
            "file": str(model_path),
            "table": model_def_raw["table_name"],
            "status": "deployed",
        }

    async def _deploy_endpoint(
        self, model_def_raw: Dict[str, Any], module_definition: Dict[str, Any]
    ) -> Dict[str, str]:
        """Genera y escribe archivo de endpoint"""
        endpoint_def = {
            "module_name": module_definition.get("name", "CustomModule"),
            "model_name": model_def_raw["name"],
            "path": model_def_raw["table_name"],
            "fields": model_def_raw["fields"],
        }

        # Generar código del endpoint
        endpoint_code = CodeGenerator.generate_endpoint_code(endpoint_def)

        # Escribir archivo
        endpoint_filename = f"{model_def_raw['name'].lower()}.py"
        endpoint_path = self.api_dir / endpoint_filename

        with open(endpoint_path, "w", encoding="utf-8") as f:
            f.write(endpoint_code)

        logger.info(f"Endpoint generado: {endpoint_path}")

        return {
            "name": model_def_raw["name"],
            "file": str(endpoint_path),
            "path": f"/api/{model_def_raw['table_name']}",
            "status": "deployed",
        }

    def _deploy_component(
        self, model_def_raw: Dict[str, Any], module_definition: Dict[str, Any]
    ) -> Dict[str, str]:
        """Genera y escribe componente React"""
        component_def = {
            "module_name": module_definition.get("name", "CustomModule"),
            "model_name": model_def_raw["name"],
            "component_name": f"{model_def_raw['name']}Page",
            "title": module_definition.get("name", model_def_raw["name"]),
            "endpoint_path": model_def_raw["table_name"],
            "fields": model_def_raw["fields"],
        }

        # Generar código del componente
        component_code = CodeGenerator.generate_react_component(component_def)

        # Escribir archivo
        component_filename = f"{model_def_raw['name']}Page.tsx"
        component_path = self.frontend_dir / component_filename

        with open(component_path, "w", encoding="utf-8") as f:
            f.write(component_code)

        logger.info(f"Componente generado: {component_path}")

        return {
            "name": f"{model_def_raw['name']}Page",
            "file": str(component_path),
            "route": f"/generated/{model_def_raw['name'].lower()}",
            "status": "deployed",
        }

    def load_generated_routes(self, app) -> List[str]:
        """
        Carga dinámicamente las rutas de los módulos generados
        Retorna lista de módulos cargados
        """
        loaded_modules = []

        if not self.api_dir.exists():
            return loaded_modules

        # Buscar todos los archivos .py en el directorio generado
        for py_file in self.api_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue

            try:
                # Importar módulo dinámicamente
                module_name = f"app.api.generated.{py_file.stem}"

                # Recargar si ya está importado
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                else:
                    importlib.import_module(module_name)

                module = sys.modules[module_name]

                # Buscar router en el módulo
                if hasattr(module, "router"):
                    router = module.router
                    prefix = f"/api/generated/{py_file.stem}"

                    # Registrar router en la app
                    app.include_router(
                        router, prefix=prefix, tags=[f"Generated: {py_file.stem}"]
                    )

                    loaded_modules.append(module_name)
                    logger.info(f"Módulo generado cargado: {module_name} en {prefix}")

            except Exception as e:
                logger.error(f"Error cargando módulo generado {py_file.name}: {e}")

        return loaded_modules

    async def undeploy_module(self, module_id: str) -> Dict[str, Any]:
        """
        Elimina archivos de un módulo desplegado
        NO elimina las tablas de la base de datos por seguridad
        """
        results = {"module_id": module_id, "deleted_files": [], "errors": []}

        try:
            # Buscar y eliminar archivos relacionados
            patterns = [
                self.models_dir / f"{module_id}*.py",
                self.api_dir / f"{module_id}*.py",
                self.frontend_dir / f"{module_id}*.tsx",
            ]

            for pattern in patterns:
                for file_path in pattern.parent.glob(pattern.name):
                    try:
                        file_path.unlink()
                        results["deleted_files"].append(str(file_path))
                        logger.info(f"Archivo eliminado: {file_path}")
                    except Exception as e:
                        results["errors"].append(
                            f"Error eliminando {file_path}: {str(e)}"
                        )

            return results

        except Exception as e:
            logger.error(f"Error general eliminando módulo {module_id}: {e}")
            results["errors"].append(f"Error general: {str(e)}")
            return results
