# Ficha de planificación: historia y patrimonio

[← Volver al índice](README.md)

> **Estado:** `en_validacion` — existe un conector narrativo heredado; ampliar y trazar desde fuentes oficiales.
> **Prioridad:** P3. **Destino:** híbrido: inventario estructurado + RAG narrativo.
> **Origen en `valorar.md`:** línea 44.

## 1. Objetivo y límites

Documentar historia municipal y lugares patrimoniales relevantes de toda la provincia configurada, con ubicación, cronología, protección, descripción y procedencia. La prioridad operativa es identificar correctamente un lugar y aportar contexto breve; no construir una enciclopedia general.

Se distinguirán hechos documentados, dataciones aproximadas y tradiciones. No se inventarán horarios, acceso, estado de conservación ni coordenadas a partir de texto narrativo; esos datos requieren fuente y vigencia propias.

## 2. Registro de fuentes

### `IAPH-OPEN-DATA`

- **Organismo:** Instituto Andaluz del Patrimonio Histórico, Junta de Andalucía.
- **Guía Digital:** https://www.juntadeandalucia.es/organismos/iaph/areas/documentacion-patrimonio/guia-digital.html
- **API:** https://guiadigital.iaph.es/store/apis/info?name=open-data-iaph&provider=guiadigital&version=1.0
- **Qué obtener:** entidades patrimoniales, denominación, tipología, localización, municipio, descripción, cronología, protección, identificadores y enlaces disponibles.
- **Formato:** API Open Data; documentar autenticación, límites y esquema antes de implementar.
- **Fiabilidad:** alta para inventario patrimonial andaluz.
- **Licencia:** verificar condiciones de la API y de imágenes/textos por separado; no asumir que fotografías heredan la licencia de los metadatos.
- **Cadencia:** trimestral.

### `JUNTA-PATRIMONIO`

- **Organismo:** Consejería competente en cultura/patrimonio.
- **Punto de descubrimiento:** Guía Digital IAPH y Catálogo General del Patrimonio Histórico Andaluz enlazado desde portales oficiales.
- **Qué obtener:** declaraciones, categorías de protección y disposiciones oficiales cuando no estén completas en la API.
- **Formato:** HTML/PDF/BOJA.
- **Fiabilidad:** alta.
- **Licencia:** pendiente de verificar por recurso.
- **Cadencia:** trimestral.

### `ARCHIVO-MUSEOS-OFICIALES`

- **Organismos:** Archivo Histórico Provincial, Museo de Cádiz y conjuntos arqueológicos de la Junta.
- **Descubrimiento:** portales institucionales de la Junta; cada publicación seleccionada tendrá URL y ficha propias.
- **Qué obtener:** contexto histórico de hitos priorizados, colecciones y cronologías, no todo el portal.
- **Formato:** HTML/PDF.
- **Fiabilidad:** alta dentro de su ámbito curatorial.
- **Licencia:** pendiente de verificar por texto/imagen.
- **Cadencia:** anual.

### `AYUNTAMIENTOS-DIPUTACION`

- **Organismos:** ayuntamientos y Diputación de Cádiz.
- **Catálogo de datos:** https://datosabiertos.dipucadiz.es/ (portal de datos abiertos; endpoint CKAN en revisión)
- **Qué obtener:** inventarios locales y metadatos de lugares no cubiertos por IAPH, solo si identifica publicador, fecha y licencia.
- **Formato:** JSON/CSV/HTML.
- **Fiabilidad:** alta para inventario municipal; el contenido turístico se considera complementario.
- **Licencia:** por dataset/publicación.
- **Cadencia:** semestral.

### `MCU-BIC` — Registros de protección estatal

- **Organismo:** Ministerio de Cultura (registro de Bienes de Interés Cultural) y Consejería de Cultura de la Junta.
- **Portal:** https://www.cultura.gob.es/
- **Qué obtener:** declaraciones BIC, categoría de protección y disposiciones oficiales (BOE/BOJA) para contrastar la protección jurídica de los bienes.
- **Formato:** HTML/PDF/BOE-BOJA.
- **Fiabilidad:** alta para régimen de protección.
- **Licencia:** pendiente de verificar por recurso.
- **Cadencia:** trimestral y tras nuevas declaraciones.

## 3. Mapeo

| Bloque | Fuente | Campos/salida | Destino | Validación |
|---|---|---|---|---|
| Lugar patrimonial | IAPH | id, nombre, tipos, municipio, geometría, protección | Tabla | Esquema y coordenadas |
| Cronología | IAPH/archivo | periodo, fecha desde/hasta, precisión, evidencia | Tabla + RAG | Historiador/documentalista |
| Descripción | IAPH/museo | resumen fiel, elementos destacados, fuente | RAG | Cita por afirmación |
| Hito histórico | archivo/museo | evento, fecha, lugares, protagonistas, incertidumbre | RAG | Contraste institucional |
| Acceso práctico | gestor del lugar | dirección, acceso, horario, vigencia | Tabla separada | Caducidad corta |

Imágenes no son necesarias para el RAG textual inicial y no se descargarán salvo licencia y caso de uso aprobados.

## 4. Auditoría del conector existente

`src/updater/sources/historia_cadiz.py` contiene seis resúmenes manuales sin URL por afirmación. Declara una licencia genérica, confianza alta y un equipo revisor no identificado, y fecha la supuesta validación en cada ejecución.

Los textos pueden usarse como lista de temas a contrastar —Gadir, Gades/Baelo Claudia, frontera medieval, Carrera de Indias, Trafalgar y 1812—, no como fuente. Deben reemplazarse por fragmentos trazables y ampliarse a los municipios y lugares seleccionados.

## 5. Instantáneas

```text
data/raw/downloads/historia-patrimonio/<AAAA-MM-DD>/
├── iaph/records.<json|xml>
├── junta/<disposicion>.pdf
├── archivos-museos/<publicacion>.html
├── diputacion/<dataset>.<json|csv>
└── MANIFEST.json
```

Filtrar por provincia/códigos/geometría configurados. Mantener HTML/API original y salida normalizada separadas, con identificadores IAPH para actualizaciones.

## 6. Calidad, presupuesto y actualización

- Validar IDs, municipio, coordenadas, duplicados, cronología y categoría de protección.
- Marcar fechas aproximadas y versiones historiográficas; no convertir una tradición en hecho demostrado.
- Revisión por historiador, arqueólogo o documentalista para el corpus narrativo.
- Pruebas: lugar con varios nombres, yacimiento en dos municipios, fecha aproximada, ubicación no visitable y hecho controvertido.
- Priorizar inicialmente lugares relevantes por municipio; pocos cientos de registros y fragmentos, sin imágenes ni PDF en la Pi.
- Actualización trimestral de API y anual de narrativas, con diff y rollback.

## 7. Pendientes para aprobar

- [ ] Probar esquema, límites y licencia de la API IAPH.
- [ ] Definir criterios de relevancia y cobertura mínima por municipio.
- [ ] Seleccionar publicaciones institucionales para los seis hitos heredados.
- [ ] Asignar revisor histórico/documental.
- [ ] Diseñar migración del conector sin mantener afirmaciones sin cita.
