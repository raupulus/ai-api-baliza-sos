# Ficha de planificación: legislación y derechos

[← Volver al índice](README.md)

> **Estado:** `propuesta` — sin corpus ni conector.
> **Prioridad:** P2. **Destino:** híbrido: artículos estructurados + fragmentos RAG.
> **Origen en `valorar.md`:** líneas 33 y 67-69.

## 1. Objetivo y límites

Facilitar consulta offline de un corpus legal pequeño y trazable: Constitución Española, Carta de los Derechos Fundamentales de la UE, Código Civil y normas esenciales relacionadas con protección civil y emergencias. La respuesta debe citar norma, artículo, versión y fecha de vigencia, y advertir que no constituye asesoramiento jurídico.

“Leyes españolas” no se interpreta como descargar todo el ordenamiento. Se excluyen jurisprudencia masiva, normativa derogada, comentarios privados y respuestas jurídicas inferidas sin artículo recuperado. La selección futura necesitará una lista cerrada y justificada.

## 2. Registro de fuentes

### `BOE-LEG-CONSOLIDADA` — Legislación consolidada del BOE

- **Organismo:** Agencia Estatal Boletín Oficial del Estado.
- **API:** https://www.boe.es/datosabiertos/api/api.php
- **Documentación:** https://boe.es/datosabiertos/documentos/APIconsolidada.pdf
- **Aviso legal:** https://boe.es/informacion/aviso_legal/
- **Qué obtener:** metadatos de norma, texto consolidado por bloques/artículos, análisis, identificador ELI/BOE, fecha de actualización y versiones.
- **Formato:** XML mediante API; PDF/HTML como evidencia auxiliar.
- **Fiabilidad:** alta; publicación oficial. El texto consolidado es informativo y debe conservarse el enlace a la publicación oficial.
- **Licencia:** aplicar exactamente el aviso legal del BOE y atribución; confirmar compatibilidad antes de redistribuir instantáneas.
- **Cadencia:** mensual para corpus estable y extraordinaria cuando cambie una norma incluida.

### `BOE-CONSTITUCION` — Constitución Española

- **Organismo:** BOE; el Congreso se usa como punto de contraste institucional.
- **BOE/ELI consolidado verificado:** https://www.boe.es/eli/es/c/1978/12/27/(1)/con
- **Congreso:** https://constitucion.congreso.es/constitucion-1978/descarga-constitucion
- **Qué obtener:** preámbulo, títulos, capítulos, secciones, artículos y reformas.
- **Formato:** XML/API preferente; PDF de contraste.
- **Fiabilidad:** alta.
- **Licencia:** aviso legal del BOE; condiciones del Congreso pendientes de verificar.
- **Cadencia:** comprobar mensualmente, aunque cambie raramente.

### `BOE-CODIGO-CIVIL` — Código Civil y legislación complementaria

- **Organismo:** BOE.
- **URL de código electrónico:** https://www.boe.es/biblioteca_juridica/codigos/codigo.php?id=034_Codigo_Civil_y_legislacion_complementaria&modo=2
- **Qué obtener:** no el PDF monolítico como unidad RAG; descubrir desde el índice las normas e identificadores oficiales aprobados para el corpus.
- **Formato:** índice HTML/PDF y normas XML vía API.
- **Fiabilidad:** alta.
- **Licencia:** aviso legal del BOE.
- **Cadencia:** mensual.

### `EURLEX-CARTA` — Carta de Derechos Fundamentales de la UE

- **Organismo:** Oficina de Publicaciones de la Unión Europea, EUR-Lex.
- **URL:** https://eur-lex.europa.eu/legal-content/ES/TXT/HTML/?uri=CELEX:12012P/TXT&from=ES
- **Qué obtener:** capítulos, artículos, título oficial, CELEX, lengua y fecha de versión.
- **Formato:** HTML/XML disponibles desde EUR-Lex.
- **Fiabilidad:** alta; portal jurídico oficial de la UE.
- **Licencia:** verificar el aviso de reutilización de EUR-Lex y las excepciones aplicables.
- **Cadencia:** anual o por nueva versión.

### `BOP-CADIZ` — Normativa provincial/local seleccionada

- **Organismo:** Diputación Provincial de Cádiz.
- **Portal:** https://www.bopcadiz.es/
- **Qué obtener:** solo disposiciones concretas previamente incluidas en la lista cerrada; no descargar el boletín completo.
- **Formato:** HTML/PDF.
- **Fiabilidad:** alta para publicación oficial local.
- **Licencia:** pendiente de verificar.
- **Cadencia:** según cada disposición seleccionada.

## 3. Corpus inicial y mapeo

| Bloque | Fuente | Clave estable | Salida | Consulta |
|---|---|---|---|---|
| Constitución | BOE | `eli + articulo + version` | texto literal y metadatos | Exacta + semántica |
| Derechos UE | EUR-Lex | `CELEX + articulo + idioma` | texto literal y metadatos | Exacta + semántica |
| Código Civil | BOE | `id_norma + articulo + version` | selección aprobada | Exacta + semántica |
| Protección civil | BOE | ELI/artículo | obligaciones y competencias | Exacta + semántica |
| Normativa local | BOP | anuncio/disposición + fecha | selección explícita | Exacta |

Los resúmenes generados nunca sustituyen el texto literal. La respuesta debe recuperar al menos un artículo vigente; si no existe coincidencia suficiente, debe indicar que no puede resolverlo offline.

## 4. Instantáneas y transformación

```text
data/raw/downloads/legislacion-derechos/<AAAA-MM-DD>/
├── boe/<id_norma>/metadatos.xml
├── boe/<id_norma>/texto_consolidado.xml
├── eurlex/12012P_TXT_es.html
├── corpus-seleccionado.json
└── MANIFEST.json
```

Parsear la jerarquía normativa sin cortar apartados ni mezclar versiones. Guardar `vigente_desde`, `vigente_hasta`, `fecha_actualizacion`, `derogada`, `idioma`, URL oficial y hash. La selección del corpus será configuración/datos, nunca una lista hardcodeada a Cádiz en el conector.

## 5. Calidad, presupuesto y actualización

- Validación por profesional jurídico antes de aprobar la selección y después de cambios sustantivos.
- Rechazar normas sin identificador oficial, textos de terceros y versiones cuya vigencia no pueda determinarse.
- Comparar por artículo y generar altas, bajas y modificaciones. Mantener la última instantánea aprobada para rollback.
- Objetivo inicial: 3-10 normas y algunos cientos de artículos; almacenar texto y metadatos compactos, no colecciones PDF completas en la Pi.
- Casos de prueba: artículo concreto, derecho fundamental, norma derogada, conflicto temporal, consulta no cubierta y petición de asesoramiento personalizado.

## 6. Pendientes para aprobar

- [ ] Definir la lista cerrada de normas además de Constitución, Carta y Código Civil.
- [ ] Verificar condiciones de reutilización de BOE, EUR-Lex, Congreso y BOP.
- [ ] Diseñar modelo de vigencia y citas antes de implementar.
- [ ] Asignar revisor jurídico.
- [ ] Estimar tamaño con una muestra XML real de la API.
