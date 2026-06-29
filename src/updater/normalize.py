"""Política de normalización y clasificación de fragmentos.

Aplica reglas transversales antes del staging/indexado:
  - El contenido sensible o no verificado no puede declararse de confianza ALTA
    sin validación humana.
  - Separa los fragmentos en (indexables directos) y (a checkpoint).
"""

from __future__ import annotations

from common.models import Fragmento, NivelConfianza


def aplicar_politica(fragmentos: list[Fragmento]) -> list[Fragmento]:
    """Ajusta el nivel de confianza según la política de seguridad."""
    for f in fragmentos:
        # Sin validar y sensible/peligroso => como mucho MEDIA.
        if f.requiere_validacion and not f.validado:
            if f.nivel_confianza == NivelConfianza.ALTA:
                f.nivel_confianza = NivelConfianza.MEDIA
        # Recalcular hash por si se editó el texto en normalización.
        if not f.hash_contenido:
            f.hash_contenido = f.calcular_hash()
    return fragmentos


def separar(fragmentos: list[Fragmento]) -> tuple[list[Fragmento], list[Fragmento]]:
    """Devuelve (indexables_directos, a_checkpoint)."""
    directos: list[Fragmento] = []
    checkpoint: list[Fragmento] = []
    for f in fragmentos:
        if f.requiere_validacion and not f.validado:
            checkpoint.append(f)
        else:
            directos.append(f)
    return directos, checkpoint
