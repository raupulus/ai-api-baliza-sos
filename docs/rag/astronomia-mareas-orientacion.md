# Ficha de planificación: astronomía, mareas y orientación

[← Volver al índice](README.md)

> **Estado:** `propuesta` — sin cálculos, descargas ni tablas publicadas.
> **Prioridad:** P1. **Destino:** tablas precalculadas + RAG explicativo.
> **Origen en `valorar.md`:** líneas 72-77.

## 1. Objetivo y decisión de agrupación

Agrupar calendario astronómico, almanaque, Luna, Sol y orientación por estrellas porque comparten coordenadas, fecha/hora y fuentes astronómicas. Las mareas permanecen como bloque separado dentro de la ficha: dependen de estaciones costeras y de otra autoridad.

Se pretende responder offline sobre orto/ocaso, fases lunares, fenómenos seleccionados, referencias celestes simples y predicción de marea publicada. No se usará la astronomía como sustituto de GPS/cartografía en una emergencia ni se inventará precisión cuando no se conozca posición, zona horaria, horizonte o estación mareográfica.

## 2. Registro de fuentes

### `ROA-EFEMERIDES`

- **Organismo:** Real Observatorio de la Armada, Ministerio de Defensa.
- **Portal:** https://armada.defensa.gob.es/ArmadaPortal/page/Portal/ArmadaEspannola/cienciaobservatorio/prefLang-es/03Efemerides
- **Sol:** https://armada.defensa.gob.es/ArmadaPortal/page/Portal/ArmadaEspannola/cienciaobservatorio/prefLang-es/03Efemerides--01Sol
- **Luna:** https://armada.defensa.gob.es/ArmadaPortal/page/Portal/ArmadaEspannola/cienciaobservatorio/prefLang-es/03Efemerides--02Luna
- **Qué obtener:** resultados de Sol/Luna disponibles para fecha y lugar, definiciones y metadatos; el Almanaque Náutico se considera publicación separada anual.
- **Formato:** formulario/HTML y publicaciones.
- **Fiabilidad:** alta; organismo oficial especializado.
- **Licencia:** pendiente de verificar. Acceso público o compra de una publicación no autorizan redistribución.
- **Cadencia:** anual para almanaque/calendario y por cambios del servicio.
- **Estabilidad:** primero documentar parámetros y condiciones del formulario; no automatizar hasta confirmar permiso.

### `IGN-ASTRONOMIA`

- **Organismo:** Observatorio Astronómico Nacional / Instituto Geográfico Nacional.
- **Anuario:** https://astronomia.ign.es/anuario-astronomico
- **Atlas celeste:** https://astronomia.ign.es/oan/atlas-celeste
- **Qué obtener:** calendario anual de eventos, atlas del cielo para Península y material explicativo de orientación/observación.
- **Formato:** HTML/PDF/publicación.
- **Fiabilidad:** alta.
- **Licencia:** verificar política del IGN/CNIG y licencia de cada descarga.
- **Cadencia:** anual.

### `ROA-ALMANAQUE` — Almanaque Náutico

- **Organismo:** Real Observatorio de la Armada.
- **Descubrimiento:** sección de publicaciones del portal ROA anterior.
- **Qué obtener:** solo metadatos, edición, erratas y campos necesarios si existe permiso y formato reutilizable. Se descartan como autoridad primaria las copias de `nauticalalmanac.it` propuestas en `valorar.md` mientras no se demuestre origen y licencia.
- **Formato:** publicación anual/aplicación ANdi según oferta oficial.
- **Fiabilidad:** alta para la edición oficial.
- **Licencia:** pendiente de verificar; posible publicación comercial.
- **Cadencia:** anual y tras erratas.

### `PDE-MAREAS` — Puertos del Estado

- **Organismo:** Puertos del Estado.
- **Portal:** https://portuscopia.puertos.es/
- **Servicio relacionado:** https://portus.puertos.es/
- **Manual de descarga:** https://bancodatos.puertos.es/BD/peticiones/Manual_Usuario_Descargaportus.pdf
- **Qué obtener:** estaciones relevantes y series/predicciones de nivel del mar o mareas con fecha, zona horaria y calidad.
- **Formato:** descargas océano-meteorológicas y metadatos.
- **Fiabilidad:** alta, con cautelas de calidad indicadas por el organismo.
- **Condiciones:** el manual de 2021 prohíbe transferir los datos descargados a terceros y exige atribución. **Bloqueado para redistribución/indexación** hasta confirmar por escrito que el uso offline del proyecto es compatible.
- **Cadencia:** anual para calendarios precalculados o según horizonte permitido; los datos se revisan permanentemente.

