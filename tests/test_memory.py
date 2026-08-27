"""Pruebas unitarias para el gestor de memoria conversacional (ConversationMemoryManager)."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from api.memory import ConversationMemoryManager


class TestConversationMemory(unittest.TestCase):

    def test_memory_manager_defaults(self):
        mgr = ConversationMemoryManager(max_turnos=15, turnos_compactar=8, ttl_segundos=1800)
        self.assertEqual(mgr.max_turnos, 15)
        self.assertEqual(mgr.turnos_compactar, 8)
        self.assertEqual(mgr.ttl_segundos, 1800)

    def test_obtener_historial_no_existente(self):
        mgr = ConversationMemoryManager(max_turnos=20, turnos_compactar=10, ttl_segundos=3600)
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = None  # No existe la conversación

        with patch("api.memory.cursor") as mock_cursor_ctx:
            mock_cursor_ctx.return_value.__enter__.return_value = mock_cur
            historial = mgr.obtener_historial("id-inexistente")
            self.assertEqual(historial, [])

    def test_obtener_historial_expirada_por_ttl(self):
        mgr = ConversationMemoryManager(max_turnos=20, turnos_compactar=10, ttl_segundos=3600)
        mock_cur = MagicMock()
        # Fila: (activa=True, resumen=None, seg_inactivo=4000.0) -> expirada (> 3600)
        mock_cur.fetchone.return_value = (True, None, 4000.0)

        with patch("api.memory.cursor") as mock_cursor_ctx:
            mock_cursor_ctx.return_value.__enter__.return_value = mock_cur
            historial = mgr.obtener_historial("id-expirado")
            self.assertEqual(historial, [])
            # Verifica que se haya ejecutado el UPDATE para marcar activa = FALSE
            update_calls = [
                call for call in mock_cur.execute.call_args_list
                if "UPDATE conversaciones SET activa = FALSE" in call[0][0]
            ]
            self.assertEqual(len(update_calls), 1)

    def test_obtener_historial_con_mensajes_y_resumen(self):
        mgr = ConversationMemoryManager(max_turnos=20, turnos_compactar=10, ttl_segundos=3600)
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = (True, "El usuario preguntó por playas", 300.0)
        mock_cur.fetchall.return_value = [
            ("user", "¿Hay medusas en Zahara?"),
            ("assistant", "No hay alertas activas de medusas hoy."),
        ]

        with patch("api.memory.cursor") as mock_cursor_ctx:
            mock_cursor_ctx.return_value.__enter__.return_value = mock_cur
            historial = mgr.obtener_historial("id-valido")
            self.assertEqual(len(historial), 3)
            self.assertEqual(historial[0]["role"], "system")
            self.assertIn("El usuario preguntó por playas", historial[0]["content"])
            self.assertEqual(historial[1]["role"], "user")
            self.assertEqual(historial[1]["content"], "¿Hay medusas en Zahara?")
            self.assertEqual(historial[2]["role"], "assistant")

    def test_resetear_conversacion(self):
        mgr = ConversationMemoryManager()
        mock_cur = MagicMock()

        with patch("api.memory.cursor") as mock_cursor_ctx:
            mock_cursor_ctx.return_value.__enter__.return_value = mock_cur
            ok = mgr.resetear_conversacion("id-a-resetear")
            self.assertTrue(ok)
            mock_cur.execute.assert_called_once_with(
                "UPDATE conversaciones SET activa = FALSE WHERE id = %s;",
                ("id-a-resetear",),
            )

    def test_guardar_turno_e_insercion(self):
        mgr = ConversationMemoryManager(max_turnos=20, turnos_compactar=10, ttl_segundos=3600)
        mock_cur = MagicMock()
        mock_cur.fetchone.side_effect = [(2,), (4,)]

        with patch("api.memory.cursor") as mock_cursor_ctx:
            mock_cursor_ctx.return_value.__enter__.return_value = mock_cur
            mgr.guardar_turno(
                id_conversacion="conv-1",
                pregunta="¿Dónde está Tarifa?",
                respuesta="Tarifa está en el extremo sur.",
                cliente_id="nodo-lora",
                metadatos={"tiempo_ms": 1200},
            )
            self.assertGreaterEqual(mock_cur.execute.call_count, 3)


if __name__ == "__main__":
    unittest.main()
