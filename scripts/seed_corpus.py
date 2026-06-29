#!/usr/bin/env python3
"""Carga un corpus semilla pequeño para probar el sistema de extremo a extremo
(Hito B) sin depender aún del actualizador. Requiere BD migrada y embeddings.

Los fragmentos sensibles de ejemplo van marcados como validados por 'seed-curado'
para reflejar que en producción habrían pasado el checkpoint humano.

Uso:
    python3 scripts/seed_corpus.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from api.rag.indexing import index_fragmentos  # noqa: E402
from common.config import settings  # noqa: E402
from common.models import Categoria, Fragmento, NivelConfianza  # noqa: E402

PROV = settings.provincia


def _semilla() -> list[Fragmento]:
    return [
        Fragmento(
            texto="Si estás perdido en la costa, sube a un punto alto y busca faros o "
            "torres vigía como referencia; la línea de costa te orienta.",
            fuente="Manual de orientación (semilla)",
            categoria=Categoria.ORIENTACION,
            provincia=PROV,
            nivel_confianza=NivelConfianza.ALTA,
            licencia="CC-BY",
        ),
        Fragmento(
            texto="Ante golpe de calor: lleva a la persona a la sombra, refresca con agua, "
            "da pequeños sorbos si está consciente y pide ayuda al 112.",
            fuente="Protección Civil (semilla, validado)",
            categoria=Categoria.PRIMEROS_AUXILIOS,
            provincia=PROV,
            nivel_confianza=NivelConfianza.ALTA,
            validado_por="seed-curado",
            validado_fecha=date.today(),
            licencia="Reutilizable",
        ),
        Fragmento(
            texto="Para conseguir agua segura, hierve durante al menos 1 minuto; evita "
            "agua estancada. En playa, no bebas agua de mar.",
            fuente="Manual de supervivencia (semilla)",
            categoria=Categoria.SUPERVIVENCIA,
            provincia=PROV,
            nivel_confianza=NivelConfianza.ALTA,
            licencia="CC-BY",
        ),
        Fragmento(
            texto="Picadura de medusa: sal del agua, no frotes ni uses agua dulce, "
            "retira restos con una tarjeta y aplica agua de mar caliente.",
            fuente="Cruz Roja (semilla, validado)",
            categoria=Categoria.FAUNA,
            subcategoria="picaduras_marinas",
            provincia=PROV,
            peligrosa=True,
            nivel_confianza=NivelConfianza.ALTA,
            validado_por="seed-curado",
            validado_fecha=date.today(),
            licencia="Reutilizable",
        ),
    ]


def main() -> int:
    frags = _semilla()
    nuevos, actualizados = index_fragmentos(frags)
    print(f"Corpus semilla cargado: {nuevos} nuevos, {actualizados} actualizados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
