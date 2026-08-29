"""Evaluación masiva del banco de pruebas contra la base vectorial y el LLM."""

from __future__ import annotations

import json
import time
import sys
from common.config import settings
from api.rag.embeddings import get_embedder
from common.db import cursor
from psycopg.rows import dict_row

CASOS = [
    # 1. Primeros Auxilios
    ("primeros_auxilios", "RCP Adulto", "Hay un hombre inconsciente y no respira, que hago"),
    ("primeros_auxilios", "Uso DEA", "Como usar un desfibrilador DEA en un adulto"),
    ("primeros_auxilios", "Atragantamiento", "Un adulto se esta atragantando y no puede hablar ni toser"),
    ("primeros_auxilios", "Pez araña", "He pisado un pez araña en la orilla del mar me arde el pie"),
    ("primeros_auxilios", "Medusa", "Me ha picado una medusa en la playa que me pongo"),
    ("primeros_auxilios", "Víbora", "Me ha mordido una serpiente en el monte que no debo hacer"),
    ("primeros_auxilios", "Hemorragia", "Tengo un corte profundo en el antebrazo y sangra mucho"),
    ("primeros_auxilios", "Fractura pierna", "Me he caido y tengo la pierna deformada con mucho dolor"),
    ("primeros_auxilios", "Quemadura", "Me he quemado la mano con agua hirviendo y sale ampolla"),

    # 2. Supervivencia
    ("supervivencia", "Agua costa", "Como conseguir y potabilizar agua en la costa sin equipo"),
    ("supervivencia", "Fuego pedernal", "Como encender fuego con pedernal si la madera esta humeda"),
    ("supervivencia", "Señales heli", "Cuales son las señales con el cuerpo para el helicoptero de rescate"),
    ("supervivencia", "Silbato montaña", "Cual es la señal internacional de socorro en montaña con silbato"),
    ("supervivencia", "Estrella polar", "Como orientarse de noche buscando el norte con la estrella polar"),

    # 3. Geografía
    ("geografia", "Villaluenga", "Donde esta Villaluenga del Rosario y que altitud tiene"),
    ("geografia", "Grazalema", "Informacion geografica y situacion de Grazalema en Cadiz"),
    ("geografia", "Pinsapar", "Donde esta el sendero del Pinsapar de Grazalema"),
    ("geografia", "Playa Bolonia", "Donde esta la playa de Bolonia y como se accede"),

    # 4. Transporte
    ("transporte", "Cercanías C-1", "Que estaciones recorre la linea C-1 de Cercanias de Cadiz"),
    ("transporte", "Bus M-010", "Que recorrido hace la linea de autobus M-010 en Cadiz"),
    ("transporte", "Estación Bahía Sur", "Donde esta la estacion de tren de San Fernando Bahia Sur"),

    # 5. Directorios
    ("directorios", "GC Chiclana", "Telefono y direccion del puesto de la Guardia Civil de Chiclana"),
    ("directorios", "112 vs 061", "Para que sirve el 112 y cuando llamar al 061"),

    # 6. Protección Civil
    ("proteccion_civil", "Incendio", "Que hacer si un incendio forestal me corta el camino en la sierra"),
    ("proteccion_civil", "Riada coche", "Que hacer si el agua sube y atrapa mi coche en una crecida"),
    ("proteccion_civil", "Terremoto", "Que hacer dentro de una casa durante un terremoto"),

    # 7. Toxicología
    ("toxicologia", "Marea roja", "Riesgo de comer coquinas o mejillones recogidos en marea roja"),
    ("toxicologia", "Lejía", "Un niño ha bebido lejia que debo hacer provocar el vomito"),

    # 8. Apoyo Psicosocial
    ("apoyo_psicosocial", "Pánico", "Como tranquilizar a una persona con ataque de panico tras un accidente"),

    # 9. Clima
    ("clima", "Ola de calor", "Cuales son las medidas principales ante una ola de calor extremo"),

    # 10. Fauna
    ("fauna", "Procesionaria", "Que hacer si un perro o persona toca orugas de procesionaria"),

    # 11. Anti-alucinación
    ("anti_alucinacion", "Capital Australia", "Cual es la capital de Australia"),
]

def main() -> None:
    embedder = get_embedder()
    print("=" * 80)
    print(f"EVALUACIÓN DE RECUPERACIÓN RAG: {len(CASOS)} CASOS")
    print(f"RAG_MIN_SCORE configurado: {settings.rag_min_score}")
    print("=" * 80)
    print()

    correctos = 0
    con_contexto = 0

    with cursor() as cur:
        cur.row_factory = dict_row
        for cat_esperada, nombre, query in CASOS:
            qvec = embedder.embed_query(query)
            cur.execute("""
                SELECT id, categoria, subcategoria, fuente,
                       1 - (embedding <=> %(qvec)s::vector) AS score,
                       LEFT(texto, 140) as resumen
                FROM fragmentos
                ORDER BY score DESC
                LIMIT 3;
            """, {"qvec": qvec})
            rows = cur.fetchall()

            if not rows:
                print(f"❌ [ERROR] Sin resultados en BD para: {query}")
                continue

            top = rows[0]
            top_score = float(top["score"])
            top_cat = top["categoria"]
            top_sub = top["subcategoria"]
            top_fnt = top["fuente"][:28]
            top_txt = top["resumen"].replace("\n", " ")

            pasa_umbral = top_score >= settings.rag_min_score
            categoria_ok = (cat_esperada == top_cat) or (cat_esperada == "anti_alucinacion" and not pasa_umbral)

            if categoria_ok:
                correctos += 1
            if pasa_umbral:
                con_contexto += 1

            status_cat = "✅" if (cat_esperada == top_cat) else ("⚠️" if cat_esperada == "anti_alucinacion" else "❌")
            status_umb = "🟢 Ctx OK" if pasa_umbral else "🔴 Ctx FILTRADO"

            print(f"{status_cat} [{cat_esperada:18}] {nombre:22} | TopScore: {top_score:.3f} ({status_umb}) | TopCat: {top_cat}")
            print(f"   Query: {query}")
            print(f"   Top 1 (Score {top_score:.3f}): [{top_cat}/{top_sub}] ({top_fnt}) -> {top_txt}")
            if len(rows) > 1:
                r2 = rows[1]
                print(f"   Top 2 (Score {float(r2['score']):.3f}): [{r2['categoria']}/{r2['subcategoria']}] -> {r2['resumen'][:90].replace(chr(10), ' ')}")
            print()

    print("=" * 80)
    print(f"Resumen: Categoría Top 1 esperada: {correctos}/{len(CASOS)} ({correctos/len(CASOS)*100:.1f}%)")
    print(f"Pasan umbral (>= {settings.rag_min_score}): {con_contexto}/{len(CASOS)} ({con_contexto/len(CASOS)*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    main()
