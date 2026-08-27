# 05 · Contratos de datos (API y RAG)

> **Última actualización:** 2026-08-27  
> **Ámbito:** Contrato HTTP de API, modelo interno de fragmentos y persistencia relacional.

[← Volver al Índice de Documentación Técnica](README.md)

---

Define los formatos estables que comparten el backend y los clientes externos,
y el formato interno de los fragmentos del RAG. Cualquier cambio aquí es un
cambio de contrato y debe versionarse.

## 1. API del bot — petición

`POST /v1/consulta`

Cabecera: `Authorization: Bearer <API_AUTH_TOKEN>`

```json
{
  "consulta": "Me ha picado una medusa en Zahara, duele mucho",
  "idioma": "es",
  "categoria_sugerida": null,
  "ubicacion": { "lat": 36.13, "lon": -5.85 },
  "cliente": "meshtastic-node-!2a4b6c8d",
  "id_conversacion": "meshtastic-node-!2a4b6c8d",
  "reset_conversacion": false
}
```

- `consulta` (str, obligatorio): texto en lenguaje natural (mín. 1, máx. 2000).
- `idioma` (str, opcional, def. `es`).
- `categoria_sugerida` (str|null, opcional): pista del cliente
  (`primeros_auxilios`, `fauna`, `flora`, `geografia`, `supervivencia`, `orientacion`, `cultura_historia`).
- `ubicacion` (obj|null, opcional): coordenadas GPS si el cliente las tiene.
- `cliente` (str, opcional): identificador del nodo o cliente (`meshtastic:!xxxx`, `telegram:123`).
- `id_conversacion` (str|null, opcional): identificador para correlar memoria multi-turno (hasta 20 turnos con compactación por IA y TTL de 1 hora).
- `reset_conversacion` (bool, opcional, def. `false`): si es `true`, archiva el contexto previo antes de responder.

## 2. API del bot — respuesta (SIEMPRE JSON)

```json
{
  "ok": true,
  "mensajes": [
    "Sal del agua. No frotes ni uses agua dulce.",
    "Retira tentáculos con pinzas. Aplica agua de mar caliente 20 min.",
    "Si cuesta respirar o empeora: 112. Info orientativa."
  ],
  "categoria": "fauna",
  "confianza": 0.82,
  "fuentes": [
    { "titulo": "Cruz Roja - picaduras marinas", "fecha": "2024-05-01" }
  ],
  "modelo": "qwen2.5-1.5b-instruct-q4_k_m",
  "tiempo_ms": 18450,
  "truncado": false
}
```

Reglas:
- `mensajes`: lista de **1 a 3** cadenas, cada una **≤ 250 caracteres**.
  Objetivo 1; usar más solo si es estrictamente necesario.
- En categorías médicas/riesgo vital, el último mensaje incluye el aviso
  (`RESP_DISCLAIMER_MEDICO`).
- Si no hay contexto suficiente, `ok: true` pero los `mensajes` lo indican
  ("No tengo datos fiables para esto; ante urgencia llama al 112") y
  `confianza` baja. **No se inventan protocolos.**
- Errores: `{ "ok": false, "error": "codigo", "detalle": "..." }` con HTTP 4xx/5xx.

## 3. Formato de fragmento del RAG (interno)

Cada unidad indexable de conocimiento. Estructura mínima (ampliable):

```json
{
  "id": "uuid",
  "texto": "Texto del fragmento, autocontenido y conciso.",
  "fuente": "Cruz Roja Española",
  "fuente_url": "https://...",
  "fecha": "2024-05-01",
  "categoria": "primeros_auxilios",
  "subcategoria": "picaduras_marinas",
  "provincia": "Cádiz",
  "nivel_confianza": "alta",
  "licencia": "CC-BY-4.0",
  "validado_por": "operador|null",
  "validado_fecha": "2026-06-21|null",
  "hash_contenido": "sha256(...)",
  "embedding": "vector(384)"
}
```

- `categoria` ∈ {`primeros_auxilios`, `fauna`, `flora`, `geografia`,
  `supervivencia`, `orientacion`, `clima`, `cultura_historia`}.
- `nivel_confianza` ∈ {`alta`, `media`, `baja`}. Las fuentes oficiales y
  validadas son `alta`; scraping no verificado nunca supera `media` y **no se
  indexa** si es contenido sensible sin validación.
- `validado_por` es obligatorio (no nulo) para `primeros_auxilios` y para fauna/flora
  marcada como peligrosa/tóxica. Sin validación → permanece en staging.
- `hash_contenido`: garantiza idempotencia en la reindexación (upsert).

## 4. Esquema relacional en PostgreSQL

- **Tabla `fragmentos`:** Almacena los chunks de texto y su vector embedding (`vector(384)`). Índice vectorial HNSW/IVFFlat.
- **Tabla `conversaciones`:** Sesiones de chat indexadas por `id` y `cliente_id` con `resumen` sintético de IA, `actualizado_en` y flag `activa` (TTL 3600 s).
- **Tabla `mensajes_conversacion`:** Historial detallado de cada turno (`conversacion_id`, `rol`, `contenido`, `orden`, `metadatos` JSONB).
- **Tabla `fuentes`:** Catálogo de fuentes, licencia y política de actualización.
- **Tabla `ingestas`:** Auditoría de ejecuciones del actualizador manual (`actualizar_fuente.py`).
- **Tabla `schema_migrations`:** Registro idempotente de migraciones SQL aplicadas.

Consulta los DDL en `deploy/postgres/migrations/0001_init.sql` y `0002_conversaciones.sql`.

## 5. Plantilla de prompt (esquema)

```
[SISTEMA]
Eres un asistente de emergencia para la provincia de {PROVINCIA}.
Responde SIEMPRE en español, de forma breve y práctica.
Usa SOLO la información del CONTEXTO. Si el contexto no basta, dilo y
recomienda llamar al 112. No inventes datos médicos ni de especies.
Límite: 3 frases muy cortas.

[CONTEXTO]
{fragmentos recuperados, con su fuente}

[CONSULTA]
{consulta del usuario}
```

El post-proceso (no el modelo) garantiza el límite duro de 250×3 caracteres.

---

[← Volver al Índice de Documentación Técnica](README.md)

