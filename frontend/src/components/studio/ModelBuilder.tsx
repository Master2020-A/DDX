/**
 * Constructor Visual de Modelos de Datos
 * Permite crear tablas y campos mediante interfaz drag-and-drop
 */
import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Checkbox,
  FormControlLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import { Plus, Trash2, Edit, Database, Type } from 'lucide-react';

interface Field {
  name: string;
  type: string;
  label: string;
  required: boolean;
  nullable: boolean;
  unique: boolean;
  indexed: boolean;
  show_in_table: boolean;
  show_in_form: boolean;
}

interface ModelDefinition {
  name: string;
  table_name: string;
  description: string;
  fields: Field[];
}

interface ModelBuilderProps {
  onSave: (model: ModelDefinition) => void;
  initialModel?: ModelDefinition;
}

const FIELD_TYPES = [
  { id: 'string', name: 'Texto Corto', icon: 'Type' },
  { id: 'text', name: 'Texto Largo', icon: 'AlignLeft' },
  { id: 'integer', name: 'Número Entero', icon: 'Hash' },
  { id: 'float', name: 'Número Decimal', icon: 'Hash' },
  { id: 'boolean', name: 'Verdadero/Falso', icon: 'ToggleLeft' },
  { id: 'date', name: 'Fecha', icon: 'Calendar' },
  { id: 'datetime', name: 'Fecha y Hora', icon: 'Clock' },
  { id: 'uuid', name: 'UUID', icon: 'Key' },
  { id: 'json', name: 'JSON', icon: 'Braces' }
];

