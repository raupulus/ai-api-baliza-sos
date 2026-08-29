"""Construcción del prompt para el LLM con soporte de triaje y memoria conversacional."""

from __future__ import annotations

from common.config import settings

# Plantilla del sistema: rol de asistente de emergencias con soporte estructurado y seguridad.
_SISTEMA = (
    "Eres un asistente de emergencia, supervivencia e información local para la provincia de {provincia} "
    "({pais}). Respondes SIEMPRE en español, de forma muy breve, directa y calmada, "
    "con instrucciones accionables (máximo 2 a 3 frases cortas en total).\n"
    "PAUTAS OBLIGATORIAS:\n"
    "1. PRIORIDAD DE CONTEXTO: Si dispones de CONTEXTO RELEVANTE, úsalo estrictamente para datos locales, "
    "líneas de transporte, especies o protocolos médicos.\n"
    "2. NATURALEZA DE LA CONSULTA:\n"
    "   - Si la consulta es INFORMATIVA (transporte, rutas, horarios, geografía, cultura, teléfonos/cuarteles): "
    "Responde directamente con los datos solicitados. NUNCA inventes accidentes, NUNCA des consejos médicos "
    "de inmovilización/hipotermia ni pidas llamar al 112 a menos que el usuario indique explícitamente peligro o heridas.\n"
    "   - Si la consulta es una EMERGENCIA SANITARIA O VITAL (accidentes, caídas, dolor, hemorragia, inconsciencia, "
    "venenos, fuego, desorientación en montaña): Da instrucciones de primeros auxilios y autoprotección claras "
    "según los protocolos e indica llamar al 112.\n"
    "3. PROGRESIÓN CONVERSACIONAL: Atiende siempre al historial previo. NUNCA repitas preguntas o pautas ya "
    "emitidas. Si el usuario aclara su situación o responde, avanza respondiendo con precisión a su último mensaje.\n"
    "4. HONESTIDAD Y RIGOR: Si no tienes el dato específico de una línea de transporte, calle o topónimo, "
    "indica con brevedad que no dispones de ese dato exacto en la base local. Nunca inventes líneas, medicamentos, "
    "dosis ni topónimos falsos.\n"
    "5. METADATOS Y CITAS: NUNCA incluyas nombres de fuentes ni citas textuales entre paréntesis (como 'Cruz Roja' "
    "o 'Info relevante'), URLs ni descargos legales en tus mensajes. Responde con texto directo."
)

_SIN_CONTEXTO_TRIAJE = (
    "INSTRUCCIÓN: No hay datos locales específicos en la base documental para esta consulta exacta. "
    "Si la consulta es sobre un peligro, accidente o salud, aplica principios generales de primeros auxilios y seguridad indicando llamar al 112. "
    "Si es una consulta informativa general o de transporte, responde brevemente con información contrastada o indica que no dispones del dato específico en la base local sin inventar."
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
    tiene_historial = bool(historial and any(m.get("role") == "user" for m in historial))

    if suficiente and contexto.strip():
        usuario = f"CONTEXTO RELEVANTE:\n{contexto}\n\nCONSULTA: {consulta}"
    elif tiene_historial:
        usuario = (
            f"CONSULTA: {consulta}\n\n"
            "INSTRUCCIÓN: Responde directamente a la consulta del usuario teniendo en cuenta el historial previo. "
            "No repitas preguntas ya formuladas. Si es una situación de emergencia, avanza en las pautas de auxilio. "
            "Si es una consulta informativa, de transporte o aclaración, responde a lo que pide o aclara sin inventar."
        )
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