### `IHM` — Instituto Hidrográfico de la Marina (contraste náutico)

- **Organismo:** Instituto Hidrográfico de la Marina, Armada Española.
- **Portal:** https://armada.defensa.gob.es/ArmadaPortal/page/Portal/ArmadaEspannola/cienciaihm1/prefLang-es/
- **Qué obtener:** cartas náuticas oficiales, derroteros y publicaciones de mareas/corrientes como contraste náutico de faros, mareas y señalización marítima.
- **Formato:** publicaciones/cartas; verificar recurso reutilizable.
- **Fiabilidad:** alta para náutica oficial; parte de la cartografía es comercial.
- **Licencia:** pendiente de verificar; no asumir reutilización.
- **Cadencia:** anual y por edición.

## 3. Mapeo

| Bloque | Fuente | Clave/campos | Destino | Validación |
|---|---|---|---|---|
| Sol | ROA o cálculo contrastado | fecha, lat, lon, zona, orto, ocaso, crepúsculos | Tabla anual | Muestra contra ROA |
| Luna | ROA o cálculo contrastado | fecha/hora, fase, iluminación, orto/ocaso | Tabla anual | Muestra contra ROA |
| Eventos | IGN/ROA | tipo, inicio/máximo/fin, visibilidad, edición | Tabla + RAG | Edición anual |
| Orientación | IGN/ROA | hemisferio, época, referencia, limitaciones | RAG | Experto/guía oficial |
| Almanaque | ROA | edición, campo astronómico autorizado | Tabla/documento | Licencia previa |
| Mareas | Puertos del Estado u origen autorizado | estación, instante, altura, tipo, zona, revisión | Tabla | Condiciones + estación |

Las tablas se generan por año y por una malla mínima de ubicaciones/estaciones, no por cada municipio si el cálculo acepta coordenadas. Todos los instantes se guardan en UTC y se presentan con zona horaria explícita, incluyendo cambios de horario.

## 4. Instantáneas y transformación

```text
data/raw/downloads/astronomia-mareas-orientacion/<AAAA-MM-DD>/
├── roa/efemerides_<periodo>.<html|json>
├── ign/atlas_calendario_<AAAA>.pdf
├── almanac/metadatos_<AAAA>.json
├── mareas/<estacion>_<periodo>.<formato>  # solo si se autoriza
├── LICENSE.txt
└── MANIFEST.json
```

Antes de adquirir en masa, guardar condiciones, parámetros, zona horaria y versión del algoritmo/publicación. Si se opta por cálculo local futuro, deberá documentarse biblioteca, versión, datos astronómicos y error máximo; no se añade dependencia en esta fase.

## 5. Calidad, presupuesto y actualización

- Validar rango de latitud/longitud, año, UTC, horario de verano, eventos inexistentes y estación mareográfica.
- Contrastar muestras de Sol/Luna con ROA y no mezclar fase global con horarios dependientes de ubicación.
- Rechazar páginas de terceros sin procedencia, calendarios sin zona horaria y mareas sin estación/fecha de revisión.
- Revisión náutica para cualquier uso de mareas; el resultado no se presenta como garantía de navegación segura.
- Presupuesto: tablas anuales compactas de pocos MiB; atlas y publicaciones quedan en el actualizador. No cargar años ilimitados ni PDFs en la Pi.
- Actualización anual con solape entre años; erratas y revisiones generan nueva instantánea, diff y aprobación.

## 6. Pendientes para aprobar

- [ ] Verificar condiciones de reutilización de ROA e IGN.
- [ ] Resolver por escrito la incompatibilidad aparente de transferencia de datos de Puertos del Estado.
- [ ] Elegir entre datos oficiales descargados y cálculo reproducible para Sol/Luna.
- [ ] Definir estaciones mareográficas y horizonte temporal permitido.
- [ ] Asignar revisión astronómica/náutica y tolerancias de error.
