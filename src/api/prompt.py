"""Construcción del prompt para el LLM con soporte de triaje y memoria conversacional."""

from __future__ import annotations

from common.config import settings

# Plantilla del sistema: rol de asistente de emergencias con triaje activo y seguridad.
_SISTEMA = (
    "Eres un asistente de emergencia y supervivencia para la provincia de {provincia} "
    "({pais}). Respondes SIEMPRE en español, de forma muy breve, directa y calmada, "
    "con instrucciones accionables (máximo 3 frases cortas en total).\n"
    "PAUTAS OBLIGATORIAS:\n"
    "1. Si dispones de CONTEXTO relevante, priorízalo estrictamente para datos locales, "
    "especies o protocolos médicos.\n"
    "2. Si falta información o el usuario está en peligro (caídas, desorientación, dolor): "
    "realiza TRIAJE ACTIVO. Pregunta primero por la gravedad inmediata (ej. si puede apoyar "
    "el pie, si hay hemorragia, si ve puntos de referencia) y da pautas inmediatas de "
    "estabilización/seguridad (no moverse a ciegas, conservar agua y batería).\n"
    "3. Nunca inventes medicamentos, dosis ni topónimos falsos. Ante riesgo vital o duda, "
    "indica claramente llamar al 112 indicando las referencias del lugar."
)

_SIN_CONTEXTO_TRIAJE = (
    "INSTRUCCIÓN: No hay datos documentales específicos en la base local para esta consulta exacta. "
    "Aplica protocolo de triaje y supervivencia: evalúa la gravedad física con una pregunta clave, "
    "proporciona pautas de seguridad inmediatas y recomienda coordinar con el 112. "
    "No inventes datos médicos complejos ni nombres ficticios."
)


def construir_mensajes(
    consulta: str,
    contexto: str,
    *,
    suficiente: bool,
    historial: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Construye los mensajes para `/v1/chat/completions` incluyendo historial y triaje."""
    sistema = _SISTEMA.format(provincia=settings.provincia, pais=settings.pais)
    mensajes: list[dict[str, str]] = [{"role": "system", "content": sistema}]

    # Inserción de turnos previos (máx. 20 turnos = 40 mensajes)
    if historial:
        for msg in historial:
            rol = msg.get("role", "user")
            cont = msg.get("content", "").strip()
            if cont and rol in ("user", "assistant", "system"):
                mensajes.append({"role": rol, "content": cont})

    # Turno actual
    if suficiente and contexto.strip():
        usuario = f"CONTEXTO RELEVANTE:\n{contexto}\n\nCONSULTA: {consulta}"
    else:
        usuario = f"CONSULTA: {consulta}\n\n{_SIN_CONTEXTO_TRIAJE}"

    mensajes.append({"role": "user", "content": usuario})
    return mensajes


def construir_prompt(consulta: str, contexto: str, *, suficiente: bool) -> str:
    """Variante legacy de texto plano."""
    sistema = _SISTEMA.format(provincia=settings.provincia, pais=settings.pais)
    if suficiente and contexto.strip():
        bloque_ctx = f"[CONTEXTO]\n{contexto}"
    else:
        bloque_ctx = f"[CONTEXTO]\n(sin datos locales específicos)\n{_SIN_CONTEXTO_TRIAJE}"

    return (
        f"[SISTEMA]\n{sistema}\n\n"
        f"{bloque_ctx}\n\n"
        f"[CONSULTA]\n{consulta}\n\n"
        f"[RESPUESTA]\n"
    )
