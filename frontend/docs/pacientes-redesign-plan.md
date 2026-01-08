# Plan de Rediseño Ejecutivo para Secciones de Pacientes

Este plan describe los pasos para modernizar, unificar y profesionalizar las pantallas clave del módulo de pacientes (Expediente Clínico, Historia Clínica, Galería de Imágenes, Laboratorio Clínico, Estudios Especiales, Diagnóstico Sugerido, Cumplimiento Normativo y Nueva Consulta). El objetivo es lograr una experiencia consistente con el nuevo panel de detalle, con énfasis en claridad, jerarquía visual y soporte para flujos complejos.

---

## 1. Base Visual Compartida

1. **Crear layout maestro** (`PatientWorkspaceLayout`)
   - Hero superior reutilizable con breadcrumbs, avatar/foto, acciones rápidas y badges de estado.
   - Contenedor de contenido con `max-w-7xl`, márgenes y padding uniformes.
   - Barra lateral opcional (cards de contacto/alertas) y lienzo principal.

2. **Sistema de componentes**
   - `DataBadge`, `MetricCard`, `GradientTile`, `TimelineCard`, `SectionHeader`.
   - Paleta degradada (indigo → violet) para héroes, tonos pastel para cards informativas.

3. **Tipografía y espaciado**
   - Inter/Outfit 500–700 para títulos.
   - Grid de 8 px, radios `rounded-3xl` para contenedores principales.

---

## 2. Expediente Clínico

1. **Hero**: Mostrar expediente, tipo de sangre, última actualización, CTA “Guardar cambios”.
2. **Tabs elevados**: Convertir tabs actuales a `SegmentedControl` con iconos, indicador de progreso.
3. **Contenido modular**:
   - Secciones con cards de color neutro + icono lineal.
   - Formularios largos divididos en `Grid` 2 columnas.
   - Chips editables para listas (padecimientos/medicamentos) con modales tipo `Sheet`.
4. **Resumen lateral**: mostrar firmas, médicos tratantes, alergias críticas.

---

## 3. Historia Clínica / Historia Pediátrica

1. **Wizard visual** para etapas (Motivo, Exploración, Diagnóstico, Plan).
2. **Linea temporal** de consultas previas a la izquierda, formulario activo a la derecha.
3. **Componente de IA** con tarjetas sugeridas (diferenciar por color y estado de confianza).
4. **Acciones persistentes** (Guardar, Generar PDF, Compartir FHIR) flotando en barra inferior sticky.

---

## 4. Galería de Imágenes

1. **Mosaico neumórfico** con filtros por fecha, tipo de estudio, etiquetas.
2. **Visor modal** con carrusel, zoom, anotaciones y comparación lado a lado.
3. **Integración IA** para resaltar hallazgos (overlay heatmap + checklist exportable).

---

## 5. Laboratorio Clínico

1. **Dashboard tipo tarjetas** (Hemograma, Perfil Lipídico, etc.) con estado (normal/alto/bajo).
2. **Tablas densas** con zebra striping, badges de referencia y chips de tendencia.
3. **CTA “Ordenar nueva prueba”** abre wizard con plantillas predefinidas.
4. **Insight IA**: sugerencias basadas en anomalías (component `InsightCard`).

---

## 6. Estudios Especiales

1. **Cards grandes** por tipo de estudio (Imagen, Funcional, Neuro, etc.).
2. **Timeline con hitos** (solicitud → programación → resultado) usando `Stepper`.
3. **Modal de resultado enriquecido** (PDF embed, métricas clave, comparación histórica).

---

## 7. Diagnóstico Sugerido

1. **Panel IA** de doble columna: árbol de hipótesis y evidencia.
2. **Widgets** de confianza, impacto y recomendaciones terapéuticas.
3. **Botones CTA** para aceptar/descartar y convertir en diagnóstico oficial.

---

## 8. Cumplimiento Normativo

1. **Panel KPI** con semáforos (verde/amarillo/rojo) para cada norma.
2. **Checklist interactivo** con estados (Pendiente, En proceso, Validado).
3. **Generador de reportes** con timeline de auditorías.

---

## 9. Nueva Consulta

1. **Wizard de 4 pasos** (Datos iniciales → Exploración → Diagnóstico → Plan).
2. **Resumen lateral** constantemente actualizado con datos clave del paciente.
3. **IA Copilot** integrado para sugerir preguntas, diagnósticos diferenciales y recetas.

---

## 10. Roadmap de Implementación

| Sprint | Entregables clave |
|--------|--------------------|
| **S1** | Layout maestro, componentes compartidos, Expediente Clínico rediseñado |
| **S2** | Historia Clínica + Nueva Consulta con wizard y AI hints |
| **S3** | Galería de Imágenes + Laboratorio (dashboards y visores) |
| **S4** | Estudios Especiales + Diagnóstico Sugerido + Cumplimiento Normativo |
| **S5** | Refinamiento multi-idioma, accesibilidad, documentación Storybook |

---

## 11. Consideraciones Técnicas

- **Internacionalización**: usar `react-i18next`, diccionarios por módulo.
- **Estado**: centralizar datos del paciente en Zustand/React Query para reutilización.
- **Tematización**: crear archivo `designTokens.ts` con colores, sombras, radios, tipografías.
- **Pruebas**: snapshots de componentes clave + e2e para principales flujos.

---

## 12. Entregables Finales

1. UI Kit en Figma/Storybook.
2. Componentes React implementados con Tailwind/clsx.
3. Documentación de uso (MDX) y ejemplos de código.
4. Scripts para migración visual (actualización de rutas y navegación).
