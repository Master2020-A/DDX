/**
 * Preview de Código Generado
 * Muestra el código que se generará para el módulo
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  Button,
  CircularProgress
} from '@mui/material';
import { Code, Download, Copy } from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8612';

interface CodePreviewProps {
  moduleId: string;
}

interface CodeData {
  model_code?: string;
  endpoint_code?: string;
  component_code?: string;
  migration_sql?: string;
}

export default function CodePreview({ moduleId }: CodePreviewProps) {
  const [loading, setLoading] = useState(false);
  const [codeData, setCodeData] = useState<CodeData>({});
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    loadCodePreview();
  }, [moduleId]);

  const loadCodePreview = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/api/studio/modules/${moduleId}/preview`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setCodeData(response.data);
    } catch (error) {
      console.error('Error cargando preview:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (code: string) => {
    navigator.clipboard.writeText(code);
    alert('Código copiado al portapapeles');
  };

  const tabs = [
    { label: 'Modelo (Python)', code: codeData.model_code, language: 'python' },
    { label: 'Endpoint (Python)', code: codeData.endpoint_code, language: 'python' },
    { label: 'Componente (React)', code: codeData.component_code, language: 'typescript' },
    { label: 'Migración (SQL)', code: codeData.migration_sql, language: 'sql' }
  ];

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Code size={24} style={{ marginRight: 8 }} />
          <Typography variant="h6">Preview de Código Generado</Typography>
        </Box>

        <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)} sx={{ mb: 2 }}>
          {tabs.map((tab, index) => (
            <Tab key={index} label={tab.label} />
          ))}
        </Tabs>

        {tabs[activeTab].code ? (
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
              <Button
                size="small"
                startIcon={<Copy size={16} />}
                onClick={() => handleCopy(tabs[activeTab].code!)}
              >
                Copiar
              </Button>
            </Box>
            <Paper
              sx={{
                p: 2,
                bgcolor: '#1E1E1E',
                color: '#D4D4D4',
                fontFamily: 'monospace',
                fontSize: '0.875rem',
                overflow: 'auto',
                maxHeight: '500px',
                '& pre': {
                  margin: 0
                }
              }}
            >
              <pre>
                <code>{tabs[activeTab].code}</code>
              </pre>
            </Paper>
          </Box>
        ) : (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography color="text.secondary">
              No hay código generado para esta sección
            </Typography>
          </Box>
        )}
      </Paper>
    </Box>
  );
}
