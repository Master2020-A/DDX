/**
 * Componente de autocompletado para códigos CIE-10
 */
import { useState, useEffect } from 'react';
import { Autocomplete, TextField, CircularProgress, Box, Typography } from '@mui/material';
import { prediagnosticoService, type CIE10SearchResult } from '@/services/prediagnosticoService';

interface Props {
  value: string;
  onChange: (codigo: string, descripcion: string) => void;
  label?: string;
  placeholder?: string;
  error?: boolean;
  helperText?: string;
  required?: boolean;
}

export default function CIE10Autocomplete({
  value,
  onChange,
  label = 'Código CIE-10',
  placeholder = 'Buscar diagnóstico o código...',
  error,
  helperText,
  required,
}: Props) {
  const [inputValue, setInputValue] = useState('');
  const [options, setOptions] = useState<CIE10SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedOption, setSelectedOption] = useState<CIE10SearchResult | null>(null);

  useEffect(() => {
    if (inputValue.length < 2) {
      setOptions([]);
      return;
    }

    const buscarCodigos = async () => {
      setLoading(true);
      try {
        const resultados = await prediagnosticoService.buscarCIE10(inputValue, 15);
        setOptions(resultados);
      } catch (err) {
        console.error('Error buscando CIE-10:', err);
        setOptions([]);
      } finally {
        setLoading(false);
      }
    };

    const timeoutId = setTimeout(buscarCodigos, 300);
    return () => clearTimeout(timeoutId);
  }, [inputValue]);

  return (
    <Autocomplete
      value={selectedOption}
      onChange={(_, newValue) => {
        setSelectedOption(newValue);
        if (newValue) {
          onChange(newValue.codigo, newValue.descripcion);
        } else {
          onChange('', '');
        }
      }}
      inputValue={inputValue}
      onInputChange={(_, newInputValue) => {
        setInputValue(newInputValue);
      }}
      options={options}
      loading={loading}
      getOptionLabel={(option) => `${option.codigo} - ${option.descripcion}`}
      isOptionEqualToValue={(option, value) => option.codigo === value.codigo}
      renderOption={(props, option) => (
        <Box component="li" {...props}>
          <Box>
            <Typography variant="body2" fontWeight="bold">
              {option.codigo}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {option.descripcion}
            </Typography>
            {option.categoria && (
              <Typography variant="caption" color="text.secondary">
                {option.categoria}
              </Typography>
            )}
          </Box>
        </Box>
      )}
      renderInput={(params) => (
        <TextField
          {...params}
          label={label}
          placeholder={placeholder}
          error={error}
          helperText={helperText}
          required={required}
          InputProps={{
            ...params.InputProps,
            endAdornment: (
              <>
                {loading ? <CircularProgress color="inherit" size={20} /> : null}
                {params.InputProps.endAdornment}
              </>
            ),
          }}
        />
      )}
      noOptionsText={
        inputValue.length < 2
          ? 'Ingrese al menos 2 caracteres para buscar'
          : 'No se encontraron resultados'
      }
    />
  );
}
