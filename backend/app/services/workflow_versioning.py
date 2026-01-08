"""
Sistema de versionado de workflows
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from app.models.workflow import Workflow
from app.models.workflow_advanced import WorkflowVersion


class WorkflowVersioningService:
    """Servicio para gestión de versiones de workflows"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_version(
        self,
        workflow_id: UUID,
        version_number: str,
        version_name: Optional[str] = None,
        changes_description: Optional[str] = None,
        breaking_changes: bool = False,
        created_by_id: Optional[UUID] = None,
        auto_publish: bool = False,
    ) -> WorkflowVersion:
        """
        Crea una nueva versión del workflow

        Args:
            workflow_id: ID del workflow
            version_number: Número de versión (ej: "1.0.0", "1.1.0")
            version_name: Nombre descriptivo de la versión
            changes_description: Descripción de los cambios
            breaking_changes: Si esta versión rompe compatibilidad
            created_by_id: Usuario que crea la versión
            auto_publish: Si se debe publicar automáticamente
        """
        # Obtener el workflow actual
        result = await self.db.execute(
            select(Workflow).where(Workflow.id == workflow_id)
        )
        workflow = result.scalar_one_or_none()

        if not workflow:
            raise ValueError(f"Workflow {workflow_id} no encontrado")

        # Crear snapshot de la versión actual
        new_version = WorkflowVersion(
            workflow_id=workflow_id,
            version_number=version_number,
            version_name=version_name or f"Versión {version_number}",
            nodes=workflow.nodes,
            edges=workflow.edges,
            config=workflow.config,
            variables=workflow.variables,
            changes_description=changes_description,
            breaking_changes=breaking_changes,
            created_by_id=created_by_id,
            is_published=auto_publish,
        )

        # Si se auto-publica, marcar como current
        if auto_publish:
            # Desmarcar la versión actual anterior
            await self._unset_current_version(workflow_id)
            new_version.is_current = True
            new_version.published_at = datetime.utcnow()

        self.db.add(new_version)
        await self.db.commit()
        await self.db.refresh(new_version)

        return new_version

    async def publish_version(
        self, version_id: UUID, set_as_current: bool = True
    ) -> WorkflowVersion:
        """
        Publica una versión y opcionalmente la marca como actual
        """
        result = await self.db.execute(
            select(WorkflowVersion).where(WorkflowVersion.id == version_id)
        )
        version = result.scalar_one_or_none()

        if not version:
            raise ValueError(f"Versión {version_id} no encontrada")

        if version.is_published:
            raise ValueError("Esta versión ya está publicada")

        version.is_published = True
        version.published_at = datetime.utcnow()

        if set_as_current:
            # Desmarcar versión actual anterior
            await self._unset_current_version(version.workflow_id)
            version.is_current = True

        await self.db.commit()
        await self.db.refresh(version)

        return version

    async def rollback_to_version(
        self, workflow_id: UUID, version_id: UUID
    ) -> Workflow:
        """
        Revierte el workflow a una versión anterior
        """
        # Obtener la versión
        result = await self.db.execute(
            select(WorkflowVersion).where(WorkflowVersion.id == version_id)
        )
        version = result.scalar_one_or_none()

        if not version:
            raise ValueError(f"Versión {version_id} no encontrada")

        if version.workflow_id != workflow_id:
            raise ValueError("La versión no pertenece a este workflow")

        # Obtener el workflow
        result = await self.db.execute(
            select(Workflow).where(Workflow.id == workflow_id)
        )
        workflow = result.scalar_one_or_none()

        if not workflow:
            raise ValueError(f"Workflow {workflow_id} no encontrado")

        # Restaurar el snapshot de la versión
        workflow.nodes = version.nodes
        workflow.edges = version.edges
        workflow.config = version.config
        workflow.variables = version.variables
        workflow.updated_at = datetime.utcnow()

        # Marcar esta versión como actual
        await self._unset_current_version(workflow_id)
        version.is_current = True

        await self.db.commit()
        await self.db.refresh(workflow)

        return workflow

    async def get_version(self, version_id: UUID) -> Optional[WorkflowVersion]:
        """Obtiene una versión específica"""
        result = await self.db.execute(
            select(WorkflowVersion).where(WorkflowVersion.id == version_id)
        )
        return result.scalar_one_or_none()

    async def get_workflow_versions(
        self, workflow_id: UUID, published_only: bool = False
    ) -> List[WorkflowVersion]:
        """
        Obtiene todas las versiones de un workflow
        """
        query = select(WorkflowVersion).where(
            WorkflowVersion.workflow_id == workflow_id
        )

        if published_only:
            query = query.where(WorkflowVersion.is_published == True)

        query = query.order_by(desc(WorkflowVersion.created_at))

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_current_version(self, workflow_id: UUID) -> Optional[WorkflowVersion]:
        """Obtiene la versión actual de un workflow"""
        result = await self.db.execute(
            select(WorkflowVersion).where(
                and_(
                    WorkflowVersion.workflow_id == workflow_id,
                    WorkflowVersion.is_current == True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def compare_versions(
        self, version_a_id: UUID, version_b_id: UUID
    ) -> Dict[str, Any]:
        """
        Compara dos versiones y retorna las diferencias
        """
        # Obtener ambas versiones
        result = await self.db.execute(
            select(WorkflowVersion).where(
                WorkflowVersion.id.in_([version_a_id, version_b_id])
            )
        )
        versions = result.scalars().all()

        if len(versions) != 2:
            raise ValueError("No se encontraron ambas versiones")

        version_a = next(v for v in versions if v.id == version_a_id)
        version_b = next(v for v in versions if v.id == version_b_id)

        # Comparar nodos
        nodes_a = {n["id"]: n for n in version_a.nodes}
        nodes_b = {n["id"]: n for n in version_b.nodes}

        nodes_added = [n for nid, n in nodes_b.items() if nid not in nodes_a]
        nodes_removed = [n for nid, n in nodes_a.items() if nid not in nodes_b]
        nodes_modified = []

        for nid in set(nodes_a.keys()) & set(nodes_b.keys()):
            if nodes_a[nid] != nodes_b[nid]:
                nodes_modified.append(
                    {"id": nid, "before": nodes_a[nid], "after": nodes_b[nid]}
                )

        # Comparar edges
        edges_a = set(tuple(e.items()) for e in version_a.edges)
        edges_b = set(tuple(e.items()) for e in version_b.edges)

        edges_added = [dict(e) for e in edges_b - edges_a]
        edges_removed = [dict(e) for e in edges_a - edges_b]

        return {
            "version_a": {
                "id": str(version_a.id),
                "version_number": version_a.version_number,
                "version_name": version_a.version_name,
            },
            "version_b": {
                "id": str(version_b.id),
                "version_number": version_b.version_number,
                "version_name": version_b.version_name,
            },
            "nodes": {
                "added": nodes_added,
                "removed": nodes_removed,
                "modified": nodes_modified,
            },
            "edges": {"added": edges_added, "removed": edges_removed},
            "summary": {
                "total_changes": len(nodes_added)
                + len(nodes_removed)
                + len(nodes_modified)
                + len(edges_added)
                + len(edges_removed),
                "nodes_changed": len(nodes_added)
                + len(nodes_removed)
                + len(nodes_modified),
                "edges_changed": len(edges_added) + len(edges_removed),
            },
        }

    async def deprecate_version(self, version_id: UUID) -> WorkflowVersion:
        """Marca una versión como deprecada"""
        result = await self.db.execute(
            select(WorkflowVersion).where(WorkflowVersion.id == version_id)
        )
        version = result.scalar_one_or_none()

        if not version:
            raise ValueError(f"Versión {version_id} no encontrada")

        if version.is_current:
            raise ValueError("No se puede deprecar la versión actual")

        version.deprecated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(version)

        return version

    async def update_version_metrics(
        self,
        version_id: UUID,
        execution_count: Optional[int] = None,
        success_rate: Optional[float] = None,
        avg_duration_ms: Optional[int] = None,
        error_count: Optional[int] = None,
    ) -> WorkflowVersion:
        """Actualiza las métricas de una versión"""
        result = await self.db.execute(
            select(WorkflowVersion).where(WorkflowVersion.id == version_id)
        )
        version = result.scalar_one_or_none()

        if not version:
            raise ValueError(f"Versión {version_id} no encontrada")

        if execution_count is not None:
            version.execution_count = execution_count
        if success_rate is not None:
            version.success_rate = success_rate
        if avg_duration_ms is not None:
            version.avg_duration_ms = avg_duration_ms
        if error_count is not None:
            version.error_count = error_count

        await self.db.commit()
        await self.db.refresh(version)

        return version

    async def _unset_current_version(self, workflow_id: UUID):
        """Desmarca la versión actual de un workflow"""
        result = await self.db.execute(
            select(WorkflowVersion).where(
                and_(
                    WorkflowVersion.workflow_id == workflow_id,
                    WorkflowVersion.is_current == True,
                )
            )
        )
        current_version = result.scalar_one_or_none()

        if current_version:
            current_version.is_current = False
            await self.db.commit()

    async def auto_version(
        self, workflow_id: UUID, created_by_id: Optional[UUID] = None
    ) -> WorkflowVersion:
        """
        Crea automáticamente una nueva versión incrementando el número
        """
        # Obtener la última versión
        versions = await self.get_workflow_versions(workflow_id)

        if not versions:
            # Primera versión
            version_number = "1.0.0"
        else:
            # Incrementar versión minor
            last_version = versions[0].version_number
            parts = last_version.split(".")

            try:
                major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
                version_number = f"{major}.{minor + 1}.{patch}"
            except:
                # Si el formato no es estándar, agregar .1
                version_number = f"{last_version}.1"

        return await self.create_version(
            workflow_id=workflow_id,
            version_number=version_number,
            version_name=f"Versión {version_number}",
            created_by_id=created_by_id,
        )
