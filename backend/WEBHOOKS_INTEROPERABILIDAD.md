# Sistema de Webhooks para Interoperabilidad HL7 FHIR

Sistema completo de suscripciones a eventos y notificaciones automáticas mediante webhooks para el módulo de Interoperabilidad.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Eventos Disponibles](#eventos-disponibles)
- [API Endpoints](#api-endpoints)
- [Seguridad](#seguridad)
- [Ejemplos de Uso](#ejemplos-de-uso)
- [Formato de Payload](#formato-de-payload)
- [Verificación de Firma](#verificación-de-firma)
- [Reintentos y Manejo de Errores](#reintentos-y-manejo-de-errores)

## 🎯 Características

- ✅ Suscripción a eventos específicos del sistema
- ✅ Envío automático de notificaciones HTTP POST
- ✅ Firma HMAC-SHA256 para verificar autenticidad
- ✅ Sistema de reintentos con backoff exponencial
- ✅ Filtros personalizados por evento
- ✅ Historial completo de entregas
- ✅ Estadísticas de éxito/fallo
- ✅ Headers HTTP personalizados
- ✅ Timeout configurable
- ✅ Prueba de webhooks

## 📡 Eventos Disponibles

### Solicitudes de Intercambio
- `solicitud.creada` - Se crea una nueva solicitud
- `solicitud.aprobada` - Una solicitud es aprobada
- `solicitud.rechazada` - Una solicitud es rechazada
- `solicitud.completada` - Una solicitud se completa exitosamente
- `solicitud.error` - Ocurre un error en una solicitud

### Instituciones
- `institucion.creada` - Se registra una nueva institución
- `institucion.actualizada` - Se actualiza una institución
- `institucion.desactivada` - Una institución es desactivada

### Consentimientos
- `consentimiento.creado` - Se crea un nuevo consentimiento
- `consentimiento.revocado` - Un consentimiento es revocado
- `consentimiento.expirando` - Un consentimiento está próximo a expirar

### Otros
- `bundle.generado` - Se genera un bundle FHIR
- `historia.creada` - Se crea una historia clínica unificada

## 🔌 API Endpoints

### Crear Suscripción
```http
POST /api/interoperabilidad/webhooks/
Authorization: Bearer {token}
Content-Type: application/json

{
  "nombre": "Webhook Producción",
  "descripcion": "Webhook para notificaciones de solicitudes",
  "url": "https://mi-sistema.com/webhooks/interoperabilidad",
  "eventos": [
    "solicitud.creada",
    "solicitud.aprobada",
    "solicitud.completada"
  ],
  "timeout_segundos": 30,
  "reintentos_max": 3,
  "headers_adicionales": {
    "X-Custom-Header": "valor"
  },
  "filtros": {
    "prioridad": ["alta", "urgente"]
  }
}
```

### Listar Suscripciones
```http
GET /api/interoperabilidad/webhooks/
Authorization: Bearer {token}
```

### Obtener Suscripción
```http
GET /api/interoperabilidad/webhooks/{webhook_id}
Authorization: Bearer {token}
```

### Actualizar Suscripción
```http
PUT /api/interoperabilidad/webhooks/{webhook_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "activo": true,
  "eventos": ["solicitud.creada", "solicitud.aprobada"]
}
```

### Eliminar Suscripción
```http
DELETE /api/interoperabilidad/webhooks/{webhook_id}
Authorization: Bearer {token}
```

### Probar Webhook
```http
POST /api/interoperabilidad/webhooks/{webhook_id}/probar
Authorization: Bearer {token}
```

### Listar Entregas
```http
GET /api/interoperabilidad/webhooks/{webhook_id}/entregas
Authorization: Bearer {token}
```

### Listar Eventos Disponibles
```http
GET /api/interoperabilidad/webhooks/eventos/disponibles
Authorization: Bearer {token}
```

## 🔒 Seguridad

### Firma HMAC-SHA256

Cada payload enviado incluye una firma en el header `X-Webhook-Signature` para verificar su autenticidad.

**Generación de la firma:**
```python
import hmac
import hashlib
import json

def verificar_firma(payload_json: str, firma_recibida: str, secret_key: str) -> bool:
    firma_calculada = hmac.new(
        secret_key.encode('utf-8'),
        payload_json.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(firma_calculada, firma_recibida)
```

**Ejemplo en Node.js:**
```javascript
const crypto = require('crypto');

function verificarFirma(payloadJson, firmaRecibida, secretKey) {
    const firmaCalculada = crypto
        .createHmac('sha256', secretKey)
        .update(payloadJson)
        .digest('hex');
    
    return crypto.timingSafeEqual(
        Buffer.from(firmaCalculada),
        Buffer.from(firmaRecibida)
    );
}
```

## 📦 Formato de Payload

Todos los webhooks envían un payload JSON con la siguiente estructura:

```json
{
  "evento": "solicitud.creada",
  "timestamp": "2024-12-19T20:00:00.000Z",
  "suscripcion_id": "uuid-de-la-suscripcion",
  "data": {
    "id": "uuid-de-la-solicitud",
    "tipo_intercambio": "expediente_completo",
    "protocolo": "fhir_r4",
    "estado": "pendiente",
    "prioridad": "alta",
    "paciente_id": "uuid-del-paciente",
    "institucion_destino_id": "uuid-de-la-institucion",
    "created_at": "2024-12-19T20:00:00.000Z"
  }
}
```

### Headers Enviados

```
Content-Type: application/json
X-Webhook-Signature: {firma-hmac-sha256}
X-Webhook-Event: {tipo-de-evento}
User-Agent: DDX-Interoperabilidad-Webhook/1.0
{headers-adicionales-configurados}
```

## 🔄 Reintentos y Manejo de Errores

### Política de Reintentos

- **Número de reintentos:** Configurable (por defecto 3)
- **Backoff exponencial:** 2^intento segundos (2s, 4s, 8s)
- **Códigos de éxito:** 200-299
- **Timeout:** Configurable (por defecto 30 segundos)

### Estados de Webhook

- **activo:** Funcionando correctamente
- **pausado:** Temporalmente desactivado por el usuario
- **desactivado:** Permanentemente desactivado
- **error:** Múltiples fallos consecutivos

### Ejemplo de Respuesta Esperada

Su endpoint debe responder con código HTTP 200-299:

```json
{
  "recibido": true,
  "mensaje": "Evento procesado correctamente"
}
```

## 💡 Ejemplos de Uso

### Ejemplo 1: Servidor Express (Node.js)

```javascript
const express = require('express');
const crypto = require('crypto');

const app = express();
app.use(express.json());

const SECRET_KEY = 'tu-secret-key-aqui';

app.post('/webhooks/interoperabilidad', (req, res) => {
    const firma = req.headers['x-webhook-signature'];
    const evento = req.headers['x-webhook-event'];
    const payload = JSON.stringify(req.body);
    
    // Verificar firma
    const firmaCalculada = crypto
        .createHmac('sha256', SECRET_KEY)
        .update(payload)
        .digest('hex');
    
    if (!crypto.timingSafeEqual(Buffer.from(firma), Buffer.from(firmaCalculada))) {
        return res.status(401).json({ error: 'Firma inválida' });
    }
    
    // Procesar evento
    console.log(`Evento recibido: ${evento}`);
    console.log('Datos:', req.body.data);
    
    // Responder rápidamente
    res.status(200).json({ recibido: true });
    
    // Procesar de forma asíncrona
    procesarEvento(req.body).catch(console.error);
});

async function procesarEvento(payload) {
    switch (payload.evento) {
        case 'solicitud.creada':
            // Lógica para nueva solicitud
            break;
        case 'solicitud.aprobada':
            // Lógica para solicitud aprobada
            break;
        // ... otros eventos
    }
}

app.listen(3000, () => {
    console.log('Servidor webhook escuchando en puerto 3000');
});
```

### Ejemplo 2: FastAPI (Python)

```python
from fastapi import FastAPI, Request, HTTPException, Header
import hmac
import hashlib
import json

app = FastAPI()

SECRET_KEY = "tu-secret-key-aqui"

def verificar_firma(payload: str, firma: str) -> bool:
    firma_calculada = hmac.new(
        SECRET_KEY.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(firma_calculada, firma)

@app.post("/webhooks/interoperabilidad")
async def webhook_interoperabilidad(
    request: Request,
    x_webhook_signature: str = Header(...),
    x_webhook_event: str = Header(...)
):
    # Obtener payload
    body = await request.body()
    payload_str = body.decode('utf-8')
    
    # Verificar firma
    if not verificar_firma(payload_str, x_webhook_signature):
        raise HTTPException(status_code=401, detail="Firma inválida")
    
    # Parsear JSON
    payload = json.loads(payload_str)
    
    # Procesar evento
    print(f"Evento recibido: {x_webhook_event}")
    print(f"Datos: {payload['data']}")
    
    # Responder rápidamente
    return {"recibido": True}
```

### Ejemplo 3: Filtros Personalizados

Crear webhook que solo reciba solicitudes de alta prioridad:

```json
{
  "nombre": "Webhook Urgencias",
  "url": "https://mi-sistema.com/webhooks/urgencias",
  "eventos": ["solicitud.creada"],
  "filtros": {
    "prioridad": ["alta", "urgente"]
  }
}
```

## 📊 Monitoreo y Estadísticas

Cada suscripción mantiene estadísticas automáticas:

- `total_envios`: Total de eventos enviados
- `total_exitosos`: Entregas exitosas
- `total_fallidos`: Entregas fallidas
- `ultimo_envio`: Timestamp del último envío
- `ultimo_exito`: Timestamp del último éxito
- `ultimo_error`: Mensaje del último error
- `ultimo_error_fecha`: Timestamp del último error

## 🧪 Pruebas

### Probar Webhook con curl

```bash
# Crear suscripción
curl -X POST http://localhost:8612/api/interoperabilidad/webhooks/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test Webhook",
    "url": "https://webhook.site/unique-id",
    "eventos": ["solicitud.creada"]
  }'

# Probar webhook
curl -X POST http://localhost:8612/api/interoperabilidad/webhooks/{webhook_id}/probar \
  -H "Authorization: Bearer {token}"
```

### Usar webhook.site para Pruebas

1. Ir a https://webhook.site
2. Copiar la URL única generada
3. Crear suscripción con esa URL
4. Probar el webhook
5. Ver los payloads recibidos en webhook.site

## 🔧 Troubleshooting

### Webhook no recibe eventos

1. Verificar que el webhook esté activo
2. Verificar que los eventos estén correctamente suscritos
3. Revisar los filtros configurados
4. Verificar que la URL sea accesible públicamente

### Errores de firma

1. Verificar que el `secret_key` sea correcto
2. Asegurarse de usar el payload JSON exacto (sin modificar)
3. Usar `hmac.compare_digest()` para comparación segura

### Timeouts

1. Aumentar `timeout_segundos` en la configuración
2. Optimizar el endpoint receptor para responder rápidamente
3. Procesar eventos de forma asíncrona

## 📝 Mejores Prácticas

1. **Responder rápido:** Responde con 200 OK inmediatamente y procesa de forma asíncrona
2. **Verificar firma:** Siempre verifica la firma HMAC antes de procesar
3. **Idempotencia:** Diseña tu endpoint para manejar eventos duplicados
4. **Logging:** Registra todos los eventos recibidos para auditoría
5. **Monitoreo:** Revisa regularmente las estadísticas de entregas
6. **HTTPS:** Usa siempre HTTPS en producción
7. **Rotación de claves:** Rota el `secret_key` periódicamente

## 🚀 Integración con Sistemas Externos

### Ejemplo: Integración con Slack

```python
import requests

def enviar_a_slack(payload):
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    
    mensaje = {
        "text": f"Nueva solicitud de intercambio",
        "attachments": [{
            "color": "good",
            "fields": [
                {"title": "Tipo", "value": payload['data']['tipo_intercambio'], "short": True},
                {"title": "Prioridad", "value": payload['data']['prioridad'], "short": True},
                {"title": "Estado", "value": payload['data']['estado'], "short": True}
            ]
        }]
    }
    
    requests.post(webhook_url, json=mensaje)
```

### Ejemplo: Integración con Microsoft Teams

```python
import requests

def enviar_a_teams(payload):
    webhook_url = "https://outlook.office.com/webhook/YOUR/WEBHOOK/URL"
    
    mensaje = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": "Nueva solicitud de intercambio",
        "themeColor": "0078D7",
        "title": "Interoperabilidad HL7 FHIR",
        "sections": [{
            "activityTitle": f"Evento: {payload['evento']}",
            "facts": [
                {"name": "Tipo", "value": payload['data']['tipo_intercambio']},
                {"name": "Prioridad", "value": payload['data']['prioridad']},
                {"name": "Estado", "value": payload['data']['estado']}
            ]
        }]
    }
    
    requests.post(webhook_url, json=mensaje)
```

## 📚 Recursos Adicionales

- [Documentación de FHIR R4](https://www.hl7.org/fhir/R4/)
- [Especificación HMAC](https://tools.ietf.org/html/rfc2104)
- [Webhook Best Practices](https://webhooks.fyi/)

## 🆘 Soporte

Para reportar problemas o solicitar ayuda:
1. Revisar el historial de entregas en `/webhooks/{id}/entregas`
2. Verificar los logs del sistema
3. Contactar al equipo de desarrollo

---

**Versión:** 1.0  
**Última actualización:** Diciembre 2024
