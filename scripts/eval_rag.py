#!/usr/bin/env python3
"""Evaluación simple del RAG: ¿se recupera el fragmento correcto en el top-k?

Lee un fichero JSON de casos (por defecto tests/data/rag_eval.json) con la forma:
    [
      {"consulta": "...", "fuente_esperada": "GBIF", "subcadena": "medusa"},
      ...
    ]
y comprueba, por cada caso, si algún fragmento recuperado coincide. Útil para
detectar regresiones al cambiar el modelo o el umbral. Requiere BD poblada.

Uso:
    python3 scripts/eval_rag.py [ruta_json]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from api.rag.retrieval import buscar  # noqa: E402

DEFAULT = Path(__file__).resolve().parents[1] / "tests" / "data" / "rag_eval.json"


def main() -> int:
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    if not ruta.exists():
        print(f"No existe el fichero de casos: {ruta}")
        return 1

    casos = json.loads(ruta.read_text(encoding="utf-8"))
    aciertos = 0
    for caso in casos:
        recuperados = buscar(caso["consulta"])
        ok = any(
            caso.get("subcadena", "").lower() in r.fragmento.texto.lower()
            or caso.get("fuente_esperada", "") == r.fragmento.fuente
            for r in recuperados
        )
        aciertos += int(ok)
        estado = "OK " if ok else "FALLO"
        top = recuperados[0].score if recuperados else 0.0
        print(f"[{estado}] {caso['consulta'][:50]:50}  top_score={top:.3f}")

    print(f"\nAciertos: {aciertos}/{len(casos)}")
    return 0 if aciertos == len(casos) else 2


if __name__ == "__main__":
    raise SystemExit(main())
