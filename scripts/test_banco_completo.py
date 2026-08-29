#!/usr/bin/env python3
"""Suite de ejecución y validación masiva por lotes del Banco de Pruebas RAG.

Ejecuta todas las combinaciones de Categoría + Subcategoría + Caso de Prueba
definidas en la interfaz web contra la API del Bot, evaluando:
1. Precisión de recuperación del RAG (categoría, score, fragmentos).
2. Cumplimiento de límites de radio LoRa (<= 200 bytes UTF-8 por paquete, máx. 3 mensajes).
3. Calidad y sentido de las respuestas del LLM (ausencia de alucinaciones médicas en transporte,
   protocolos RCP válidos, teléfonos reales, etc.).
4. Genera un informe detallado con tabla de resultados e incidencias detectadas.

Uso:
    python3 scripts/test_banco_completo.py [--url http://172.18.1.121:8870] [--token TOKEN] [--output informe.md]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# ==============================================================================
# 1. CATÁLOGO COMPLETO DEL BANCO DE PRUEBAS (Sincronizado con index.html)
# ==============================================================================

BANCO_PRUEBAS = {
    "primeros_auxilios": {
        "nombre": "🩺 Primeros Auxilios",
        "tipos": {
            "soporte_vital": {
                "nombre": "Soporte Vital / RCP",
                "casos": [
                    {
                        "titulo": "Hombre inconsciente no respira (RCP)",
                        "query": "Hay un hombre inconsciente y no respira, que hago",
                        "keywords_esperadas": ["112", "compresion", "pecho", "30"],
                        "keywords_prohibidas": ["inmovilizar la bota", "hipotermia"]
                    },
                    {
                        "titulo": "Uso de Desfibrilador (DEA)",
                        "query": "Como usar un desfibrilador DEA en un adulto",
                        "keywords_esperadas": ["dea", "parche", "pecho", "descarga"],
                        "keywords_prohibidas": []
                    },
                    {
                        "titulo": "Soporte vital básico pediátrico",
                        "query": "Un niño no respira como hacer RCP pediatrico",
                        "keywords_esperadas": ["ventilacion", "compresion", "112"],
                        "keywords_prohibidas": []
                    }
                ]
            },
            "atragantamiento": {
                "nombre": "Atragantamiento (OVACE)",
                "casos": [
                    {
                        "titulo": "Atragantamiento severo adulto (Heimlich)",
                        "query": "Un adulto se esta atragantando y no puede hablar ni toser",
                        "keywords_esperadas": ["golpe", "espalda", "ombligo", "heimlich", "compresion"],
                        "keywords_prohibidas": []
                    },
                    {
                        "titulo": "Atragantamiento en lactante/bebé",
                        "query": "Un bebe se ha atragantado con un objeto que hago",
                        "keywords_esperadas": ["espalda", "boca", "golpe", "112"],
                        "keywords_prohibidas": []
                    }
                ]
            },
            "picaduras_mordeduras": {
                "nombre": "Picaduras y Mordeduras",
                "casos": [
                    {
                        "titulo": "Picadura de pez araña en la playa",
                        "query": "He pisado un pez araña en la orilla del mar me arde el pie",
                        "keywords_esperadas": ["caliente", "agua", "40", "termolabil"],
                        "keywords_prohibidas": ["torniquete", "hielo"]
                    },
                    {
                        "titulo": "Picadura de medusa",
                        "query": "Me ha picado una medusa en la playa que me pongo",
                        "keywords_esperadas": ["mar", "tarjeta", "no frotar", "salada"],
                        "keywords_prohibidas": ["agua dulce", "orina", "frotar"]
                    },
                    {
                        "titulo": "Mordedura de serpiente víbora",
                        "query": "Me ha mordido una serpiente en el monte que no debo hacer",
                        "keywords_esperadas": ["no", "calma", "112", "reposo"],
                        "keywords_prohibidas": ["succionar", "cortar", "torniquete"]
                    }
                ]
            },
            "traumatismos_hemorragias": {
                "nombre": "Traumatismos y Hemorragias",
                "casos": [
                    {
                        "titulo": "Corte profundo con sangrado activo",
                        "query": "Tengo un corte profundo en el antebrazo y sangra mucho",
                        "keywords_esperadas": ["presion", "directa", "herida", "limpia"],
                        "keywords_prohibidas": []
                    },
                    {
                        "titulo": "Posible fractura de pierna",
                        "query": "Me he caido y tengo la pierna deformada con mucho dolor",
                        "keywords_esperadas": ["inmovil", "no apoyar", "112"],
                        "keywords_prohibidas": []
                    },
                    {
                        "titulo": "Persona desmayada que respira (PLS)",
                        "query": "Una persona se ha desmayado respira pero no reacciona",
                        "keywords_esperadas": ["lateral", "seguridad", "respira", "112"],
                        "keywords_prohibidas": []
                    }
                ]
            },
            "quemaduras": {
                "nombre": "Quemaduras",
                "casos": [
                    {
                        "titulo": "Quemadura con agua hirviendo",
                        "query": "Me he quemado la mano con agua hirviendo y sale ampolla",
                        "keywords_esperadas": ["agua", "fria", "no romper ampolla", "limpia"],
                        "keywords_prohibidas": ["pasta de dientes", "aceite", "mantequilla"]
                    }
                ]
            }
        }
    },
    "supervivencia": {
        "nombre": "🛡️ Supervivencia y Refugio",
        "tipos": {
            "agua_fuego": {
                "nombre": "Agua y Fuego",
                "casos": [
                    {
                        "titulo": "Obtener agua potable en costa/playa",
                        "query": "Como conseguir y potabilizar agua en la costa sin equipo",
                        "keywords_esperadas": ["no beber agua de mar", "hervir", "destilar", "dulce"],
                        "keywords_prohibidas": ["beber agua de mar directamente"]
                    },
                    {
                        "titulo": "Hacer fuego con chispero en mojado",
                        "query": "Como encender fuego con pedernal si la madera esta humeda",
                        "keywords_esperadas": ["yesca", "corteza", "chispa", "seca"],
                        "keywords_prohibidas": []
                    }
                ]
            },
            "rescate_senales": {
                "nombre": "Señales de Rescate",
                "casos": [
                    {
                        "titulo": "Señales al helicóptero de rescate",
                        "query": "Cuales son las señales con el cuerpo para el helicoptero de rescate",
                        "keywords_esperadas": ["y", "brazo", "v", "despejada"],
                        "keywords_prohibidas": []
                    },
                    {
                        "titulo": "Señales acusticas de socorro",
                        "query": "Cual es la señal internacional de socorro en montaña con silbato",
                        "keywords_esperadas": ["pitido", "silbato", "minuto", "6"],
                        "keywords_prohibidas": []
                    }
                ]
            },
            "orientacion": {
                "nombre": "Orientación Natural",
                "casos": [
                    {
                        "titulo": "Orientarse de noche con estrellas",
                        "query": "Como orientarse de noche buscando el norte con la estrella polar",
                        "keywords_esperadas": ["osa mayor", "norte", "polar", "estrella"],
                        "keywords_prohibidas": []
                    },
                    {
                        "titulo": "Orientarse de día con un palo y sol",
                        "query": "Metodo de la sombra de un palo para encontrar el norte",
                        "keywords_esperadas": ["palo", "sombra", "oeste", "este"],
                        "keywords_prohibidas": []
                    }
                ]
            }
        }
    },
    "geografia": {
        "nombre": "📍 Geografía y Municipios",
        "tipos": {
            "municipios": {
                "nombre": "Poblaciones y Accesos",
                "casos": [
                    {
                        "titulo": "Ubicación de Villaluenga del Rosario",
                        "query": "Donde esta Villaluenga del Rosario y que altitud tiene",
                        "keywords_esperadas": ["villaluenga", "sierra", "858", "cadiz"],
                        "keywords_prohibidas": ["inmovilizar", "hipotermia", "torniquete"]
                    },
                    {
                        "titulo": "Municipio de Grazalema",
                        "query": "Informacion geografica y situacion de Grazalema en Cadiz",
                        "keywords_esperadas": ["grazalema", "sierra", "cadiz"],
                        "keywords_prohibidas": ["inmovilizar", "torniquete"]
                    },
                    {
                        "titulo": "Tarifa y límites",
                        "query": "Donde se encuentra el termino municipal de Tarifa",
                        "keywords_esperadas": ["tarifa", "estrecho", "cadiz"],
                        "keywords_prohibidas": []
                    }
                ]
            },
            "parajes_senderos": {
                "nombre": "Parajes y Montaña",
                "casos": [
                    {
                        "titulo": "Sendero del Pinsapar",
                        "query": "Donde esta el sendero del Pinsapar de Grazalema",
                        "keywords_esperadas": ["pinsapar", "grazalema", "sierra"],
                        "keywords_prohibidas": []
                    },
                    {
                        "titulo": "Playa de Bolonia",
                        "query": "Donde esta la playa de Bolonia y como se accede",
                        "keywords_esperadas": ["bolonia", "tarifa", "playa"],
                        "keywords_prohibidas": []
                    }
                ]
            }
        }
    },
    "transporte": {
        "nombre": "🚆 Transporte Público",
        "tipos": {
            "cercanias": {
                "nombre": "Renfe Cercanías",
                "casos": [
                    {
                        "titulo": "Paradas línea C-1 Cercanías",
                        "query": "Que estaciones recorre la linea C-1 de Cercanias de Cadiz",
                        "keywords_esperadas": ["c-1", "cadiz", "jerez", "bahia sur", "san fernando", "puerto real"],
                        "keywords_prohibidas": ["inmovilizar", "hipotermia", "112"]
                    },
                    {
                        "titulo": "Tren de Jerez a Cádiz",
                        "query": "Hay tren de cercanias entre Jerez de la Frontera y Cadiz",
                        "keywords_esperadas": ["c-1", "jerez", "cadiz", "cercanias"],
                        "keywords_prohibidas": ["inmovilizar", "hipotermia"]
                    }
                ]
            },
            "autobuses": {
                "nombre": "Autobuses Consorcio",
                "casos": [
                    {
                        "titulo": "Línea M-010 Bahía de Cádiz",
                        "query": "Que recorrido hace la linea de autobus M-010 en Cadiz",
                        "keywords_esperadas": ["m-010", "cadiz", "san fernando", "cortadura"],
                        "keywords_prohibidas": ["inmovilizar", "hipotermia", "torniquete"]
                    },
                    {
                        "titulo": "Autobús Cádiz - Puerto Real",
                        "query": "Que lineas de autobus conectan Cadiz con Puerto Real",
                        "keywords_esperadas": ["m-030", "puerto real", "cadiz"],
                        "keywords_prohibidas": ["inmovilizar", "hipotermia"]
                    }
                ]
            },
            "estaciones": {
                "nombre": "Estaciones de Tren",
                "casos": [
                    {
                        "titulo": "Estación de San Fernando Bahía Sur",
                        "query": "Donde esta la estacion de tren de San Fernando Bahia Sur",
                        "keywords_esperadas": ["san fernando", "bahia sur", "estacion"],
                        "keywords_prohibidas": ["inmovilizar", "hipotermia"]
                    },
                    {
                        "titulo": "Estación de Puerto Real",
                        "query": "Donde se ubica la estacion de ferrocarril de Puerto Real",
                        "keywords_esperadas": ["puerto real", "estacion"],
                        "keywords_prohibidas": []
                    }
                ]
            }
        }
    },
    "directorios": {
        "nombre": "📞 Directorios y Cuarteles",
        "tipos": {
            "guardia_civil": {
                "nombre": "Puestos Guardia Civil",
                "casos": [
                    {
                        "titulo": "Puesto Guardia Civil de Chiclana",
                        "query": "Telefono y direccion del puesto de la Guardia Civil de Chiclana",
                        "keywords_esperadas": ["956 40 01 02", "chiclana", "musica", "062"],
                        "keywords_prohibidas": ["inmovilizar", "hipotermia"]
                    },
                    {
                        "titulo": "Puesto Guardia Civil de Chipiona",
                        "query": "Telefono de la Guardia Civil en Chipiona",
                        "keywords_esperadas": ["956 37 02 01", "chipiona", "062"],
                        "keywords_prohibidas": []
                    },
                    {
                        "titulo": "Puesto Guardia Civil de El Bosque",
                        "query": "Telefono del cuartel de la Guardia Civil en El Bosque",
                        "keywords_esperadas": ["956 71 60 03", "el bosque", "062"],
                        "keywords_prohibidas": []
                    }
                ]
            },
            "emergencias_tlf": {
                "nombre": "Teléfonos Únicos",
                "casos": [
                    {
                        "titulo": "Diferencia 112 y 061",
                        "query": "Para que sirve el 112 y cuando llamar al 061",
                        "keywords_esperadas": ["112", "061", "sanitaria", "emergencia"],
                        "keywords_prohibidas": []
                    },
                    {
                        "titulo": "Teléfono 016 violencia",
                        "query": "Cual es el telefono de atencion 016 y como funciona",
                        "keywords_esperadas": ["016", "violencia", "factura", "gratuito"],
                        "keywords_prohibidas": []
                    }
                ]
            }
        }
    },
    "proteccion_civil": {
        "nombre": "🚨 Protección Civil",
        "tipos": {
            "incendios": {
                "nombre": "Incendios Forestales",
                "casos": [
                    {
                        "titulo": "Cercado por fuego en el monte",
                        "query": "Que hacer si un incendio forestal me corta el camino en la sierra",
                        "keywords_esperadas": ["viento", "quemada", "112", "fuego"],
                        "keywords_prohibidas": []
                    }
                ]
            },
            "inundaciones": {
                "nombre": "Inundaciones y Riadas",
                "casos": [
                    {
                        "titulo": "Coche atrapado por riada",
                        "query": "Que hacer si el agua sube y atrapa mi coche en una crecida",
                        "keywords_esperadas": ["techo", "ventanilla", "salir", "112"],
                        "keywords_prohibidas": ["permanecer dentro", "vadear"]
                    }
                ]
            },
            "sismos": {
                "nombre": "Terremotos",
                "casos": [
                    {
                        "titulo": "Conducta durante un terremoto",
                        "query": "Que hacer dentro de una casa durante un terremoto",
                        "keywords_esperadas": ["mueble", "dintel", "mesa", "proteger"],
                        "keywords_prohibidas": ["ascensor", "correr"]
                    }
                ]
            }
        }
    },
    "toxicologia": {
        "nombre": "☣️ Toxicología y Venenos",
        "tipos": {
            "biotoxinas": {
                "nombre": "Biotoxinas Marinas",
                "casos": [
                    {
                        "titulo": "Marea roja y moluscos",
                        "query": "Riesgo de comer coquinas o mejillones recogidos en marea roja",
                        "keywords_esperadas": ["toxina", "paralizante", "marisco", "prohib"],
                        "keywords_prohibidas": ["la coccion elimina la toxina"]
                    }
                ]
            },
            "quimicos": {
                "nombre": "Químicos Domésticos",
                "casos": [
                    {
                        "titulo": "Ingestión de lejía o cáustico",
                        "query": "Un niño ha bebido lejia que debo hacer provocar el vomito",
                        "keywords_esperadas": ["no", "vomito", "112", "toxicologia"],
                        "keywords_prohibidas": ["provocar el vomito", "dar leche", "dar vinagre"]
                    }
                ]
            }
        }
    },
    "apoyo_psicosocial": {
        "nombre": "🧠 Apoyo Psicosocial",
        "tipos": {
            "crisis": {
                "nombre": "Intervención en Crisis",
                "casos": [
                    {
                        "titulo": "Ataque de pánico en catástrofe",
                        "query": "Como tranquilizar a una persona con ataque de panico tras un accidente",
                        "keywords_esperadas": ["calma", "respirar", "acompañar", "seguridad"],
                        "keywords_prohibidas": []
                    },
                    {
                        "titulo": "Cuidado emocional infantil",
                        "query": "Como atender emocionalmente a un niño tras una evacuacion",
                        "keywords_esperadas": ["escuchar", "seguridad", "calma", "afecto"],
                        "keywords_prohibidas": []
                    }
                ]
            }
        }
    },
    "clima": {
        "nombre": "🌦️ Clima y Meteorología",
        "tipos": {
            "calor": {
                "nombre": "Calor Extremo",
                "casos": [
                    {
                        "titulo": "Prevención ola de calor",
                        "query": "Cuales son las medidas principales ante una ola de calor extremo",
                        "keywords_esperadas": ["agua", "sombra", "sol", "fresco"],
                        "keywords_prohibidas": []
                    },
                    {
                        "titulo": "Golpe de calor síntomas",
                        "query": "Sintomas de golpe de calor y que hacer",
                        "keywords_esperadas": ["piel caliente", "sombra", "agua", "112"],
                        "keywords_prohibidas": []
                    }
                ]
            }
        }
    },
    "fauna": {
        "nombre": "🐾 Fauna y Especies",
        "tipos": {
            "procesionaria": {
                "nombre": "Procesionaria del Pino",
                "casos": [
                    {
                        "titulo": "Contacto con procesionaria",
                        "query": "Que hacer si un perro o persona toca orugas de procesionaria",
                        "keywords_esperadas": ["no frotar", "agua", "veterinario", "urticante"],
                        "keywords_prohibidas": []
                    }
                ]
            }
        }
    },
    "anti_alucinacion": {
        "nombre": "❌ Pruebas Fuera de Dominio",
        "tipos": {
            "fuera_dominio": {
                "nombre": "Filtro Fuera de Ámbito",
                "casos": [
                    {
                        "titulo": "Pregunta de geografía mundial",
                        "query": "Cual es la capital de Australia",
                        "keywords_esperadas": [],
                        "keywords_prohibidas": ["llamar al 112", "inmovilizar"]
                    },
                    {
                        "titulo": "Receta de cocina",
                        "query": "Como hacer una tarta de chocolate paso a paso",
                        "keywords_esperadas": [],
                        "keywords_prohibidas": ["llamar al 112", "inmovilizar"]
                    }
                ]
            }
        }
    }
}

# ==============================================================================
# 2. MOTOR DE EVALUACIÓN Y EJECUCIÓN
# ==============================================================================

@dataclass
class ResultadoCaso:
    categoria: str
    subcategoria: str
    titulo: str
    query: str
    ok: bool
    status_code: int
    tiempo_ms: int
    mensajes: list[str]
    max_bytes: int
    categoria_recuperada: str | None
    confianza: float
    fragmentos_rag: int
    fuentes: list[str]
    alertas: list[str] = field(default_factory=list)


def evaluar_caso(
    base_url: str,
    token: str,
    cat_key: str,
    sub_key: str,
    caso: dict[str, Any]
) -> ResultadoCaso:
    titulo = caso["titulo"]
    query = caso["query"]
    esperadas = caso.get("keywords_esperadas", [])
    prohibidas = caso.get("keywords_prohibidas", [])

    endpoint = f"{base_url.rstrip('/')}/v1/consulta"
    payload = json.dumps({
        "consulta": query,
        "id_conversacion": f"batch-{cat_key}-{sub_key}-{int(time.time()*1000)%100000}"
    }).encode("utf-8")

    req = urllib.request.Request(endpoint, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    t0 = time.time()
    alertas: list[str] = []

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            status_code = resp.status
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return ResultadoCaso(
            categoria=cat_key,
            subcategoria=sub_key,
            titulo=titulo,
            query=query,
            ok=False,
            status_code=exc.code,
            tiempo_ms=int((time.time() - t0) * 1000),
            mensajes=[f"HTTP Error: {exc.code} - {exc.reason}"],
            max_bytes=0,
            categoria_recuperada=None,
            confianza=0.0,
            fragmentos_rag=0,
            fuentes=[],
            alertas=[f"Fallo HTTP {exc.code}"]
        )
    except Exception as exc:
        return ResultadoCaso(
            categoria=cat_key,
            subcategoria=sub_key,
            titulo=titulo,
            query=query,
            ok=False,
            status_code=0,
            tiempo_ms=int((time.time() - t0) * 1000),
            mensajes=[f"Error de conexión: {str(exc)}"],
            max_bytes=0,
            categoria_recuperada=None,
            confianza=0.0,
            fragmentos_rag=0,
            fuentes=[],
            alertas=["Error de conexión / Timeout"]
        )

    tiempo_total_ms = int((time.time() - t0) * 1000)
    mensajes = data.get("mensajes", [])
    cat_rec = data.get("categoria")
    confianza = float(data.get("confianza", 0.0))
    frags_count = int(data.get("fragmentos_rag", 0))
    fuentes = [f.get("titulo", "") for f in data.get("fuentes", [])]

    # 1. Comprobación de límites de radio LoRa
    max_bytes = 0
    for idx, msg in enumerate(mensajes):
        b_len = len(msg.encode("utf-8"))
        if b_len > max_bytes:
            max_bytes = b_len
        if b_len > 200:
            alertas.append(f"Paquete [{idx+1}] excede 200 bytes UTF-8 ({b_len} B)")

    if len(mensajes) > 3:
        alertas.append(f"Excede límite de 3 mensajes ({len(mensajes)} msgs)")
    if len(mensajes) == 0:
        alertas.append("Respuesta vacía (0 mensajes)")

    # 2. Comprobación semántica y de categoría RAG
    if cat_key != "anti_alucinacion":
        if frags_count == 0:
            alertas.append("RAG no recuperó ningún fragmento (0 contexto)")
        if cat_rec != cat_key:
            alertas.append(f"Categoría inesperada (Esperada: {cat_key}, Recuperada: {cat_rec})")

    # 3. Comprobación de keywords prohibidas (detección de alucinaciones)
    texto_completo = " ".join(mensajes).lower()
    for kw in prohibidas:
        if kw.lower() in texto_completo:
            alertas.append(f"Alucinación/Contenido prohibido detectado: '{kw}'")

    # 4. Comprobación de keywords esperadas
    coincidencias = sum(1 for kw in esperadas if kw.lower() in texto_completo)
    if esperadas and coincidencias == 0:
        alertas.append(f"No incluye conceptos clave esperados ({', '.join(esperadas[:3])})")

    caso_ok = len(alertas) == 0

    return ResultadoCaso(
        categoria=cat_key,
        subcategoria=sub_key,
        titulo=titulo,
        query=query,
        ok=caso_ok,
        status_code=status_code,
        tiempo_ms=tiempo_total_ms,
        mensajes=mensajes,
        max_bytes=max_bytes,
        categoria_recuperada=cat_rec,
        confianza=confianza,
        fragmentos_rag=frags_count,
        fuentes=fuentes,
        alertas=alertas
    )


def generar_informe_markdown(resultados: list[ResultadoCaso], base_url: str) -> str:
    total = len(resultados)
    exitosos = sum(1 for r in resultados if r.ok)
    fallidos = total - exitosos
    pct = (exitosos / total * 100) if total > 0 else 0.0

    lineas = [
        f"# Informe de Evaluación Masiva por Lotes — Banco de Pruebas RAG",
        f"",
        f"- **Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Servidor evaluado:** `{base_url}`",
        f"- **Total de pruebas ejecutadas:** `{total}` combinaciones",
        f"- **Pruebas superadas sin alertas:** `{exitosos}` ({pct:.1f}%)",
        f"- **Pruebas con incidencias / alertas:** `{fallidos}`",
        f"",
        f"---",
        f"",
        f"## 📊 Resumen por Categoría",
        f"",
        f"| Categoría | Casos | Superados | Fallidos | Tasa Éxito |",
        f"| :--- | :---: | :---: | :---: | :---: |"
    ]

    por_cat: dict[str, list[ResultadoCaso]] = {}
    for r in resultados:
        por_cat.setdefault(r.categoria, []).append(r)

    for cat, casos in por_cat.items():
        c_tot = len(casos)
        c_ok = sum(1 for c in casos if c.ok)
        c_fail = c_tot - c_ok
        c_pct = (c_ok / c_tot * 100) if c_tot > 0 else 0.0
        lineas.append(f"| `{cat}` | {c_tot} | {c_ok} | {c_fail} | **{c_pct:.1f}%** |")

    lineas.extend([
        f"",
        f"---",
        f"",
        f"## 📝 Detalle de Cada Caso de Prueba",
        f""
    ])

    for idx, r in enumerate(resultados, 1):
        icono = "✅" if r.ok else "❌"
        lineas.append(f"### {idx}. {icono} [{r.categoria} / {r.subcategoria}] {r.titulo}")
        lineas.append(f"- **Consulta:** *\"{r.query}\"*")
        lineas.append(f"- **RAG:** Cat: `{r.categoria_recuperada}` | Conf: `{r.confianza:.3f}` | Fragmentos: `{r.fragmentos_rag}` | Fuentes: `{', '.join(r.fuentes[:2]) or 'Ninguna'}`")
        lineas.append(f"- **Métricas:** Latencia: `{r.tiempo_ms} ms` | Máx Bytes: `{r.max_bytes}/200 B` | Paquetes: `{len(r.mensajes)}`")
        
        if r.alertas:
            lineas.append(f"- ⚠️ **Alertas detectadas:**")
            for a in r.alertas:
                lineas.append(f"  - 🔴 {a}")

        lineas.append(f"- **Mensajes generados:**")
        for m_idx, m in enumerate(r.mensajes, 1):
            b = len(m.encode("utf-8"))
            lineas.append(f"  > **[{m_idx}] ({b} bytes UTF-8):** {m}")
        lineas.append("")

    return "\n".join(lineas)


def main() -> int:
    parser = argparse.ArgumentParser(description="Ejecutor de pruebas por lotes del Bot de Emergencias")
    parser.add_argument("--url", default=os.environ.get("API_BASE_URL", "http://172.18.1.121:8870"), help="URL base de la API")
    parser.add_argument("--token", default=os.environ.get("API_AUTH_TOKEN", "4d7a1d7affbeb459814d1fa220b2a70b"), help="Token Bearer de autenticación")
    parser.add_argument("--output", default="eval_report_banco.md", help="Archivo de salida para el informe Markdown")
    parser.add_argument("--json", default="", help="Ruta opcional para volcar resultados en JSON")
    args = parser.parse_args()

    print("=" * 80)
    print("🚀 EJECUTOR MASIVO DEL BANCO DE PRUEBAS COMPLETO (INTRANET / RAG)")
    print(f"🎯 Servidor objetivo: {args.url}")
    print(f"🔑 Token Bearer: {args.token[:6]}...{args.token[-4:] if len(args.token)>10 else ''}")
    print("=" * 80)
    print()

    # Contar casos totales
    total_casos = sum(len(sub["casos"]) for cat in BANCO_PRUEBAS.values() for sub in cat["tipos"].values())
    print(f"📦 Total de casos a evaluar: {total_casos}")
    print("⏳ Iniciando inferencias con Qwen 2.5 local... (puede tardar unos minutos)\n")

    resultados: list[ResultadoCaso] = []
    contador = 0

    for cat_key, cat_data in BANCO_PRUEBAS.items():
        print(f"--- Categoría: {cat_data['nombre']} ({cat_key}) ---")
        for sub_key, sub_data in cat_data["tipos"].items():
            for caso in sub_data["casos"]:
                contador += 1
                sys.stdout.write(f"  [{contador:02d}/{total_casos:02d}] {caso['titulo']:<40} ... ")
                sys.stdout.flush()

                res = evaluar_caso(args.url, args.token, cat_key, sub_key, caso)
                resultados.append(res)

                if res.ok:
                    print(f"✅ OK ({res.tiempo_ms/1000:.1f}s | {res.max_bytes}B | Conf: {res.confianza:.2f})")
                else:
                    alertas_str = "; ".join(res.alertas)
                    print(f"❌ FALLO ({res.tiempo_ms/1000:.1f}s) -> {alertas_str}")

        print()

    # Generar informe
    informe_md = generar_informe_markdown(resultados, args.url)
    out_path = Path(args.output)
    out_path.write_text(informe_md, encoding="utf-8")
    print("=" * 80)
    print(f"📄 Informe detallado generado en: {out_path.resolve()}")

    if args.json:
        json_path = Path(args.json)
        json_data = [r.__dict__ for r in resultados]
        json_path.write_text(json.dumps(json_data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"📊 Datos en bruto guardados en: {json_path.resolve()}")

    exitosos = sum(1 for r in resultados if r.ok)
    print(f"🏁 RESULTADO FINAL: {exitosos}/{total_casos} casos superados con éxito ({exitosos/total_casos*100:.1f}%)")
    print("=" * 80)

    return 0 if exitosos == total_casos else 1


if __name__ == "__main__":
    sys.exit(main())
