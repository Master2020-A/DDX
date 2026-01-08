"""
API para DDX Studio - Constructor visual no-code
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
import logging

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.usuario import Usuario
from app.models.custom_module import (
    CustomModule,
    CustomModel,
    CustomEndpoint,
    CustomForm,
    ModuleDeployment,
    ModuleStatus,
)
from app.services.code_generator import CodeGenerator

logger = logging.getLogger(__name__)
router = APIRouter()  # main.py lo monta con prefix="/api/studio"


# ==================== SCHEMAS ====================


class FieldDefinition(BaseModel):
    name: str
    type: str
    label: Optional[str] = None
    required: bool = False
    nullable: bool = True
    unique: bool = False
    indexed: bool = False
    default: Optional[Any] = None
    validation: Optional[Dict[str, Any]] = None
    show_in_table: bool = True
    show_in_form: bool = True


class RelationshipDefinition(BaseModel):
    name: str
    target_model: str
    type: str
    back_populates: Optional[str] = None


class ModelDefinition(BaseModel):
    name: str
    table_name: str
    description: Optional[str] = None
    fields: List[FieldDefinition]
    relationships: Optional[List[RelationshipDefinition]] = []
    indexes: Optional[List[str]] = []


class EndpointDefinition(BaseModel):
    name: str
    path: str
    method: str
    description: Optional[str] = None
    auth_required: bool = True
    handler_type: str = "crud"
    model_name: Optional[str] = None
    custom_logic: Optional[Dict[str, Any]] = None


class FormDefinition(BaseModel):
    name: str
    title: str
    description: Optional[str] = None
    fields: List[FieldDefinition]
    layout: Optional[Dict[str, Any]] = None
    submit_endpoint: str


class ModuleDefinition(BaseModel):
    module_id: str
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    icon: Optional[str] = None
    color: Optional[str] = None
    category: Optional[str] = None
    models: List[ModelDefinition] = []
    endpoints: List[EndpointDefinition] = []
    forms: List[FormDefinition] = []


class ModuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    module_id: str
    name: str
    description: Optional[str] = None
    version: str
    status: str
    icon: Optional[str] = None
    color: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CodePreview(BaseModel):
    model_code: Optional[str] = None
    endpoint_code: Optional[str] = None
    component_code: Optional[str] = None
    migration_sql: Optional[str] = None


# ==================== ENDPOINTS ====================


@router.get("/modules", response_model=List[ModuleResponse])
async def list_modules(
    status_filter: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    query = select(CustomModule)
    if status_filter:
        query = query.where(CustomModule.status == status_filter)
    if category:
        query = query.where(CustomModule.category == category)

    result = await db.execute(query.order_by(CustomModule.created_at.desc()))
    return result.scalars().all()


@router.post(
    "/modules", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED
)
async def create_module(
    module_def: ModuleDefinition,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(
        select(CustomModule).where(CustomModule.module_id == module_def.module_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un módulo con ID '{module_def.module_id}'",
        )

    new_module = CustomModule(
        module_id=module_def.module_id,
        name=module_def.name,
        description=module_def.description,
        version=module_def.version,
        icon=module_def.icon,
        color=module_def.color,
        category=module_def.category,
        status=ModuleStatus.DRAFT.value,
        definition=module_def.model_dump(),
        created_by_id=current_user.id,
    )
    db.add(new_module)
    await db.commit()
    await db.refresh(new_module)

    for m in module_def.models:
        db.add(
            CustomModel(
                module_id=new_module.id,
                name=m.name,
                table_name=m.table_name,
                description=m.description,
                fields=[f.model_dump() for f in m.fields],
                relationships=[r.model_dump() for r in (m.relationships or [])],
                indexes=m.indexes,
            )
        )

    for e in module_def.endpoints:
        db.add(
            CustomEndpoint(
                module_id=new_module.id,
                name=e.name,
                path=e.path,
                method=e.method,
                description=e.description,
                auth_required=e.auth_required,
                handler_type=e.handler_type,
                handler_config=e.model_dump(),
            )
        )

    for f in module_def.forms:
        db.add(
            CustomForm(
                module_id=new_module.id,
                name=f.name,
                title=f.title,
                description=f.description,
                fields=[x.model_dump() for x in f.fields],
                layout=f.layout,
                submit_endpoint=f.submit_endpoint,
            )
        )

    await db.commit()
    await db.refresh(new_module)
    return new_module


@router.get("/modules/{module_id}", response_model=ModuleResponse)
async def get_module(
    module_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(
        select(CustomModule).where(CustomModule.module_id == module_id)
    )
    module = result.scalar_one_or_none()
    if not module:
        raise HTTPException(
            status_code=404, detail=f"Módulo '{module_id}' no encontrado"
        )
    return module


@router.put("/modules/{module_id}", response_model=ModuleResponse)
async def update_module(
    module_id: str,
    module_def: ModuleDefinition,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(
        select(CustomModule).where(CustomModule.module_id == module_id)
    )
    module = result.scalar_one_or_none()
    if not module:
        raise HTTPException(
            status_code=404, detail=f"Módulo '{module_id}' no encontrado"
        )

    module.name = module_def.name
    module.description = module_def.description
    module.version = module_def.version
    module.icon = module_def.icon
    module.color = module_def.color
    module.category = module_def.category
    module.definition = module_def.model_dump()

    await db.execute(delete(CustomModel).where(CustomModel.module_id == module.id))
    await db.execute(
        delete(CustomEndpoint).where(CustomEndpoint.module_id == module.id)
    )
    await db.execute(delete(CustomForm).where(CustomForm.module_id == module.id))

    for m in module_def.models:
        db.add(
            CustomModel(
                module_id=module.id,
                name=m.name,
                table_name=m.table_name,
                description=m.description,
                fields=[f.model_dump() for f in m.fields],
                relationships=[r.model_dump() for r in (m.relationships or [])],
                indexes=m.indexes,
            )
        )

    for e in module_def.endpoints:
        db.add(
            CustomEndpoint(
                module_id=module.id,
                name=e.name,
                path=e.path,
                method=e.method,
                description=e.description,
                auth_required=e.auth_required,
                handler_type=e.handler_type,
                handler_config=e.model_dump(),
            )
        )

    for f in module_def.forms:
        db.add(
            CustomForm(
                module_id=module.id,
                name=f.name,
                title=f.title,
                description=f.description,
                fields=[x.model_dump() for x in f.fields],
                layout=f.layout,
                submit_endpoint=f.submit_endpoint,
            )
        )

    await db.commit()
    await db.refresh(module)
    return module


@router.delete("/modules/{module_id}")
async def delete_module(
    module_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Elimina un módulo de la base de datos y sus archivos generados
    """
    from app.services.module_deployer import ModuleDeployer

    result = await db.execute(
        select(CustomModule).where(CustomModule.module_id == module_id)
    )
    module = result.scalar_one_or_none()
    if not module:
        raise HTTPException(
            status_code=404, detail=f"Módulo '{module_id}' no encontrado"
        )

    # Eliminar archivos físicos si el módulo está desplegado
    if module.status == ModuleStatus.ACTIVE.value:
        deployer = ModuleDeployer()
        undeploy_result = await deployer.undeploy_module(module_id)
        logger.info(f"Archivos eliminados: {undeploy_result.get('deleted_files', [])}")

    # Eliminar de la base de datos
    await db.delete(module)
    await db.commit()

    return {
        "message": f"Módulo '{module_id}' eliminado exitosamente",
        "files_deleted": (
            undeploy_result.get("deleted_files", [])
            if module.status == ModuleStatus.ACTIVE.value
            else []
        ),
    }


