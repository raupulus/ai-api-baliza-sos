# Módulo 08 · Despliegue y operación

## Resumen

Deja el sistema corriendo de forma **nativa con systemd** en la Raspberry Pi,
arrancando solo tras un reinicio, afinado para 4 GB y con un **runbook** de
operación: instalación, tuning del SO, gestión de servicios, cambio de modelo,
actualización de la base de conocimiento y resolución de incidencias. Cierra el
proyecto para producción.

Dependencias: todos los módulos previos. Habilita: Hito D (producción).

## Fase 1 — Preparación de la Raspberry Pi

- Raspberry Pi OS **Lite** (sin escritorio) última versión.
- Almacenamiento recomendado: SSD USB (o SD de calidad).
- `zram`/swap controlado como red de seguridad.
- Usuario de servicio dedicado y permisos sobre `data/`.

## Fase 2 — Unidades systemd

- `postgresql-local.service`: arranca el clúster de `data/postgres`.
- `llama-server.service`: `llama-server` con el modelo de `env.py`.
- `bot-api.service`: Uvicorn (1 worker); `After=`/`Requires=` de postgres y
  llama-server.
- `context-updater.service` + `.timer`: ejecución programada del actualizador.
- Política de reinicio (`Restart=on-failure`) y arranque al boot.

## Fase 3 — Instalación reproducible

- Script `scripts/install.sh`: entorno, dependencias, init de BD, esquema,
  copia de unidades systemd, habilitado de servicios.
- `scripts/download_model.sh` (módulo 02) integrado en la instalación.
- Verificación post-instalación con `healthcheck.sh`.

## Fase 4 — Operación

- Runbook: arrancar/parar/reiniciar cada servicio; ver logs (`journalctl`).
- **Cambio de modelo**: editar `LLM_MODEL_PATH` → `systemctl restart
  llama-server` → verificar RAM/tiempos.
- **Actualizar conocimiento**: lanzar el actualizador, revisar staging, aprobar,
  confirmar indexado.
- **Cambio de provincia**: editar variables geográficas en `env.py`, reejecutar
  el actualizador, reindexar.

## Fase 5 — Mantenimiento

- Rotación de logs.
- Backups programados (módulo 07) y verificación periódica.
- Monitorización de RAM/temperatura/almacenamiento de la Pi.
- Procedimiento de actualización de llama.cpp/modelos/dependencias.

## Fase 6 — Validación de producción

- Arranque limpio tras reinicio físico de la Pi (todos los servicios suben).
- Prueba end-to-end desde un cliente simulado (Telegram/Meshtastic).
- Comportamiento estable bajo varias consultas seguidas (sin OOM).

## Verificación del módulo

- Reinicio físico → sistema operativo sin intervención manual.
- Cambio de modelo y de provincia probados por el procedimiento documentado.
- Backups y restauración verificados en el dispositivo.

## Checklist

- [ ] Fase 1: Raspberry Pi OS Lite y almacenamiento preparados.
- [ ] Fase 1: zram/swap y usuario de servicio configurados.
- [ ] Fase 2: `postgresql-local.service` operativo.
- [ ] Fase 2: `llama-server.service` con modelo por env.
- [ ] Fase 2: `bot-api.service` con dependencias declaradas.
- [ ] Fase 2: `context-updater` service + timer.
- [ ] Fase 2: reinicio automático y arranque al boot.
- [ ] Fase 3: `install.sh` reproducible y verificado.
- [ ] Fase 3: `healthcheck.sh` post-instalación.
- [ ] Fase 4: runbook de servicios y logs.
- [ ] Fase 4: procedimiento de cambio de modelo probado.
- [ ] Fase 4: procedimiento de actualización de conocimiento.
- [ ] Fase 4: procedimiento de cambio de provincia.
- [ ] Fase 5: rotación de logs y backups programados.
- [ ] Fase 5: monitorización de recursos de la Pi.
- [ ] Fase 6: arranque limpio tras reinicio físico verificado.
- [ ] Fase 6: end-to-end desde cliente simulado y estabilidad sin OOM.
