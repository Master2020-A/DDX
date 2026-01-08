// frontend/src/pages/Workflows.tsx
import React, { useCallback, useEffect, useMemo, useState } from "react";

/**
 * Workflows y Agentes IA
 * Página de diagnóstico / exploración de endpoints.
 *
 * Nota: tu backend monta workflows bajo /api (según main.py).
 * Si tu router define prefix="/workflows", el endpoint típico sería:
 *   GET /api/workflows
 */

type Json = Record<string, unknown> | unknown[] | string | number | boolean | null;

type FetchState<T> = {
  loading: boolean;
  error: string | null;
  status: number | null;
  data: T | null;
};

function safeJsonParse(text: string): Json | null {
  try {
    return JSON.parse(text) as Json;
  } catch {
    return null;
  }
}

function getTokenFromStorage(): string | null {
  // Ajusta estas keys si tu app usa otras
  const candidates = ["access_token", "token"];

  for (const key of candidates) {
    const raw = localStorage.getItem(key);
    if (!raw) continue;

    // A veces guardan el token como JSON: { access_token: "..." }
    const parsed = safeJsonParse(raw);
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      const obj = parsed as Record<string, unknown>;
      const maybe = obj.access_token ?? obj.token;
      if (typeof maybe === "string" && maybe.trim()) return maybe.trim();
    }

    // O directo como string
    if (typeof raw === "string" && raw.trim()) return raw.trim();
  }

  return null;
}

function buildAuthHeader(): Record<string, string> {
  const token = getTokenFromStorage();
  if (!token) return {};

  // Soporta si ya viene con "Bearer "
  const value = token.startsWith("Bearer ") ? token : `Bearer ${token}`;
  return { Authorization: value };
}

async function fetchAny(url: string, init?: RequestInit) {
  const res = await fetch(url, init);
  const text = await res.text();

  // Intentar JSON; si no, devolver texto
  const asJson = safeJsonParse(text);
  return {
    ok: res.ok,
    status: res.status,
    statusText: res.statusText,
    contentType: res.headers.get("content-type") ?? "",
    rawText: text,
    json: asJson,
  };
}

