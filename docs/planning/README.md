# docs/planning — Planificación y Hoja de Ruta

> **Última actualización:** 2026-08-27  
> **Ámbito:** Organización de sprints, diseño de fases y archivo histórico.

Este directorio gestiona la planificación operativa del proyecto.

---

## 1. Regla de Oro para Agentes de IA y Colaboradores

> [!IMPORTANT]
> **Actualización Obligatoria tras Implementar:**
> Cada vez que se complete la implementación de una funcionalidad planificada, el agente o colaborador DEBE actualizar inmediatamente la hoja de ruta y marcar las tareas correspondientes como completadas en la documentación (`docs/info/06-estado-implementacion.md` y `CHANGELOG.md`).

---

## 2. Estructura del Directorio

* **[`archive/`](archive/):** Archivo histórico de planes iniciales completados o superados:
  * [`archive/initial_plan/`](archive/initial_plan/): Planificación fundacional de 8 módulos (00 a 08).
  * [`archive/checks/`](archive/checks/): Checkpoints de validación de fases previas.

---

## 3. Hoja de Ruta Activa

El estado real y vivo de la implementación se mantiene centralizado en:
* **[`../info/06-estado-implementacion.md`](../info/06-estado-implementacion.md):** Matriz de módulos y estado en producción.
* **[`../../CHANGELOG.md`](../../CHANGELOG.md):** Historial cronológico de versiones y novedades.
