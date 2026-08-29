"""Limpia frases de 'llama al 112' y 'acude al médico' de los fragmentos RAG,
enfocándolos 100% en acciones físicas y de supervivencia en el terreno."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

STAGING_APROBADOS = Path(__file__).resolve().parent.parent / "data" / "staging" / "aprobados"

# Excluir fragmentos de directorios donde los teléfonos son el dato buscado
EXCLUIR_CATEGORIAS = {"directorios"}

PATRONES_REEMPLAZO = [
    (re.compile(r"Llama al 112 de inmediato en manos libres\.?\s*", re.IGNORECASE), ""),
    (re.compile(r"Llama al 112 [^.]*\.?\s*", re.IGNORECASE), ""),
    (re.compile(r"Llamar al 112 [^.]*\.?\s*", re.IGNORECASE), ""),
    (re.compile(r"llama al 112\.?\s*", re.IGNORECASE), ""),
    (re.compile(r"llama al 112 y [^.]*\.?\s*", re.IGNORECASE), ""),
    (re.compile(r"y llama al 112\.?\s*", re.IGNORECASE), ""),
    (re.compile(r"y llama de inmediato al 112[^.]*\.?\s*", re.IGNORECASE), ""),
    (re.compile(r"acude a un centro sanitario\.?\s*", re.IGNORECASE), ""),
    (re.compile(r"acude al médico\.?\s*", re.IGNORECASE), ""),
    (re.compile(r"acude al veterinario cuanto antes[^.]*\.?\s*", re.IGNORECASE), "mantén al animal en reposo e inmovilizado."),
]

def main() -> None:
    modificados = 0
    total = 0
    for p in STAGING_APROBADOS.glob("*.json"):
        total += 1
        data = json.loads(p.read_text(encoding="utf-8"))
        if data.get("categoria") in EXCLUIR_CATEGORIAS:
            continue
        
        texto_orig = data.get("texto", "")
        texto_limpio = texto_orig
        for pat, repl in PATRONES_REEMPLAZO:
            texto_limpio = pat.sub(repl, texto_limpio)
        
        # Limpiar espacios dobles o saltos de línea huérfanos
        texto_limpio = re.sub(r" +", " ", texto_limpio)
        texto_limpio = re.sub(r"\n\s*\n+", "\n\n", texto_limpio).strip()

        if texto_limpio != texto_orig:
            data["texto"] = texto_limpio
            h = hashlib.sha256(texto_limpio.encode("utf-8")).hexdigest()
            data["hash_contenido"] = h
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            modificados += 1

    print(f"Sanitizados {modificados}/{total} fragmentos en {STAGING_APROBADOS}")

if __name__ == "__main__":
    main()
