# Módulo 07 · Calidad, seguridad y observabilidad

## Resumen

Endurece el sistema antes de producción: garantiza la **validación humana** del
contenido sensible, los **avisos legales/médicos**, la **anti-alucinación**
(el LLM solo usa el contexto), las **pruebas** automatizadas, la
**observabilidad** (logs y métricas ligeras) y los **backups**. Transversal a la
API y al actualizador. Es lo que diferencia un prototipo de algo que puede
asistir a una persona en apuros con responsabilidad.

Dependencias: 04, 05. Habilita: Hito D.

## Fase 1 — Seguridad del contenido

- Reforzar el **checkpoint humano** (módulo 05) como puerta única para indexar
  primeros auxilios y especies peligrosas.
- Reglas de prompt anti-alucinación: "usa solo el contexto; si falta, dilo y
  recomienda 112". Pruebas que verifiquen el comportamiento sin contexto.
- Avisos: inserción automática de `RESP_DISCLAIMER_MEDICO` por categoría.
- Política documentada de "qué NO hace el bot" (no diagnostica, no sustituye al
  112) visible para integradores.

## Fase 2 — Seguridad técnica

- Autenticación de la API por token; rotación documentada.
- Secretos solo en `env.py` (nunca en git); revisión de que no se filtran en
  logs.
- Hardening de PostgreSQL local (acceso solo localhost, credenciales propias).
- Límites de tamaño de petición y saneamiento de entrada.

## Fase 3 — Pruebas

- Unitarias: post-proceso 250×3, normalización de fragmentos, recuperación.
- Integración: pipeline API end-to-end y pipeline del actualizador.
- Pruebas de regresión del RAG (set de evaluación del módulo 03).
- Pruebas de "camino triste": LLM caído, BD caída, timeout, sin contexto.

## Fase 4 — Observabilidad

- Logging estructurado por servicio (`LOG_LEVEL`, `LOG_DIR`).
- Métricas ligeras: latencia por petición, tasa de "sin contexto", uso de RAM,
  recuentos de ingesta. Evitar dependencias pesadas (un endpoint/fichero basta).
- Healthchecks (`/health`, scripts) integrables con systemd.

## Fase 5 — Backups y recuperación

- Backup periódico de la BD (`pg_dump`) y del staging aprobado.
- Procedimiento de restauración documentado.
- Plan ante corrupción de SD: reconstruir desde backups + reindexar.

## Fase 6 — Documentación de calidad

- Checklist de "listo para producción".
- Notas de evaluación del modelo elegido (calidad en español, casos fallidos).
- Registro de decisiones y limitaciones conocidas.

## Verificación del módulo

- Suite de pruebas verde en CI local.
- Intento de indexar contenido sensible sin validación → bloqueado.
- Backup y restauración probados de extremo a extremo.

## Checklist

> Leyenda de estado (autogenerada en la fase de implementación): [x] = terminado en código y verificado en sandbox · [ ] = pendiente de ejecutar en la Raspberry Pi o con BD/red en vivo (compilar llama.cpp en ARM, descargar modelo, levantar PostgreSQL, pruebas de integración).


- [x] Fase 1: checkpoint humano reforzado como puerta única.
- [x] Fase 1: reglas anti-alucinación con pruebas del caso sin contexto.
- [x] Fase 1: avisos médicos automáticos por categoría.
- [ ] Fase 1: política "qué NO hace el bot" documentada.
- [x] Fase 2: auth por token y rotación documentada.
- [x] Fase 2: secretos fuera de git y de logs.
- [ ] Fase 2: hardening de PostgreSQL local.
- [x] Fase 2: límites de tamaño y saneamiento de entrada.
- [x] Fase 3: pruebas unitarias clave (post-proceso, normalización, retrieval).
- [ ] Fase 3: pruebas de integración de ambos pipelines.
- [x] Fase 3: regresión del RAG y casos de "camino triste".
- [ ] Fase 4: logging estructurado y métricas ligeras.
- [ ] Fase 4: healthchecks integrables con systemd.
- [x] Fase 5: backups (`pg_dump`) y restauración probada.
- [ ] Fase 6: checklist de "listo para producción" y limitaciones conocidas.
- [ ] Verificación: suite verde; indexado sin validación bloqueado.