export default function Workflows(): React.JSX.Element {
  const apiBase = useMemo(() => {
    // Puedes definir cualquiera de estas en .env del frontend:
    // VITE_API_BASE_URL=http://localhost:8612
    // VITE_API_URL=http://localhost:8612
    const envBase =
      (import.meta as any).env?.VITE_API_BASE_URL ||
      (import.meta as any).env?.VITE_API_URL ||
      "";
    return String(envBase || "").trim().replace(/\/+$/, "");
  }, []);

  const [baseUrl, setBaseUrl] = useState<string>(apiBase); // vacío => mismo origen
  const [endpoint, setEndpoint] = useState<string>("/api/workflows");
  const [method, setMethod] = useState<"GET" | "POST">("GET");
  const [body, setBody] = useState<string>(
    JSON.stringify(
      {
        // Si tu backend requiere un payload para crear workflows, ajústalo aquí
        name: "Workflow demo",
        description: "Creado desde Workflows.tsx",
      },
      null,
      2
    )
  );

  const [state, setState] = useState<FetchState<Json>>({
    loading: false,
    error: null,
    status: null,
    data: null,
  });

  const fullUrl = useMemo(() => {
    const path = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
    return `${baseUrl}${path}`;
  }, [baseUrl, endpoint]);

  const runRequest = useCallback(async () => {
    setState({ loading: true, error: null, status: null, data: null });

    try {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
        ...buildAuthHeader(),
      };

      const init: RequestInit = {
        method,
        headers,
      };

      if (method !== "GET") {
        // Validar JSON antes de enviar
        const parsed = safeJsonParse(body);
        if (parsed === null) {
          throw new Error("El body no es JSON válido. Corrígelo antes de enviar.");
        }
        init.body = JSON.stringify(parsed);
      }

      const result = await fetchAny(fullUrl, init);

      const data: Json =
        result.json !== null
          ? result.json
          : {
              contentType: result.contentType,
              text: result.rawText,
            };

      setState({
        loading: false,
        error: result.ok ? null : `${result.status} ${result.statusText}`,
        status: result.status,
        data,
      });
    } catch (e: any) {
      setState({
        loading: false,
        error: e?.message ? String(e.message) : "Error desconocido",
        status: null,
        data: null,
      });
    }
  }, [body, fullUrl, method]);

  // Autocarga una vez (puedes quitar esto si no quieres llamadas automáticas)
  useEffect(() => {
    runRequest();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div style={{ padding: 16, maxWidth: 1100, margin: "0 auto" }}>
      <h1 style={{ marginBottom: 8 }}>Workflows</h1>
      <p style={{ marginTop: 0, color: "#666" }}>
        Página para probar endpoints de Workflows (GET/POST). Si tu API usa JWT,
        asegúrate de tener <code>access_token</code> en <code>localStorage</code>.
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 12,
          marginTop: 12,
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <label style={{ fontWeight: 600 }}>Base URL (opcional)</label>
          <input
            value={baseUrl}
            onChange={(e) => setBaseUrl(e.target.value)}
            placeholder="Ej: http://localhost:8612 (vacío = mismo origen)"
            style={{ padding: 10, borderRadius: 8, border: "1px solid #ddd" }}
          />

          <label style={{ fontWeight: 600, marginTop: 6 }}>Endpoint</label>
          <input
            value={endpoint}
            onChange={(e) => setEndpoint(e.target.value)}
            placeholder="/api/workflows"
            style={{ padding: 10, borderRadius: 8, border: "1px solid #ddd" }}
          />

          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <label style={{ fontWeight: 600 }}>Método</label>
            <select
              value={method}
              onChange={(e) => setMethod(e.target.value as "GET" | "POST")}
              style={{ padding: 10, borderRadius: 8, border: "1px solid #ddd" }}
            >
              <option value="GET">GET</option>
              <option value="POST">POST</option>
            </select>

            <button
              onClick={runRequest}
              disabled={state.loading}
              style={{
                marginLeft: "auto",
                padding: "10px 14px",
                borderRadius: 8,
                border: "1px solid #ddd",
                background: state.loading ? "#f5f5f5" : "#fff",
                cursor: state.loading ? "not-allowed" : "pointer",
                fontWeight: 600,
              }}
            >
              {state.loading ? "Cargando..." : "Ejecutar"}
            </button>
          </div>

          <div style={{ marginTop: 6, color: "#444" }}>
            <div style={{ fontSize: 13 }}>
              URL final: <code>{fullUrl}</code>
            </div>
            <div style={{ fontSize: 13 }}>
              Token detectado:{" "}
              <code>{getTokenFromStorage() ? "sí" : "no"}</code>
            </div>
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <label style={{ fontWeight: 600 }}>
            Body (solo para POST/PUT/PATCH)
          </label>
          <textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            rows={14}
            spellCheck={false}
            style={{
              padding: 10,
              borderRadius: 8,
              border: "1px solid #ddd",
              fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
              fontSize: 12,
              resize: "vertical",
            }}
          />
        </div>
      </div>

      <div style={{ marginTop: 16 }}>
        <h2 style={{ marginBottom: 8 }}>Respuesta</h2>

        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <div>
            Status:{" "}
            <strong>
              {state.status !== null ? state.status : "—"}
            </strong>
          </div>
          {state.error && (
            <div style={{ color: "#b00020" }}>
              Error: <strong>{state.error}</strong>
            </div>
          )}
        </div>

        <pre
          style={{
            marginTop: 10,
            padding: 12,
            borderRadius: 8,
            background: "#0b1020",
            color: "#e6e6e6",
            overflow: "auto",
            fontSize: 12,
          }}
        >
          {state.data !== null ? JSON.stringify(state.data, null, 2) : "Sin datos"}
        </pre>

        <div style={{ marginTop: 10, color: "#666", fontSize: 13 }}>
          Si te da 404 en <code>/api/workflows</code>, prueba con{" "}
          <code>/api/workflows/</code> o revisa el prefix real de tu router en backend.
        </div>
      </div>
    </div>
  );
}