"""Gestor de memoria conversacional persistente con soporte multi-cliente.

Almacena los turnos en PostgreSQL (tablas `conversaciones` y `mensajes_conversacion`),
mantiene una ventana de hasta 20 turnos por cliente, compacta con IA el historial
antiguo cuando se supera el límite y descarta el contexto si transcurre más de 1 hora
sin actividad para ese ID.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from common.config import settings
from common.db import cursor
from common.errors import DatabaseError

_log = logging.getLogger(__name__)


class ConversationMemoryManager:
    """Administra el ciclo de vida, persistencia y compactación de conversaciones."""

    def __init__(
        self,
        max_turnos: int | None = None,
        turnos_compactar: int | None = None,
        ttl_segundos: int | None = None,
    ) -> None:
        self._max_turnos = max_turnos
        self._turnos_compactar = turnos_compactar
        self._ttl_segundos = ttl_segundos

    @property
    def max_turnos(self) -> int:
        return self._max_turnos if self._max_turnos is not None else settings.conv_max_turnos

    @property
    def turnos_compactar(self) -> int:
        return self._turnos_compactar if self._turnos_compactar is not None else settings.conv_turnos_compactar

    @property
    def ttl_segundos(self) -> int:
        return self._ttl_segundos if self._ttl_segundos is not None else settings.conv_ttl_segundos

    def obtener_historial(self, id_conversacion: str) -> list[dict[str, str]]:
        """Recupera los mensajes del historial activo para un ID de conversación.

        Devuelve una lista con formato [{"role": "...", "content": "..."}] lista para el LLM.
        Si la conversación ha expirado (más de 1 hora sin usarse) o no está activa,
        devuelve una lista vacía y archiva la sesión expirada.
        """
        if not id_conversacion:
            return []

        try:
            with cursor() as cur:
                # 1. Verificar estado de la conversación y TTL
                cur.execute(
                    """
                    SELECT id, activa, resumen,
                           EXTRACT(EPOCH FROM (NOW() - actualizado_en)) AS segundos_inactivo
                    FROM conversaciones
                    WHERE id = %s;
                    """,
                    (id_conversacion,),
                )
                fila = cur.fetchone()
                if not fila:
                    return []

                _, activa, resumen, seg_inactivo = fila
                if not activa:
                    return []

                # Si ha pasado más de 1 hora sin mensajes con ese ID, expira
                if seg_inactivo is not None and seg_inactivo > self.ttl_segundos:
                    _log.info(
                        "Conversación %s expirada por inactividad (%d s > %d s). Archivando.",
                        id_conversacion,
                        int(seg_inactivo),
                        self.ttl_segundos,
                    )
                    cur.execute(
                        "UPDATE conversaciones SET activa = FALSE WHERE id = %s;",
                        (id_conversacion,),
                    )
                    return []

                # 2. Recuperar mensajes ordenados
                cur.execute(
                    """
                    SELECT rol, contenido
                    FROM mensajes_conversacion
                    WHERE conversacion_id = %s
                    ORDER BY orden ASC;
                    """,
                    (id_conversacion,),
                )
                filas_msg = cur.fetchall()

                mensajes: list[dict[str, str]] = []
                if resumen:
                    mensajes.append(
                        {
                            "role": "system",
                            "content": f"[RESUMEN DE CONVERSACIÓN PREVIA]: {resumen}",
                        }
                    )

                for rol, cont in filas_msg:
                    mensajes.append({"role": rol, "content": cont})

                return mensajes

        except Exception as exc:
            _log.error("Error obteniendo historial de conversación %s: %s", id_conversacion, exc)
            return []

    def guardar_turno(
        self,
        id_conversacion: str,
        cliente_id: str,
        consulta_usuario: str,
        respuesta_asistente: str,
        metadatos: dict[str, Any] | None = None,
        llm: Any = None,
    ) -> dict[str, Any]:
        """Guarda un nuevo turno (usuario y respuesta) y aplica compactación si procede."""
        if not id_conversacion:
            return {"turnos": 0, "compactado": False}

        cliente = cliente_id or id_conversacion
        compactado = False
        turnos_activos = 1

        try:
            with cursor() as cur:
                # 1. Upsert de la conversación (crear o reactivar y refrescar timestamp)
                cur.execute(
                    """
                    INSERT INTO conversaciones (id, cliente_id, creado_en, actualizado_en, activa)
                    VALUES (%s, %s, NOW(), NOW(), TRUE)
                    ON CONFLICT (id) DO UPDATE SET
                        cliente_id = EXCLUDED.cliente_id,
                        actualizado_en = NOW(),
                        activa = TRUE;
                    """,
                    (id_conversacion, cliente),
                )

                # 2. Obtener el siguiente número de orden
                cur.execute(
                    "SELECT COALESCE(MAX(orden), 0) FROM mensajes_conversacion WHERE conversacion_id = %s;",
                    (id_conversacion,),
                )
                max_orden = cur.fetchone()[0]

                # 3. Insertar mensaje de usuario
                cur.execute(
                    """
                    INSERT INTO mensajes_conversacion (conversacion_id, rol, contenido, orden)
                    VALUES (%s, 'user', %s, %s);
                    """,
                    (id_conversacion, consulta_usuario, max_orden + 1),
                )

                # 4. Insertar mensaje de asistente con metadatos
                meta_json = json.dumps(metadatos, ensure_ascii=False) if metadatos else None
                cur.execute(
                    """
                    INSERT INTO mensajes_conversacion (conversacion_id, rol, contenido, orden, metadatos)
                    VALUES (%s, 'assistant', %s, %s, %s::jsonb);
                    """,
                    (id_conversacion, respuesta_asistente, max_orden + 2, meta_json),
                )

                # 5. Comprobar si se excede el límite de 20 turnos (40 mensajes)
                cur.execute(
                    "SELECT COUNT(*) FROM mensajes_conversacion WHERE conversacion_id = %s;",
                    (id_conversacion,),
                )
                total_mensajes = cur.fetchone()[0]
                limite_mensajes = self.max_turnos * 2

                if total_mensajes > limite_mensajes and llm is not None:
                    self._compactar_historial(cur, id_conversacion, llm)
                    compactado = True

                # Conteo final de turnos activos (mensajes // 2)
                cur.execute(
                    "SELECT COUNT(*) FROM mensajes_conversacion WHERE conversacion_id = %s;",
                    (id_conversacion,),
                )
                total_actual = cur.fetchone()[0]
                turnos_activos = (total_actual + 1) // 2

            return {"turnos": turnos_activos, "compactado": compactado}

        except Exception as exc:
            _log.error("Error guardando turno en conversación %s: %s", id_conversacion, exc)
            return {"turnos": 0, "compactado": False}

    def _compactar_historial(self, cur: Any, id_conversacion: str, llm: Any) -> None:
        """Compacta con IA los turnos antiguos que exceden el límite reciente."""
        try:
            # Obtener todos los mensajes ordenados
            cur.execute(
                """
                SELECT id, rol, contenido
                FROM mensajes_conversacion
                WHERE conversacion_id = %s
                ORDER BY orden ASC;
                """,
                (id_conversacion,),
            )
            todos = cur.fetchall()
            conservar_cnt = self.turnos_compactar * 2
            if len(todos) <= conservar_cnt:
                return

            a_compactar = todos[:-conservar_cnt]
            ids_a_eliminar = [m[0] for m in a_compactar]

            # Formatear texto a resumir
            texto_a_resumir = "\n".join(
                f"{'Usuario' if m[1] == 'user' else 'Asistente'}: {m[2]}" for m in a_compactar
            )

            # Obtener resumen previo si existía
            cur.execute("SELECT resumen FROM conversaciones WHERE id = %s;", (id_conversacion,))
            resumen_previo = cur.fetchone()[0] or ""

            prompt_resumen = [
                {
                    "role": "system",
                    "content": (
                        "Eres un asistente de síntesis. Resume de forma MUY breve (máximo 2 frases) "
                        "los hechos clave, síntomas o situación del usuario descritos en este diálogo previo."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Resumen anterior: {resumen_previo}\n\n"
                        f"Nuevos turnos a compactar:\n{texto_a_resumir}\n\n"
                        "Genera el nuevo resumen consolidado breve:"
                    ),
                },
            ]

            nuevo_resumen = llm.chat(prompt_resumen).strip()

            # Guardar resumen en la conversación y eliminar los mensajes antiguos de la tabla activa
            cur.execute(
                "UPDATE conversaciones SET resumen = %s WHERE id = %s;",
                (nuevo_resumen, id_conversacion),
            )
            cur.execute(
                "DELETE FROM mensajes_conversacion WHERE id = ANY(%s);",
                (ids_a_eliminar,),
            )
            _log.info(
                "Conversación %s compactada: %d mensajes sintetizados en resumen.",
                id_conversacion,
                len(ids_a_eliminar),
            )
        except Exception as exc:
            _log.warning("No se pudo compactar la conversación %s: %s", id_conversacion, exc)

    def resetear_conversacion(self, id_conversacion: str) -> bool:
        """Marca una conversación como inactiva para empezar un hilo nuevo."""
        if not id_conversacion:
            return False

        try:
            with cursor() as cur:
                cur.execute(
                    "UPDATE conversaciones SET activa = FALSE WHERE id = %s RETURNING id;",
                    (id_conversacion,),
                )
                row = cur.fetchone()
                return row is not None
        except Exception as exc:
            _log.error("Error reseteando conversación %s: %s", id_conversacion, exc)
            return False


# Singleton del gestor de memoria
conversation_memory = ConversationMemoryManager()
