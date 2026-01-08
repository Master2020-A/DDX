/**
 * Constructor Visual de Endpoints API
 * Permite crear endpoints REST mediante interfaz visual
 */
import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Checkbox,
  FormControlLabel,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Chip
} from '@mui/material';
import { Zap } from 'lucide-react';

interface EndpointDefinition {
  name: string;
  path: string;
  method: string;
  description: string;
  auth_required: boolean;
  handler_type: string;
  model_name: string;
}

interface EndpointBuilderProps {
  onSave: (endpoint: EndpointDefinition) => void;
  modelName?: string;
}

const HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'];
const HANDLER_TYPES = [
  { id: 'crud', name: 'CRUD Automático', description: 'Crear, Leer, Actualizar, Eliminar' },
  { id: 'list', name: 'Listar', description: 'Obtener lista de registros' },
  { id: 'detail', name: 'Detalle', description: 'Obtener un registro por ID' },
  { id: 'create', name: 'Crear', description: 'Crear nuevo registro' },
  { id: 'update', name: 'Actualizar', description: 'Actualizar registro existente' },
  { id: 'delete', name: 'Eliminar', description: 'Eliminar registro' },
  { id: 'custom', name: 'Personalizado', description: 'Lógica personalizada' }
];

export default function EndpointBuilder({ onSave, modelName }: EndpointBuilderProps) {
  const [endpoint, setEndpoint] = useState<EndpointDefinition>({
    name: modelName ? `${modelName} CRUD` : '',
    path: modelName ? `/${modelName.toLowerCase()}` : '',
    method: 'GET',
    description: '',
    auth_required: true,
    handler_type: 'crud',
    model_name: modelName || ''
  });

  const getMethodColor = (method: string) => {
    const colors: Record<string, string> = {
      GET: '#10B981',
      POST: '#3B82F6',
      PUT: '#F59E0B',
      DELETE: '#EF4444',
      PATCH: '#8B5CF6'
    };
    return colors[method] || '#6B7280';
  };

  return (
    <Box>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Zap size={24} style={{ marginRight: 8 }} />
          <Typography variant="h6">Definición del Endpoint</Typography>
        </Box>

        <TextField
          fullWidth
          margin="normal"
          label="Nombre del Endpoint"
          placeholder="ej: Listar Vacunas"
          value={endpoint.name}
          onChange={(e) => setEndpoint({ ...endpoint, name: e.target.value })}
        />

        <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Método HTTP</InputLabel>
            <Select
              value={endpoint.method}
              onChange={(e) => setEndpoint({ ...endpoint, method: e.target.value })}
              label="Método HTTP"
            >
              {HTTP_METHODS.map(method => (
                <MenuItem key={method} value={method}>
                  <Chip
                    label={method}
                    size="small"
                    sx={{ bgcolor: getMethodColor(method), color: 'white' }}
                  />
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            fullWidth
            label="Ruta del Endpoint"
            placeholder="/api/vacunas"
            value={endpoint.path}
            onChange={(e) => setEndpoint({ ...endpoint, path: e.target.value })}
            helperText="Ruta relativa (ej: /vacunas, /vacunas/{id})"
          />
        </Box>

        <TextField
          fullWidth
          margin="normal"
          label="Descripción"
          placeholder="Descripción del endpoint"
          multiline
          rows={2}
          value={endpoint.description}
          onChange={(e) => setEndpoint({ ...endpoint, description: e.target.value })}
        />

        <FormControl fullWidth margin="normal">
          <InputLabel>Tipo de Handler</InputLabel>
          <Select
            value={endpoint.handler_type}
            onChange={(e) => setEndpoint({ ...endpoint, handler_type: e.target.value })}
            label="Tipo de Handler"
          >
            {HANDLER_TYPES.map(type => (
              <MenuItem key={type.id} value={type.id}>
                <Box>
                  <Typography variant="body2">{type.name}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {type.description}
                  </Typography>
                </Box>
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {modelName && (
          <TextField
            fullWidth
            margin="normal"
            label="Modelo Asociado"
            value={endpoint.model_name}
            disabled
            helperText="Modelo de datos que usará este endpoint"
          />
        )}

        <FormControlLabel
          control={
            <Checkbox
              checked={endpoint.auth_required}
              onChange={(e) => setEndpoint({ ...endpoint, auth_required: e.target.checked })}
            />
          }
          label="Requiere autenticación"
        />

        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            size="large"
            onClick={() => onSave(endpoint)}
            disabled={!endpoint.name || !endpoint.path}
          >
            Guardar Endpoint
          </Button>
        </Box>
      </Paper>
    </Box>
  );
}
