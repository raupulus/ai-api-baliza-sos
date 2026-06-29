"""Construcción del prompt para el LLM. Lógica pura y testeable."""

from __future__ import annotations

from common.config import settings

# Plantilla del sistema: reglas de brevedad, español, y anti-alucinación.
_SISTEMA = (
    "Eres un asistente de emergencia y supervivencia para la provincia de {provincia} "
    "({pais}). Respondes SIEMPRE en español, de forma muy breve y práctica, con "
    "instrucciones accionables. Usa EXCLUSIVAMENTE la información del CONTEXTO. "
    "Si el contexto no es suficiente, dilo claramente y recomienda llamar al 112; "
    "NO inventes datos médicos, de especies ni de lugares. Máximo 3 frases cortas."
)

_SIN_CONTEXTO = (
    "No hay CONTEXTO disponible para esta consulta. Responde brevemente que no "
    "dispones de información fiable para ayudar con seguridad y recomienda llamar "
    "al 112 si es una urgencia. No inventes."
)


def construir_prompt(consulta: str, contexto: str, *, suficiente: bool) -> str:
    """Ensambla el prompt completo en el formato que espera llama-server."""
    sistema = _SISTEMA.format(provincia=settings.provincia, pais=settings.pais)

    if suficiente and contexto.strip():
        bloque_ctx = f"[CONTEXTO]\n{contexto}"
    else:
        bloque_ctx = f"[CONTEXTO]\n(vacío)\n{_SIN_CONTEXTO}"

    return (
        f"[SISTEMA]\n{sistema}\n\n"
        f"{bloque_ctx}\n\n"
        f"[CONSULTA]\n{consulta}\n\n"
        f"[RESPUESTA]\n"
    )
