# Ficha de planificación: radio y comunicaciones de emergencia

[← Volver al índice](README.md)

> **Estado:** `propuesta` — sin corpus ni tablas aprobadas.
> **Prioridad:** P1. **Destino:** RAG para manuales + tablas exactas para bandas/frecuencias.
> **Origen en `valorar.md`:** líneas 49-50 y 64-66, además de la línea 70.

## 1. Objetivo y límites

Preparar ayuda offline para configurar y operar Meshtastic, Winlink, VARA HF, VarAC y PinPoint APRS, junto con un resumen legal español de bandas y comunicaciones de emergencia. Las instrucciones deben identificar producto, versión, sistema y requisitos de licencia.

No se publicarán frecuencias como “libres” sin servicio, país, modo, licencia y vigencia; no se autoriza interferir, suplantar indicativos, transmitir en bandas restringidas ni saltarse límites técnicos. En peligro se describirá el marco legal vigente con cita, sin prometer cobertura.

## 2. Registro de fuentes

### `MESHTASTIC-OFFICIAL`

- **Organismo/proyecto:** Meshtastic, documentación y repositorios oficiales.
- **Portal:** https://meshtastic.org/docs/
- **Repositorio de referencia:** https://github.com/meshtastic/meshtastic
- **Qué obtener:** configuración regional UE, canales, roles, consumo, seguridad, límites de paquetes, clientes y resolución de problemas; fijar versión/tag.
- **Formato:** Markdown versionado y documentación web.
- **Fiabilidad:** alta para el producto; normativa RF debe contrastarse con BOE/CNAF.
- **Licencia:** el repositorio indicado declara GPL-3.0; verificar licencia del repositorio exacto que contiene cada página y cumplir atribución.
- **Cadencia:** por release, con revisión mensual.

### `WINLINK`

- **Organismo:** Amateur Radio Safety Foundation / Winlink Global Radio Email.
- **Portal:** https://winlink.org/
- **Qué obtener:** arquitectura, cuentas/indicativos, modos de conexión, flujo de mensajes y procedimientos oficiales de cliente.
- **Formato:** HTML y manuales enlazados.
- **Fiabilidad:** alta para Winlink.
- **Licencia:** pendiente de verificar por manual; no redistribuir ejecutables.
- **Cadencia:** trimestral y por versión.

### `VARAC-VARA`

- **Organismo:** proyectos VarAC y VARA de sus respectivos autores.
- **Manuales VarAC:** https://www.varac-hamradio.com/post/varac-user-manuals
- **Qué obtener:** instalación/configuración, interoperabilidad, mensajería y diferencias entre VARA HF y VarAC.
- **Formato:** HTML/PDF/manual.
- **Fiabilidad:** alta para uso del producto, no para regulación.
- **Licencia:** pendiente de verificar; VARA/VarAC pueden tener condiciones comerciales o de redistribución.
- **Cadencia:** por versión.

### `PINPOINT-APRS`

- **Organismo:** PinPoint APRS.
- **Descargas/documentación:** https://pinpointaprs.com/download.html
- **Qué obtener:** configuración del cliente, mapas offline, indicativo, TNC/modem y limitaciones.
- **Formato:** HTML/PDF/ayuda de software.
- **Fiabilidad:** alta para el producto; auxiliar para APRS en general.
- **Licencia:** pendiente de verificar; no almacenar instaladores salvo permiso.
- **Cadencia:** por versión.

### `BOE-RADIO`

- **Organismo:** BOE y Secretaría de Estado de Telecomunicaciones.
- **CNAF vigente evaluado:** https://www.boe.es/eli/es/o/2026/07/10/tdf732/con
- **Reglamento de radioaficionados:** https://www.boe.es/eli/es/o/2013/07/09/iet1311/con
- **Qué obtener:** atribución de bandas, notas UN, límites y régimen de radioaficionados, siempre desde textos consolidados/vigentes.
- **Formato:** HTML/XML vía BOE.
- **Fiabilidad:** alta y normativa.
- **Licencia:** aviso legal BOE: https://boe.es/informacion/aviso_legal/
- **Cadencia:** mensual y tras nueva orden.

