/**
 * Componente de notificaciones para valores críticos de laboratorio
 */
import React, { useState, useEffect } from 'react';
import {
  Badge,
  IconButton,
  Menu,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Typography,
  Box,
  Chip,
  Button
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import laboratorioService from '@/services/laboratorioService';
import { PruebaLaboratorioResumen } from '@/types/laboratorio';

interface NotificacionesLaboratorioProps {
  pacienteId?: string;
}

const NotificacionesLaboratorio: React.FC<NotificacionesLaboratorioProps> = ({ pacienteId }) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notificaciones, setNotificaciones] = useState<PruebaLaboratorioResumen[]>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (pacienteId) {
      cargarNotificaciones();
    }
  }, [pacienteId]);

  const cargarNotificaciones = async () => {
    if (!pacienteId) return;
    
    setLoading(true);
    try {
      // Obtener todas las pruebas del paciente
      const pruebas = await laboratorioService.listarPruebasPaciente(pacienteId);
      
      // Filtrar solo las que tienen valores críticos o requieren atención
      const pruebasConAlertas = pruebas.filter(
        p => p.tiene_valores_criticos || p.requiere_atencion
      );
      
      // Ordenar por fecha más reciente
      pruebasConAlertas.sort((a, b) => 
        new Date(b.fecha).getTime() - new Date(a.fecha).getTime()
      );
      
      setNotificaciones(pruebasConAlertas);
    } catch (error) {
      console.error('Error cargando notificaciones:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleVerPrueba = (pruebaId: string) => {
    handleClose();
    // Navegar al detalle de la prueba
    if (pacienteId) {
      navigate(`/laboratorios/${pacienteId}?prueba=${pruebaId}`);
    }
  };

  const handleMarcarVistas = () => {
    // Aquí podrías implementar lógica para marcar como vistas
    setNotificaciones([]);
    handleClose();
  };

  const formatearFecha = (fecha: string) => {
    const date = new Date(fecha);
    const ahora = new Date();
    const diffMs = ahora.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) {
      return `Hace ${diffMins} min`;
    } else if (diffHours < 24) {
      return `Hace ${diffHours} h`;
    } else if (diffDays < 7) {
      return `Hace ${diffDays} días`;
    } else {
      return date.toLocaleDateString('es-MX', { 
        day: '2-digit', 
        month: 'short' 
      });
    }
  };

  const obtenerIconoEstado = (prueba: PruebaLaboratorioResumen) => {
    if (prueba.tiene_valores_criticos) {
      return <ErrorIcon color="error" />;
    } else if (prueba.requiere_atencion) {
      return <WarningIcon color="warning" />;
    }
    return <CheckCircleIcon color="success" />;
  };

  const open = Boolean(anchorEl);
  const cantidadNotificaciones = notificaciones.length;

  return (
    <>
      <IconButton
        color="inherit"
        onClick={handleClick}
        aria-label="notificaciones"
      >
        <Badge badgeContent={cantidadNotificaciones} color="error">
          <NotificationsIcon />
        </Badge>
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        PaperProps={{
          sx: {
            width: 400,
            maxHeight: 500,
            overflow: 'auto'
          }
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">
            Alertas de Laboratorio
          </Typography>
          {cantidadNotificaciones > 0 && (
            <Chip 
              label={cantidadNotificaciones} 
              color="error" 
              size="small" 
            />
          )}
        </Box>
        <Divider />

        {loading ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography color="text.secondary">Cargando...</Typography>
          </Box>
        ) : cantidadNotificaciones === 0 ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <CheckCircleIcon sx={{ fontSize: 48, color: 'success.main', mb: 1 }} />
            <Typography color="text.secondary">
              No hay alertas pendientes
            </Typography>
          </Box>
        ) : (
          <>
            <List sx={{ p: 0 }}>
              {notificaciones.map((notif, index) => (
                <React.Fragment key={notif.id}>
                  {index > 0 && <Divider />}
                  <ListItem
                    button
                    onClick={() => handleVerPrueba(notif.id)}
                    sx={{
                      '&:hover': {
                        backgroundColor: 'action.hover'
                      }
                    }}
                  >
                    <ListItemIcon>
                      {obtenerIconoEstado(notif)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box>
                          <Typography variant="body2" fontWeight="bold">
                            {notif.area.replace('_', ' ').toUpperCase()} - {notif.tipo_prueba.replace('_', ' ')}
                          </Typography>
                          {notif.tiene_valores_criticos && (
                            <Chip 
                              label="VALORES CRÍTICOS" 
                              color="error" 
                              size="small" 
                              sx={{ mt: 0.5 }}
                            />
                          )}
                          {notif.requiere_atencion && !notif.tiene_valores_criticos && (
                            <Chip 
                              label="Requiere Atención" 
                              color="warning" 
                              size="small" 
                              sx={{ mt: 0.5 }}
                            />
                          )}
                        </Box>
                      }
                      secondary={
                        <Typography variant="caption" color="text.secondary">
                          {formatearFecha(notif.fecha)}
                        </Typography>
                      }
                    />
                  </ListItem>
                </React.Fragment>
              ))}
            </List>
            <Divider />
            <Box sx={{ p: 1, textAlign: 'center' }}>
              <Button 
                size="small" 
                onClick={handleMarcarVistas}
                startIcon={<CloseIcon />}
              >
                Marcar todas como vistas
              </Button>
            </Box>
          </>
        )}
      </Menu>
    </>
  );
};

export default NotificacionesLaboratorio;
