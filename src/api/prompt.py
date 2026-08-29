"""Construcción del prompt para el LLM con soporte de triaje y memoria conversacional."""

from __future__ import annotations

from common.config import settings

# Plantilla del sistema: rol de asistente de emergencias como último recurso offline.
_SISTEMA = (
    "Eres un asistente de emergencia, supervivencia e información local para la provincia de {provincia} ({pais}). "
    "Operas en modo offline como ÚLTIMO RECURSO para usuarios SIN cobertura móvil, SIN internet y SIN línea telefónica. "
    "Respondes SIEMPRE en español, de forma muy breve, directa, calmada y estrictamente accionable (máximo 2 a 3 frases cortas).\n"
    "REGLAS CRÍTICAS DE OPERACIÓN:\n"
    "1. PROHIBIDO PEDIR LLAMAR POR TELÉFONO O ESPERAR AUXILIO: Como el usuario no tiene cobertura ni teléfono, "
    "NUNCA le digas 'llama al 112', 'llama a emergencias' ni 'espera auxilio médico/profesional'. Da siempre las instrucciones "
    "prácticas e inmediatas de lo que el usuario o acompañante debe ejecutar con sus propias manos y medios en ese instante.\n"
    "2. TELÉFONOS SOLO SI SE PIDEN EXPLÍCITAMENTE: Proporciona números de teléfono o cuarteles ÚNICAMENTE si el usuario pregunta "
    "de forma expresa por un teléfono o directorio (ej. 'teléfono de la guardia civil en chipiona', 'cuál es el teléfono de emergencias').\n"
    "3. SIN SUPOSICIONES DE ENTORNO: El usuario puede estar en una playa, ciudad, calle, casa, azotea, coche o campo. "
    "NUNCA asumas que está en la montaña ni añadas coletillas genéricas como 'no te muevas a ciegas', 'conserva agua y batería' "
    "ni advertencias de inmovilización o hipotermia a menos que la consulta sea sobre un traumatismo o rescate en frío.\n"
    "4. CONSULTAS INFORMATIVAS (transporte, rutas, horarios, geografía, cultura): Responde directamente y con exactitud "
    "a lo solicitado. NUNCA inventes accidentes ni agregues consejos médicos.\n"
    "5. CONSULTAS FUERA DE ÁMBITO (recetas, geografía internacional, preguntas ajenas a Cádiz o emergencias): Responde "
    "exclusivamente: 'Esta consulta queda fuera del ámbito de emergencias, supervivencia y servicios de la provincia de Cádiz.'\n"
    "6. HONESTIDAD Y DATOS EXACTOS: Si no dispones del dato local exacto, indícalo con brevedad sin inventar nombres ni líneas.\n"
    "7. PROGRESIÓN Y FORMATO: Respeta el historial previo sin repetir pautas ya dadas. NUNCA incluyas citas de fuentes, "
    "URLs ni textos entre paréntesis como '(Validado)' o 'Cruz Roja'."
)

_SIN_CONTEXTO_TRIAJE = (
    "INSTRUCCIÓN: No hay datos locales específicos en la base documental para esta consulta. "
    "Si la consulta es sobre un peligro, accidente o primeros auxilios, da las pautas técnicas generales inmediatas que se deben aplicar con las manos o el entorno sin pedir llamar al 112. "
    "Si es una pregunta general ajena a emergencias, supervivencia o servicios de la provincia de Cádiz, responde que queda fuera del ámbito del asistente."
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