@router.post("/modules/{module_id}/undeploy")
async def undeploy_module(
    module_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Desactiva un módulo desplegado (elimina archivos pero mantiene definición)
    """
    from app.services.module_deployer import ModuleDeployer

    result = await db.execute(
        select(CustomModule).where(CustomModule.module_id == module_id)
    )
    module = result.scalar_one_or_none()
    if not module:
        raise HTTPException(
            status_code=404, detail=f"Módulo '{module_id}' no encontrado"
        )

    if module.status != ModuleStatus.ACTIVE.value:
        raise HTTPException(
            status_code=400,
            detail=f"Módulo no está desplegado (estado: {module.status})",
        )

    # Eliminar archivos físicos
    deployer = ModuleDeployer()
    undeploy_result = await deployer.undeploy_module(module_id)

    # Actualizar estado
    module.status = ModuleStatus.INACTIVE.value
    await db.commit()

    return {
        "message": f"Módulo '{module_id}' desactivado exitosamente",
        "result": undeploy_result,
    }


@router.post("/reload-modules")
async def reload_generated_modules(
    current_user: Usuario = Depends(get_current_user),
):
    """
    Recarga dinámicamente todos los módulos generados
    Útil después de desplegar nuevos módulos sin reiniciar el servidor
    """
    from app.services.module_deployer import ModuleDeployer
    from fastapi import Request

    # Nota: Esto requiere acceso a la instancia de FastAPI
    # Por ahora retornamos información sobre los módulos disponibles
    deployer = ModuleDeployer()

    # Listar archivos generados
    models = (
        list(deployer.models_dir.glob("*.py")) if deployer.models_dir.exists() else []
    )
    endpoints = list(deployer.api_dir.glob("*.py")) if deployer.api_dir.exists() else []

    return {
        "message": "Para aplicar cambios, reinicia el servidor o usa hot-reload",
        "generated_models": [f.stem for f in models if f.name != "__init__.py"],
        "generated_endpoints": [f.stem for f in endpoints if f.name != "__init__.py"],
        "note": "Los módulos se cargarán automáticamente en el próximo reinicio",
    }


@router.post("/modules/{module_id}/preview", response_model=CodePreview)
async def preview_code(
    module_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(
        select(CustomModule).where(CustomModule.module_id == module_id)
    )
    module = result.scalar_one_or_none()
    if not module:
        raise HTTPException(
            status_code=404, detail=f"Módulo '{module_id}' no encontrado"
        )

    definition = module.definition or {}
    preview = CodePreview()

    if definition.get("models"):
        first_model = definition["models"][0]
        model_def = {
            "module_name": module.name,
            "name": first_model["name"],
            "table_name": first_model["table_name"],
            "description": first_model.get("description", ""),
            "fields": first_model["fields"],
            "relationships": first_model.get("relationships", []),
        }
        preview.model_code = CodeGenerator.generate_model_code(model_def)
        preview.migration_sql = CodeGenerator.generate_migration_sql(model_def)

        endpoint_def = {
            "module_name": module.name,
            "model_name": first_model["name"],
            "path": first_model["table_name"],
            "fields": first_model["fields"],
        }
        preview.endpoint_code = CodeGenerator.generate_endpoint_code(endpoint_def)

        component_def = {
            "module_name": module.name,
            "model_name": first_model["name"],
            "component_name": f"{first_model['name']}Page",
            "title": module.name,
            "endpoint_path": first_model["table_name"],
            "fields": first_model["fields"],
        }
        preview.component_code = CodeGenerator.generate_react_component(component_def)

    return preview


@router.post("/modules/{module_id}/deploy")
async def deploy_module(
    module_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Despliega un módulo completo:
    - Genera código de modelos, endpoints y componentes
    - Escribe archivos físicos
    - Ejecuta migraciones SQL
    - Actualiza estado del módulo
    """
    from app.services.module_deployer import ModuleDeployer

    result = await db.execute(
        select(CustomModule).where(CustomModule.module_id == module_id)
    )
    module = result.scalar_one_or_none()
    if not module:
        raise HTTPException(
            status_code=404, detail=f"Módulo '{module_id}' no encontrado"
        )

    # Usar el nuevo servicio de despliegue
    deployer = ModuleDeployer()
    definition = module.definition or {}

    try:
        # Desplegar módulo (escribe archivos y ejecuta migraciones)
        deployment_result = await deployer.deploy_module(definition, db)

        # Guardar resultado en el módulo
        module.generated_code = deployment_result
        module.status = ModuleStatus.ACTIVE.value
        module.deployed_at = datetime.utcnow()

        # Crear registro de despliegue
        deployment = ModuleDeployment(
            module_id=module.id,
            version=module.version,
            status="success" if not deployment_result.get("errors") else "partial",
            deployed_by_id=current_user.id,
            deployment_log=f"Módulo desplegado. Modelos: {len(deployment_result['models'])}, Endpoints: {len(deployment_result['endpoints'])}, Componentes: {len(deployment_result['components'])}",
            error_log=(
                "\n".join(deployment_result.get("errors", []))
                if deployment_result.get("errors")
                else None
            ),
            completed_at=datetime.utcnow(),
        )
        db.add(deployment)

        await db.commit()
        await db.refresh(module)

        return {
            "message": (
                "Módulo desplegado exitosamente"
                if not deployment_result.get("errors")
                else "Módulo desplegado con advertencias"
            ),
            "result": deployment_result,
            "module_status": module.status,
            "deployed_at": (
                module.deployed_at.isoformat() if module.deployed_at else None
            ),
        }

    except Exception as e:
        logger.error(f"Error desplegando módulo {module_id}: {e}")

        # Registrar despliegue fallido
        deployment = ModuleDeployment(
            module_id=module.id,
            version=module.version,
            status="failed",
            deployed_by_id=current_user.id,
            deployment_log=f"Error desplegando módulo",
            error_log=str(e),
            completed_at=datetime.utcnow(),
        )
        db.add(deployment)
        await db.commit()

        raise HTTPException(
            status_code=500, detail=f"Error desplegando módulo: {str(e)}"
        )


# catálogos públicos
@router.get("/categories")
async def get_categories():
    return {
        "categories": [
            {"id": "clinical", "name": "Clínico", "icon": "Stethoscope"},
            {"id": "administrative", "name": "Administrativo", "icon": "Briefcase"},
            {"id": "laboratory", "name": "Laboratorio", "icon": "Flask"},
            {"id": "imaging", "name": "Imagenología", "icon": "Image"},
            {"id": "pharmacy", "name": "Farmacia", "icon": "Pill"},
            {"id": "billing", "name": "Facturación", "icon": "DollarSign"},
            {"id": "custom", "name": "Personalizado", "icon": "Wrench"},
        ]
    }


@router.get("/field-types")
async def get_field_types():
    return {
        "types": [
            {"id": "string", "name": "Texto Corto", "icon": "Type"},
            {"id": "text", "name": "Texto Largo", "icon": "AlignLeft"},
            {"id": "integer", "name": "Número Entero", "icon": "Hash"},
            {"id": "float", "name": "Número Decimal", "icon": "Hash"},
            {"id": "boolean", "name": "Verdadero/Falso", "icon": "ToggleLeft"},
            {"id": "date", "name": "Fecha", "icon": "Calendar"},
            {"id": "datetime", "name": "Fecha y Hora", "icon": "Clock"},
            {"id": "uuid", "name": "UUID", "icon": "Key"},
            {"id": "json", "name": "JSON", "icon": "Braces"},
        ]
    }
