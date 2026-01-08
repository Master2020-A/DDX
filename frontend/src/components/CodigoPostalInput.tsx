import React, { useEffect, useMemo, useRef, useState } from "react";
import api from "@/lib/api";

interface CodigoPostalData {
  codigo_postal: string;
  pais: string;
  estado: string;
  municipio: string;
  ciudad?: string;
  colonia?: string;
  colonias?: string[];
  fuente?: string;
}

interface CodigoPostalInputProps {
  value: string; // <- IMPORTANTE: este value existe y se usa
  onChange: (value: string) => void;
  onDataLoaded?: (data: CodigoPostalData) => void;
  className?: string;
  disabled?: boolean;
}

const onlyDigits = (s: string) => (s ?? "").replace(/\D/g, "");

const CodigoPostalInput: React.FC<CodigoPostalInputProps> = ({
  value,          // <- AQUÍ estaba el problema típico: faltaba este value
  onChange,
  onDataLoaded,
  className = "",
  disabled = false,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const lastCpRef = useRef<string | null>(null);
  const debounceRef = useRef<number | null>(null);

  const cp = useMemo(() => onlyDigits(value).slice(0, 5), [value]);

  useEffect(() => {
    // limpiar debounce anterior
    if (debounceRef.current) {
      window.clearTimeout(debounceRef.current);
      debounceRef.current = null;
    }

    // si no hay 5 dígitos, no consultamos
    if (cp.length !== 5) {
      setError(null);
      setLoading(false);
      lastCpRef.current = null;
      return;
    }

    // evita consultar repetido el mismo CP
    if (lastCpRef.current === cp) return;

    debounceRef.current = window.setTimeout(async () => {
      try {
        setLoading(true);
        setError(null);

        // ✅ Backend consulta catálogo/SEPOMEX con fallback automático
        const res = await api.get(`/catalogos/codigo-postal/${cp}`);
        const data = res.data as CodigoPostalData;

        lastCpRef.current = cp;

        onDataLoaded?.(data);
      } catch (err: any) {
        // si tu backend regresa {detail:"..."} (FastAPI), lo mostramos
        const rawMessage =
          err?.response?.data?.detail ||
          err?.message ||
          "No pudimos obtener el código postal";

        const normalized = String(rawMessage).toLowerCase();
        const friendlyMessage = normalized.includes("apikey")
          ? "No pudimos conectar con el catálogo externo. Completa los campos manualmente."
          : rawMessage;

        setError(friendlyMessage);
        lastCpRef.current = null;
      } finally {
        setLoading(false);
      }
    }, 400);

    return () => {
      if (debounceRef.current) {
        window.clearTimeout(debounceRef.current);
        debounceRef.current = null;
      }
    };
  }, [cp, onDataLoaded]);

  return (
    <div>
      <div className="relative">
        <input
          type="text"
          value={cp}
          onChange={(e) => {
            const next = onlyDigits(e.target.value).slice(0, 5);
            // permitir nueva consulta
            lastCpRef.current = null;
            onChange(next);
          }}
          placeholder="Código postal (5 dígitos)"
          maxLength={5}
          disabled={disabled}
          className={`input ${error ? "border-red-500" : ""} ${className}`}
        />

        {loading && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <div className="animate-spin h-4 w-4 border-2 border-primary-500 border-t-transparent rounded-full" />
          </div>
        )}
      </div>

      {error && <p className="text-sm text-red-600 mt-1">{error}</p>}
    </div>
  );
};

export default CodigoPostalInput;