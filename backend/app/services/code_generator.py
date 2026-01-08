"""
Motor de generación de código para DDX Studio
Genera código Python (SQLAlchemy, FastAPI) y TypeScript (React) desde metadata
"""

from typing import Dict, List, Any
from jinja2 import Template
import json


class CodeGenerator:
    """Generador de código desde metadata"""

    # Template para modelo SQLAlchemy
    MODEL_TEMPLATE = '''"""
Modelo generado automáticamente por DDX Studio
Módulo: {{ module_name }}
"""
from sqlalchemy import Column, String, DateTime, Integer, Boolean, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class {{ model_name }}(Base):
    """{{ description }}"""
    __tablename__ = "{{ table_name }}"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    {% for field in fields %}
    {{ field.name }} = Column({{ field.column_type }}{{ ', nullable=' + field.nullable|string if field.nullable is defined }}{{ ', unique=' + field.unique|string if field.unique }})
    {%- endfor %}
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    {% if relationships %}
    
    # Relaciones
    {% for rel in relationships %}
    {{ rel.name }} = relationship("{{ rel.target_model }}"{{ ', back_populates="' + rel.back_populates + '"' if rel.back_populates }})
    {%- endfor %}
    {% endif %}
'''

    # Template para endpoint FastAPI
    ENDPOINT_TEMPLATE = '''"""
Endpoints generados automáticamente por DDX Studio
Módulo: {{ module_name }}
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.usuario import Usuario
from app.models.{{ model_file }} import {{ model_name }}

router = APIRouter()


# Schemas
class {{ model_name }}Create(BaseModel):
    """Schema para crear {{ model_name }}"""
    {% for field in create_fields %}
    {{ field.name }}: {{ field.python_type }}{{ ' = None' if not field.required }}
    {%- endfor %}


class {{ model_name }}Response(BaseModel):
    """Schema de respuesta para {{ model_name }}"""
    id: UUID
    {% for field in response_fields %}
    {{ field.name }}: {{ field.python_type }}
    {%- endfor %}
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# Endpoints
@router.post("/{{ endpoint_path }}", response_model={{ model_name }}Response)
async def create_{{ model_name_lower }}(
    data: {{ model_name }}Create,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Crear nuevo {{ model_name }}"""
    new_item = {{ model_name }}(**data.dict())
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return new_item


@router.get("/{{ endpoint_path }}", response_model=List[{{ model_name }}Response])
async def list_{{ model_name_lower }}(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar {{ model_name }}"""
    result = await db.execute(
        select({{ model_name }}).offset(skip).limit(limit)
    )
    items = result.scalars().all()
    return items


@router.get("/{{ endpoint_path }}/{item_id}", response_model={{ model_name }}Response)
async def get_{{ model_name_lower }}(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener {{ model_name }} por ID"""
    result = await db.execute(
        select({{ model_name }}).where({{ model_name }}.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{{ model_name }} no encontrado"
        )
    
    return item


@router.put("/{{ endpoint_path }}/{item_id}", response_model={{ model_name }}Response)
async def update_{{ model_name_lower }}(
    item_id: UUID,
    data: {{ model_name }}Create,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Actualizar {{ model_name }}"""
    result = await db.execute(
        select({{ model_name }}).where({{ model_name }}.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{{ model_name }} no encontrado"
        )
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(item, key, value)
    
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{{ endpoint_path }}/{item_id}")
async def delete_{{ model_name_lower }}(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Eliminar {{ model_name }}"""
    result = await db.execute(
        select({{ model_name }}).where({{ model_name }}.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{{ model_name }} no encontrado"
        )
    
    await db.delete(item)
    await db.commit()
    
    return {"message": "{{ model_name }} eliminado exitosamente"}
'''

    # Template para componente React
    REACT_COMPONENT_TEMPLATE = """/**
 * Componente generado automáticamente por DDX Studio
 * Módulo: {{ module_name }}
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress
} from '@mui/material';
import { Add, Edit, Delete } from '@mui/icons-material';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8612';

interface {{ model_name }} {
  id: string;
  {% for field in fields %}
  {{ field.name }}: {{ field.ts_type }};
  {%- endfor %}
  created_at: string;
  updated_at: string;
}

export default function {{ component_name }}() {
  const [items, setItems] = useState<{{ model_name }}[]>([]);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState<Partial<{{ model_name }}>>({});

  useEffect(() => {
    loadItems();
  }, []);

  const loadItems = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/{{ endpoint_path }}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setItems(response.data);
    } catch (error) {
      console.error('Error cargando datos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/api/{{ endpoint_path }}`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDialogOpen(false);
      setFormData({});
      loadItems();
    } catch (error) {
      console.error('Error guardando:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('¿Está seguro de eliminar este registro?')) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/api/{{ endpoint_path }}/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      loadItems();
    } catch (error) {
      console.error('Error eliminando:', error);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h4">{{ title }}</Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setDialogOpen(true)}
          >
            Nuevo
          </Button>
        </Box>

        {loading ? (
          <CircularProgress />
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  {% for field in table_fields %}
                  <TableCell>{{ field.label }}</TableCell>
                  {%- endfor %}
                  <TableCell>Acciones</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {items.map((item) => (
                  <TableRow key={item.id}>
                    {% for field in table_fields %}
                    <TableCell>{item.{{ field.name }}}</TableCell>
                    {%- endfor %}
                    <TableCell>
                      <Button size="small" onClick={() => handleDelete(item.id)}>
                        <Delete />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Nuevo {{ title }}</DialogTitle>
          <DialogContent>
            {% for field in form_fields %}
            <TextField
              fullWidth
              margin="normal"
              label="{{ field.label }}"
              type="{{ field.input_type }}"
              value={formData.{{ field.name }} || ''}
              onChange={(e) => setFormData({ ...formData, {{ field.name }}: e.target.value })}
            />
            {%- endfor %}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>Cancelar</Button>
            <Button onClick={handleSubmit} variant="contained">Guardar</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
}
"""

    @staticmethod
    def generate_model_code(model_definition: Dict[str, Any]) -> str:
        """Generar código SQLAlchemy desde definición de modelo"""
        template = Template(CodeGenerator.MODEL_TEMPLATE)

        # Mapear tipos de datos
        type_mapping = {
            "string": "String(255)",
            "text": "Text",
            "integer": "Integer",
            "float": "Float",
            "boolean": "Boolean",
            "date": "Date",
            "datetime": "DateTime",
            "uuid": "UUID(as_uuid=True)",
            "json": "JSONB",
        }

        # Preparar campos
        fields = []
        for field in model_definition.get("fields", []):
            fields.append(
                {
                    "name": field["name"],
                    "column_type": type_mapping.get(field["type"], "String(255)"),
                    "nullable": field.get("nullable", True),
                    "unique": field.get("unique", False),
                }
            )

        return template.render(
            module_name=model_definition.get("module_name", "CustomModule"),
            model_name=model_definition["name"],
            table_name=model_definition["table_name"],
            description=model_definition.get("description", ""),
            fields=fields,
            relationships=model_definition.get("relationships", []),
        )

    @staticmethod
    def generate_endpoint_code(endpoint_definition: Dict[str, Any]) -> str:
        """Generar código FastAPI desde definición de endpoint"""
        template = Template(CodeGenerator.ENDPOINT_TEMPLATE)

        # Mapear tipos Python
        type_mapping = {
            "string": "str",
            "text": "str",
            "integer": "int",
            "float": "float",
            "boolean": "bool",
            "date": "str",
            "datetime": "str",
            "uuid": "UUID",
            "json": "dict",
        }

        model_name = endpoint_definition["model_name"]
        fields = endpoint_definition.get("fields", [])

        create_fields = []
        response_fields = []

        for field in fields:
            field_def = {
                "name": field["name"],
                "python_type": type_mapping.get(field["type"], "str"),
                "required": field.get("required", False),
            }
            create_fields.append(field_def)
            response_fields.append(field_def)

        return template.render(
            module_name=endpoint_definition.get("module_name", "CustomModule"),
            model_name=model_name,
            model_name_lower=model_name.lower(),
            model_file=model_name.lower(),
            endpoint_path=endpoint_definition.get("path", model_name.lower()),
            create_fields=create_fields,
            response_fields=response_fields,
        )

    @staticmethod
    def generate_react_component(component_definition: Dict[str, Any]) -> str:
        """Generar componente React desde definición"""
        template = Template(CodeGenerator.REACT_COMPONENT_TEMPLATE)

        # Mapear tipos TypeScript
        type_mapping = {
            "string": "string",
            "text": "string",
            "integer": "number",
            "float": "number",
            "boolean": "boolean",
            "date": "string",
            "datetime": "string",
            "uuid": "string",
            "json": "any",
        }

        fields = []
        table_fields = []
        form_fields = []

        for field in component_definition.get("fields", []):
            field_def = {
                "name": field["name"],
                "ts_type": type_mapping.get(field["type"], "string"),
                "label": field.get("label", field["name"].replace("_", " ").title()),
                "input_type": (
                    "number" if field["type"] in ["integer", "float"] else "text"
                ),
            }
            fields.append(field_def)

            if field.get("show_in_table", True):
                table_fields.append(field_def)

            if field.get("show_in_form", True):
                form_fields.append(field_def)

        return template.render(
            module_name=component_definition.get("module_name", "CustomModule"),
            model_name=component_definition["model_name"],
            component_name=component_definition.get(
                "component_name", f"{component_definition['model_name']}Page"
            ),
            title=component_definition.get("title", component_definition["model_name"]),
            endpoint_path=component_definition.get(
                "endpoint_path", component_definition["model_name"].lower()
            ),
            fields=fields,
            table_fields=table_fields,
            form_fields=form_fields,
        )

    @staticmethod
    def generate_migration_sql(model_definition: Dict[str, Any]) -> str:
        """Generar SQL de migración para crear tabla"""
        type_mapping = {
            "string": "VARCHAR(255)",
            "text": "TEXT",
            "integer": "INTEGER",
            "float": "FLOAT",
            "boolean": "BOOLEAN",
            "date": "DATE",
            "datetime": "TIMESTAMP",
            "uuid": "UUID",
            "json": "JSONB",
        }

        table_name = model_definition["table_name"]
        fields = model_definition.get("fields", [])

        sql = f"-- Migración generada por DDX Studio\n"
        sql += f"-- Tabla: {table_name}\n\n"
        sql += f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        sql += "    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n"

        for field in fields:
            sql_type = type_mapping.get(field["type"], "VARCHAR(255)")
            nullable = "" if field.get("nullable", True) else " NOT NULL"
            unique = " UNIQUE" if field.get("unique", False) else ""
            sql += f"    {field['name']} {sql_type}{nullable}{unique},\n"

        sql += "    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,\n"
        sql += "    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP\n"
        sql += ");\n\n"

        # Índices
        for field in fields:
            if field.get("indexed", False):
                sql += f"CREATE INDEX IF NOT EXISTS idx_{table_name}_{field['name']} ON {table_name}({field['name']});\n"

        return sql