### `REMER-VADEMECUM-2017`

- **Organismo:** Dirección General de Protección Civil y Emergencias.
- **REMER:** https://www.proteccioncivil.es/coordinacion/redes/remer
- **Publicación:** https://cpage.mpr.gob.es/publicacion/vademecum-remer-2017-126170195-0000/
- **Copia local existente:** `data/raw/Vademecum_Remer_2017.rar` y `data/raw/Vademecum_Remer_2017/`.
- **Qué obtener:** terminología, procedimientos REMER y referencias históricas útiles; inventariar capítulos antes de asignarlos a fichas.
- **Formato:** archivo/PDF/HTML, 2017, NIPO 126-17-018-X/019-5.
- **Fiabilidad:** alta como publicación oficial histórica, pero no como autoridad única vigente.
- **Licencia:** pendiente de verificar; no asumir reutilización por estar descargado.
- **Cadencia:** por nueva edición o cambios REMER.

### `UIT-HET` — Manual de telecomunicaciones de emergencia

- **Organismo:** Unión Internacional de Telecomunicaciones.
- **URL:** https://www.itu.int/pub/D-HDB-HET/es
- **Qué obtener:** usar como referencia de revisión sobre planificación y redes, no como contenido copiado automáticamente.
- **Formato:** publicación/manual.
- **Fiabilidad:** alta, pero edición antigua y contexto profesional.
- **Licencia:** derechos reservados; reutilización pendiente. Bloqueado para indexación hasta autorización compatible.

## 3. Mapeo

| Bloque | Fuente | Salida | Destino | Validación |
|---|---|---|---|---|
| Meshtastic | oficial + BOE | tarea, versión, región, pasos, advertencia | RAG | Prueba con versión fijada |
| Winlink | oficial + BOE | modo, requisitos, flujo, error común | RAG | Radioaficionado |
| VARA/VarAC/PinPoint | manual propio | producto/versión, pasos, límites | RAG | Prueba de software |
| Bandas | CNAF | rango, servicio, nota, límites, vigencia | Tabla | Revisión normativa |
| Frecuencias/canales | autoridad competente | frecuencia, modo, ámbito, licencia, fuente, vigencia | Tabla | Doble comprobación |
| REMER | DGPCE | procedimiento histórico/vigente, edición | RAG | Contraste actual |

No mezclar una frecuencia de escucha, llamada, repetidor local o servicio profesional. La tabla exigirá `country=ES`, zona si aplica y estado `vigente/pendiente/historico`.

## 4. Instantáneas

```text
data/raw/downloads/radio-comunicaciones/<AAAA-MM-DD>/
├── meshtastic/<tag>/
├── winlink/<version>/
├── varac-vara/<version>/
├── pinpoint/<version>/
├── boe/<eli>/
├── remer/manifest-local.json
└── MANIFEST.json
```

El Vademécum existente tendrá inventario y hash sin duplicar sus 633 MiB. Extraer solo capítulos autorizados y relevantes; los binarios y originales pesados no llegan a la Pi.

## 5. Calidad, presupuesto y actualización

- Toda instrucción de software debe llevar versión; detectar enlaces rotos y opciones renombradas.
- Toda frecuencia debe tener fuente normativa/operativa, fecha, servicio, modo y requisitos. Rechazar listas de foros.
- Revisión por radioaficionado con licencia y conocimiento normativo.
- Pruebas: región LoRa incorrecta, transmisión sin indicativo, banda fuera de autorización, manual antiguo y consulta de emergencia ambigua.
- Objetivo: menos de 200 fragmentos y unos cientos de registros; seleccionar páginas, no espejar repositorios completos.
- Comparar tags y textos legales; un cambio de banda o potencia bloquea la tabla hasta revisión y permite rollback.

## 6. Pendientes para aprobar

- [ ] Identificar repositorio/licencia exactos de las páginas Meshtastic seleccionadas.
- [ ] Verificar permisos de Winlink, VarAC, VARA y PinPoint.
- [ ] Inventariar capítulos y condiciones del Vademécum 2017.
- [ ] Definir la lista mínima de frecuencias con autoridad verificable.
- [ ] Asignar revisor radioaficionado y jurídico.
