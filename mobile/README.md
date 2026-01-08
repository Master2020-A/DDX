# 📱 DDX Portal Paciente - Aplicación Móvil

Aplicación móvil multiplataforma (Android/iOS) del Portal del Paciente para el sistema DDX.

## 🚀 Características

- ✅ **Autenticación segura** con almacenamiento encriptado
- 📅 **Gestión de citas** médicas
- 🔬 **Solicitud de estudios** clínicos
- 💬 **Mensajería** con médicos
- 💊 **Recordatorios** de medicamentos con notificaciones push
- ⚙️ **Configuración** personalizada
- 📊 **Dashboard** con métricas en tiempo real
- 🔐 **Soporte para biometría** (huella/Face ID)

## 📋 Requisitos Previos

### Para Desarrollo

- **Node.js** 18+ y npm
- **Expo CLI**: `npm install -g expo-cli`
- **Expo Go** app en tu dispositivo móvil (para pruebas rápidas)

### Para Compilación Android

- **Android Studio** con SDK Platform 33+
- **Java JDK** 11+
- Variables de entorno configuradas:
  - `ANDROID_HOME`
  - `JAVA_HOME`

### Para Compilación iOS (solo macOS)

- **Xcode** 14+
- **CocoaPods**: `sudo gem install cocoapods`
- **Cuenta de Apple Developer** (para distribución)

## 🛠️ Instalación

### 1. Instalar Dependencias

```bash
cd mobile
npm install
```

### 2. Configurar Backend

Edita `src/services/api.ts` y cambia la URL del backend:

```typescript
const API_BASE_URL = 'http://TU_IP_LOCAL:8612/api';
```

**Importante**: 
- Para Android: Usa la IP de tu computadora (ej: `192.168.1.100`)
- Para iOS: Usa la IP de tu computadora
- NO uses `localhost` o `127.0.0.1` (no funcionará en dispositivos físicos)

### 3. Iniciar el Servidor de Desarrollo

```bash
npm start
```

Esto abrirá Expo Dev Tools en tu navegador.

## 📱 Ejecutar en Dispositivo

### Opción 1: Expo Go (Más Rápido)

1. Instala **Expo Go** desde:
   - [Google Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent) (Android)
   - [App Store](https://apps.apple.com/app/expo-go/id982107779) (iOS)

2. Escanea el código QR que aparece en la terminal o en Expo Dev Tools

3. La app se cargará automáticamente en tu dispositivo

### Opción 2: Emulador Android

```bash
npm run android
```

### Opción 3: Simulador iOS (solo macOS)

```bash
npm run ios
```

## 📦 Compilar para Producción

### Android APK (Debug)

```bash
# Instalar EAS CLI
npm install -g eas-cli

# Login en Expo
eas login

# Configurar proyecto
eas build:configure

# Compilar APK
eas build --platform android --profile preview
```

El APK se descargará automáticamente cuando termine.

### Android AAB (Para Google Play Store)

```bash
eas build --platform android --profile production
```

### iOS (Para App Store)

```bash
eas build --platform ios --profile production
```

## 🔧 Configuración Avanzada

### Cambiar Nombre de la App

Edita `app.json`:

```json
{
  "expo": {
    "name": "Tu Nombre de App",
    "slug": "tu-slug"
  }
}
```

### Cambiar Icono y Splash Screen

Reemplaza los archivos en `assets/`:
- `icon.png` (1024x1024)
- `splash.png` (1284x2778)
- `adaptive-icon.png` (1024x1024, solo Android)

### Configurar Notificaciones Push

1. Crea un proyecto en [Firebase Console](https://console.firebase.google.com/)
2. Descarga `google-services.json` (Android) y `GoogleService-Info.plist` (iOS)
3. Colócalos en la raíz del proyecto
4. Actualiza `app.json` con las credenciales

## 🗂️ Estructura del Proyecto

```
mobile/
├── App.tsx                      # Punto de entrada
├── app.json                     # Configuración de Expo
├── package.json                 # Dependencias
├── src/
│   ├── screens/                 # Pantallas de la app
│   │   ├── LoginScreen.tsx
│   │   ├── DashboardScreen.tsx
│   │   ├── CitasScreen.tsx
│   │   ├── EstudiosScreen.tsx
│   │   ├── MensajesScreen.tsx
│   │   └── ConfiguracionScreen.tsx
│   ├── navigation/              # Navegación
│   │   └── MainTabs.tsx
│   └── services/                # Servicios API
│       ├── api.ts
│       ├── authService.ts
│       └── portalPacienteService.ts
└── assets/                      # Recursos (iconos, imágenes)
```

## 🔐 Seguridad

- **Tokens** almacenados en `SecureStore` (encriptado)
- **Comunicación HTTPS** recomendada en producción
- **Autenticación biométrica** disponible
- **Sesiones** con expiración automática

## 🐛 Solución de Problemas

### Error: "Network Error"

- Verifica que el backend esté corriendo
- Confirma que la IP en `api.ts` sea correcta
- Asegúrate de estar en la misma red WiFi

### Error: "Unable to resolve module"

```bash
npm install
expo start --clear
```

### App no se actualiza

```bash
expo start --clear
# O presiona 'r' en la terminal para recargar
```

### Problemas con Android Build

```bash
cd android
./gradlew clean
cd ..
npm run android
```

## 📚 Recursos

- [Documentación de Expo](https://docs.expo.dev/)
- [React Native Docs](https://reactnative.dev/docs/getting-started)
- [React Navigation](https://reactnavigation.org/docs/getting-started)
- [EAS Build](https://docs.expo.dev/build/introduction/)

## 🤝 Contribuir

1. Crea una rama para tu feature
2. Realiza tus cambios
3. Prueba en Android e iOS
4. Crea un Pull Request

## 📄 Licencia

Propiedad de DDX Medical Systems

---

## 🚀 Quick Start

```bash
# 1. Instalar dependencias
cd mobile && npm install

# 2. Configurar IP del backend en src/services/api.ts

# 3. Iniciar desarrollo
npm start

# 4. Escanear QR con Expo Go
```

¡Listo! Tu app móvil del Portal del Paciente está funcionando 🎉