export default function ModelBuilder({ onSave, initialModel }: ModelBuilderProps) {
  const [model, setModel] = useState<ModelDefinition>(
    initialModel || {
      name: '',
      table_name: '',
      description: '',
      fields: []
    }
  );
  
  const [fieldDialogOpen, setFieldDialogOpen] = useState(false);
  const [editingField, setEditingField] = useState<Field | null>(null);
  const [editingIndex, setEditingIndex] = useState<number>(-1);
  const [newField, setNewField] = useState<Field>({
    name: '',
    type: 'string',
    label: '',
    required: false,
    nullable: true,
    unique: false,
    indexed: false,
    show_in_table: true,
    show_in_form: true
  });

  const handleAddField = () => {
    setNewField({
      name: '',
      type: 'string',
      label: '',
      required: false,
      nullable: true,
      unique: false,
      indexed: false,
      show_in_table: true,
      show_in_form: true
    });
    setEditingField(null);
    setEditingIndex(-1);
    setFieldDialogOpen(true);
  };

  const handleEditField = (field: Field, index: number) => {
    setNewField({ ...field });
    setEditingField(field);
    setEditingIndex(index);
    setFieldDialogOpen(true);
  };

  const handleSaveField = () => {
    if (!newField.name || !newField.type) {
      alert('El nombre y tipo de campo son requeridos');
      return;
    }

    const updatedFields = [...model.fields];
    
    if (editingIndex >= 0) {
      updatedFields[editingIndex] = newField;
    } else {
      updatedFields.push(newField);
    }

    setModel({ ...model, fields: updatedFields });
    setFieldDialogOpen(false);
  };

  const handleDeleteField = (index: number) => {
    if (!confirm('¿Eliminar este campo?')) return;
    
    const updatedFields = model.fields.filter((_, i) => i !== index);
    setModel({ ...model, fields: updatedFields });
  };

  const handleNameChange = (name: string) => {
    const tableName = name.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
    setModel({ ...model, name, table_name: tableName });
  };

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      string: '#3B82F6',
      text: '#8B5CF6',
      integer: '#10B981',
      float: '#059669',
      boolean: '#F59E0B',
      date: '#EC4899',
      datetime: '#EF4444',
      uuid: '#6366F1',
      json: '#14B8A6'
    };
    return colors[type] || '#6B7280';
  };

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Database size={24} style={{ marginRight: 8 }} />
          <Typography variant="h6">Definición del Modelo</Typography>
        </Box>

        <TextField
          fullWidth
          margin="normal"
          label="Nombre del Modelo"
          placeholder="ej: Vacuna"
          value={model.name}
          onChange={(e) => handleNameChange(e.target.value)}
          helperText="Nombre en formato PascalCase (ej: Vacuna, HistorialVacunacion)"
        />

        <TextField
          fullWidth
          margin="normal"
          label="Nombre de la Tabla"
          placeholder="ej: vacunas"
          value={model.table_name}
          onChange={(e) => setModel({ ...model, table_name: e.target.value })}
          helperText="Nombre de la tabla en la base de datos (generado automáticamente)"
          disabled
        />

        <TextField
          fullWidth
          margin="normal"
          label="Descripción"
          placeholder="Descripción del modelo"
          multiline
          rows={2}
          value={model.description}
          onChange={(e) => setModel({ ...model, description: e.target.value })}
        />
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Campos ({model.fields.length})</Typography>
          <Button
            variant="contained"
            startIcon={<Plus />}
            onClick={handleAddField}
          >
            Agregar Campo
          </Button>
        </Box>

        {model.fields.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Type size={48} style={{ opacity: 0.3, margin: '0 auto' }} />
            <Typography color="text.secondary" sx={{ mt: 2 }}>
              No hay campos definidos. Agrega el primer campo.
            </Typography>
          </Box>
        ) : (
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Nombre</TableCell>
                  <TableCell>Tipo</TableCell>
                  <TableCell>Etiqueta</TableCell>
                  <TableCell>Opciones</TableCell>
                  <TableCell align="right">Acciones</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {model.fields.map((field, index) => (
                  <TableRow key={index}>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {field.name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={FIELD_TYPES.find(t => t.id === field.type)?.name || field.type}
                        size="small"
                        sx={{ 
                          bgcolor: getTypeColor(field.type),
                          color: 'white'
                        }}
                      />
                    </TableCell>
                    <TableCell>{field.label || field.name}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {field.required && <Chip label="Requerido" size="small" color="error" variant="outlined" />}
                        {field.unique && <Chip label="Único" size="small" color="warning" variant="outlined" />}
                        {field.indexed && <Chip label="Indexado" size="small" color="info" variant="outlined" />}
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      <IconButton size="small" onClick={() => handleEditField(field, index)}>
                        <Edit size={16} />
                      </IconButton>
                      <IconButton size="small" color="error" onClick={() => handleDeleteField(index)}>
                        <Trash2 size={16} />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            size="large"
            onClick={() => onSave(model)}
            disabled={!model.name || model.fields.length === 0}
          >
            Guardar Modelo
          </Button>
        </Box>
      </Paper>

      {/* Diálogo: Agregar/Editar Campo */}
      <Dialog open={fieldDialogOpen} onClose={() => setFieldDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingField ? 'Editar Campo' : 'Nuevo Campo'}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            margin="normal"
            label="Nombre del Campo"
            placeholder="ej: nombre_vacuna"
            value={newField.name}
            onChange={(e) => setNewField({ ...newField, name: e.target.value })}
            helperText="Nombre en snake_case (ej: nombre_vacuna, fecha_aplicacion)"
          />

          <FormControl fullWidth margin="normal">
            <InputLabel>Tipo de Dato</InputLabel>
            <Select
              value={newField.type}
              onChange={(e) => setNewField({ ...newField, type: e.target.value })}
              label="Tipo de Dato"
            >
              {FIELD_TYPES.map(type => (
                <MenuItem key={type.id} value={type.id}>{type.name}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            fullWidth
            margin="normal"
            label="Etiqueta"
            placeholder="ej: Nombre de la Vacuna"
            value={newField.label}
            onChange={(e) => setNewField({ ...newField, label: e.target.value })}
            helperText="Etiqueta que se mostrará en formularios"
          />

          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>Opciones</Typography>
            
            <FormControlLabel
              control={
                <Checkbox
                  checked={newField.required}
                  onChange={(e) => setNewField({ ...newField, required: e.target.checked, nullable: !e.target.checked })}
                />
              }
              label="Campo requerido"
            />

            <FormControlLabel
              control={
                <Checkbox
                  checked={newField.unique}
                  onChange={(e) => setNewField({ ...newField, unique: e.target.checked })}
                />
              }
              label="Valor único"
            />

            <FormControlLabel
              control={
                <Checkbox
                  checked={newField.indexed}
                  onChange={(e) => setNewField({ ...newField, indexed: e.target.checked })}
                />
              }
              label="Crear índice"
            />

            <FormControlLabel
              control={
                <Checkbox
                  checked={newField.show_in_table}
                  onChange={(e) => setNewField({ ...newField, show_in_table: e.target.checked })}
                />
              }
              label="Mostrar en tabla"
            />

            <FormControlLabel
              control={
                <Checkbox
                  checked={newField.show_in_form}
                  onChange={(e) => setNewField({ ...newField, show_in_form: e.target.checked })}
                />
              }
              label="Mostrar en formulario"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFieldDialogOpen(false)}>Cancelar</Button>
          <Button onClick={handleSaveField} variant="contained">
            {editingField ? 'Actualizar' : 'Agregar'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
