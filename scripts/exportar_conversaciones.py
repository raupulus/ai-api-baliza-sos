#!/usr/bin/env python3
"""Script CLI para exportar el historial de conversaciones y mensajes a JSONL o CSV.

Permite filtrar por cliente, ID de conversación, estado activo o fecha, facilitando
auditorías de emergencias, evaluación de calidad y métricas de soporte.

Uso:
    python3 scripts/exportar_conversaciones.py --formato jsonl --salida conversaciones.jsonl
    python3 scripts/exportar_conversaciones.py --cliente "meshtastic:!abcd1234" --formato csv --salida cliente.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

# Añadir src/ al path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))

from common.db import cursor  # noqa: E402
from common.logging import get_logger  # noqa: E402

_log = get_logger("exportar_conversaciones")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Exporta conversaciones y mensajes desde PostgreSQL a JSONL o CSV.",
    )
    parser.add_argument(
        "--cliente",
        type=str,
        default=None,
        help="Filtrar por identificador de cliente (ej. 'meshtastic:!2a4b6c8d').",
    )
    parser.add_argument(
        "--conversacion",
        type=str,
        default=None,
        help="Filtrar por ID exacto de conversación.",
    )
    parser.add_argument(
        "--activas-solo",
        action="store_true",
        help="Exportar únicamente conversaciones que sigan marcadas como activas.",
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=1000,
        help="Cantidad máxima de conversaciones a recuperar (def. 1000).",
    )
    parser.add_argument(
        "--formato",
        choices=["jsonl", "csv"],
        default="jsonl",
        help="Formato de exportación ('jsonl' o 'csv', def. 'jsonl').",
    )
    parser.add_argument(
        "--salida",
        type=str,
        default=None,
        help="Ruta del archivo de salida (si no se especifica, imprime en stdout).",
    )
    return parser.parse_args()


def exportar() -> None:
    args = parse_args()

    query_conv = """
        SELECT id, cliente_id, resumen, activa, creado_en, actualizado_en
        FROM conversaciones
        WHERE 1=1
    """
    params_conv: list[object] = []

    if args.cliente:
        query_conv += " AND cliente_id = %s"
        params_conv.append(args.cliente)
    if args.conversacion:
        query_conv += " AND id = %s"
        params_conv.append(args.conversacion)
    if args.activas_solo:
        query_conv += " AND activa = TRUE"

    query_conv += " ORDER BY actualizado_en DESC LIMIT %s;"
    params_conv.append(args.limite)

    out_file = open(args.salida, "w", encoding="utf-8") if args.salida else sys.stdout

    try:
        with cursor() as cur:
            cur.execute(query_conv, tuple(params_conv))
            conversaciones = cur.fetchall()

            if not conversaciones:
                _log.info("No se encontraron conversaciones con los filtros especificados.")
                return

            if args.formato == "csv":
                writer = csv.writer(out_file)
                writer.writerow([
                    "conversacion_id",
                    "cliente_id",
                    "orden",
                    "rol",
                    "contenido",
                    "creado_en",
                    "metadatos",
                ])
                for conv in conversaciones:
                    conv_id = conv[0]
                    cur.execute(
                        """
                        SELECT orden, rol, contenido, creado_en, metadatos
                        FROM mensajes_conversacion
                        WHERE conversacion_id = %s
                        ORDER BY orden ASC;
                        """,
                        (conv_id,),
                    )
                    for m in cur.fetchall():
                        writer.writerow([
                            conv_id,
                            conv[1],
                            m[0],
                            m[1],
                            m[2],
                            m[3].isoformat() if isinstance(m[3], datetime) else str(m[3]),
                            json.dumps(m[4], ensure_ascii=False) if m[4] else "{}",
                        ])

            else:  # jsonl
                for conv in conversaciones:
                    conv_id = conv[0]
                    cur.execute(
                        """
                        SELECT orden, rol, contenido, creado_en, metadatos
                        FROM mensajes_conversacion
                        WHERE conversacion_id = %s
                        ORDER BY orden ASC;
                        """,
                        (conv_id,),
                    )
                    mensajes = []
                    for m in cur.fetchall():
                        mensajes.append({
                            "orden": m[0],
                            "rol": m[1],
                            "contenido": m[2],
                            "creado_en": m[3].isoformat() if isinstance(m[3], datetime) else str(m[3]),
                            "metadatos": m[4] or {},
                        })

                    item = {
                        "id": conv[0],
                        "cliente_id": conv[1],
                        "resumen": conv[2],
                        "activa": conv[3],
                        "creado_en": conv[4].isoformat() if isinstance(conv[4], datetime) else str(conv[4]),
                        "actualizado_en": conv[5].isoformat() if isinstance(conv[5], datetime) else str(conv[5]),
                        "mensajes": mensajes,
                    }
                    out_file.write(json.dumps(item, ensure_ascii=False) + "\n")

        if args.salida:
            _log.info("Exportadas %d conversaciones a %s", len(conversaciones), args.salida)

    finally:
        if args.salida:
            out_file.close()


if __name__ == "__main__":
    exportar()
