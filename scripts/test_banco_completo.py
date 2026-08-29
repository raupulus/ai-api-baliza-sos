#!/usr/bin/env python3
"""Suite de ejecución y validación masiva por lotes del Banco de Pruebas RAG.

Evalúa la operatividad del asistente offline como ÚLTIMO RECURSO (sin cobertura):
1. Precisión de recuperación del RAG y categorías relevantes.
2. Cumplimiento de límites de radio LoRa (<= 200 bytes UTF-8 por paquete, máx. 3 mensajes).
3. Calidad de respuesta:
   - Instrucciones prácticas directas (qué hacer con las manos / entorno en el momento).
   - NUNCA pedir llamar al 112 o esperar auxilio telefónico en emergencias (usuario sin cobertura).
   - Dar teléfonos ÚNICAMENTE si el usuario pregunta explícitamente por un directorio/número.
   - Respuestas neutras ante preguntas fuera de ámbito (recetas, geografía mundial).
4. Genera informe detallado en Markdown y JSON.
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
# 1. CATÁLOGO COMPLETO DEL BANCO DE PRUEBAS
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
                        "categorias_validas": ["primeros_auxilios"],
                        "keywords_esperadas": ["compresion", "pecho", "30", "100", "120"],
                        "keywords_prohibidas": ["llama al 112", "llamar al 112", "hipotermia", "bota"]
                    },
                    {
                        "titulo": "Uso de Desfibrilador (DEA)",
                        "query": "Como usar un desfibrilador DEA en un adulto",
                        "categorias_validas": ["primeros_auxilios"],
                        "keywords_esperadas": ["dea", "pecho", "parche", "descarga", "instruccion", "shock", "dispositivo", "compresion"],
                        "keywords_prohibidas": ["llama al 112", "llamar al 112"]
                    },
                    {
                        "titulo": "Soporte vital básico pediátrico",
                        "query": "Un niño no respira como hacer RCP pediatrico",
                        "categorias_validas": ["primeros_auxilios"],
                        "keywords_esperadas": ["compresion", "pecho", "ventilacion", "mano"],
                        "keywords_prohibidas": ["llama al 112", "llamar al 112"]
                    }
                ]
            },
            "atragantamiento": {
                "nombre": "Atragantamiento (OVACE)",
                "casos": [
                    {
                        "titulo": "Atragantamiento severo adulto (Heimlich)",
                        "query": "Un adulto se esta atragantando y no puede hablar ni toser",
                        "categorias_validas": ["primeros_auxilios"],
                        "keywords_esperadas": ["golpe", "espalda", "ombligo", "compresion", "heimlich"],
                        "keywords_prohibidas": ["llama al 112", "llamar al 112"]
                    },
                    {
                        "titulo": "Atragantamiento en lactante/bebé",
                        "query": "Un bebe se ha atragantado con un objeto que hago",
                        "categorias_validas": ["primeros_auxilios"],
                        "keywords_esperadas": ["antebrazo", "boca abajo", "espalda", "dedo", "compresion"],
                        "keywords_prohibidas": ["llama al 112", "llamar al 112"]
                    }
                ]
            },
            "picaduras_mordeduras": {
                "nombre": "Picaduras y Mordeduras",
                "casos": [
                    {
                        "titulo": "Picadura de pez araña en la playa",
                        "query": "He pisado un pez araña en la orilla del mar me arde el pie",
                        "categorias_validas": ["fauna", "primeros_auxilios"],
                        "keywords_esperadas": ["caliente", "agua", "40", "45", "termolabil"],
                        "keywords_prohibidas": ["torniquete", "hielo", "llama al 112", "llamar al 112"]
                    },
                    {
                        "titulo": "Picadura de medusa",
                        "query": "Me ha picado una medusa en la playa que me pongo",
                        "categorias_validas": ["fauna", "primeros_auxilios"],
                        "keywords_esperadas": ["mar", "salada", "tarjeta", "no frotar"],
                        "keywords_prohibidas": ["aplica agua dulce", "lava con agua dulce", "orina", "llama al 112"]
                    },
                    {
                        "titulo": "Mordedura de serpiente víbora",
                        "query": "Me ha mordido una serpiente en el monte que no debo hacer",
                        "categorias_validas": ["fauna", "primeros_auxilios"],
                        "keywords_esperadas": ["reposo", "calma", "inmovil", "no"],
                        "keywords_prohibidas": ["succionar", "cortar", "torniquete", "llama al 112"]
                    }
                ]
            },
            "traumatismos_hemorragias": {
                "nombre": "Traumatismos y Hemorragias",
                "casos": [
                    {
                        "titulo": "Corte profundo con sangrado activo",
                        "query": "Tengo un corte profundo en el antebrazo y sangra mucho",
                        "categorias_validas": ["primeros_auxilios"],
                        "keywords_esperadas": ["presion", "directa", "herida", "tela", "gasa", "compresiv"],
                        "keywords_prohibidas": ["llama al 112", "llamar al 112"]
                    },
                    {
                        "titulo": "Posible fractura de pierna",
                        "query": "Me he caido y tengo la pierna deformada con mucho dolor",
                        "categorias_validas": ["primeros_auxilios"],
                        "keywords_esperadas": ["inmovil", "no mover", "apoyar", "posicion"],
                        "keywords_prohibidas": ["llama al 112", "llamar al 112"]
                    },
                    {
                        "titulo": "Persona desmayada que respira (PLS)",
                        "query": "Una persona se ha desmayado respira pero no reacciona",
                        "categorias_validas": ["primeros_auxilios"],
                        "keywords_esperadas": ["lateral", "seguridad", "posicion", "respira", "lado", "compresion"],
                        "keywords_prohibidas": ["llama al 112", "llamar al 112"]
                    }
                ]
            },
            "quemaduras": {
                "nombre": "Quemaduras",
                "casos": [
                    {
                        "titulo": "Quemadura con agua hirviendo",
                        "query": "Me he quemado la mano con agua hirviendo y sale ampolla",
                        "categorias_validas": ["primeros_auxilios"],
                        "keywords_esperadas": ["agua", "fria", "ampolla", "limpia"],
                        "keywords_prohibidas": ["pasta de dientes", "aceite", "mantequilla", "llama al 112"]
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
                        "categorias_validas": ["supervivencia"],
                        "keywords_esperadas": ["no beber agua de mar", "hervir", "destilar", "arroyo", "manantial"],
                        "keywords_prohibidas": ["beber agua de mar directamente", "llama al 112"]
                    },
                    {
                        "titulo": "Hacer fuego con chispero en mojado",
                        "query": "Como encender fuego con pedernal si la madera esta humeda",
                        "categorias_validas": ["supervivencia", "primeros_auxilios", "proteccion_civil"],
                        "keywords_esperadas": ["yesca", "corteza", "chispa", "seca", "pedernal", "fuego", "calor", "humed"],
                        "keywords_prohibidas": ["llama al 112"]
                    }
                ]
            },
            "rescate_senales": {
                "nombre": "Señales de Rescate",
                "casos": [
                    {
                        "titulo": "Señales al helicóptero de rescate",
                        "query": "Cuales son las señales con el cuerpo para el helicoptero de rescate",
                        "categorias_validas": ["supervivencia"],
                        "keywords_esperadas": ["y", "brazo", "v", "despejad"],
                        "keywords_prohibidas": ["llama al 112"]
                    },
                    {
                        "titulo": "Señales acusticas de socorro",
                        "query": "Cual es la señal internacional de socorro en montaña con silbato",
                        "categorias_validas": ["supervivencia", "orientacion", "geografia"],
                        "keywords_esperadas": ["6", "3", "pitido", "minuto", "silbato", "largo", "socorro"],
                        "keywords_prohibidas": ["llama al 112"]
                    }
                ]
            },
            "orientacion": {
                "nombre": "Orientación Natural",
                "casos": [
                    {
                        "titulo": "Orientarse de noche con estrellas",
                        "query": "Como orientarse de noche buscando el norte con la estrella polar",
                        "categorias_validas": ["supervivencia", "orientacion"],
                        "keywords_esperadas": ["osa mayor", "polar", "norte", "estrella"],
                        "keywords_prohibidas": ["llama al 112"]
                    },
                    {
                        "titulo": "Orientarse de día con un palo y sol",
                        "query": "Metodo de la sombra de un palo para encontrar el norte",
                        "categorias_validas": ["supervivencia", "orientacion", "geografia"],
                        "keywords_esperadas": ["palo", "sombra", "oeste", "este", "norte"],
                        "keywords_prohibidas": ["llama al 112"]
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
                        "categorias_validas": ["geografia"],
                        "keywords_esperadas": ["villaluenga", "cadiz", "puercas", "sierra", "858", "provincia"],
                        "keywords_prohibidas": ["inmovil", "hipotermia", "llama al 112", "auxilio"]
                    },
                    {
                        "titulo": "Municipio de Grazalema",
                        "query": "Informacion geografica y situacion de Grazalema en Cadiz",
                        "categorias_validas": ["geografia"],
                        "keywords_esperadas": ["grazalema", "sierra", "cadiz"],
                        "keywords_prohibidas": ["inmovil", "llama al 112", "auxilio"]
                    },
                    {
                        "titulo": "Tarifa y límites",
                        "query": "Donde se encuentra el termino municipal de Tarifa",
                        "categorias_validas": ["geografia", "directorios"],
                        "keywords_esperadas": ["tarifa", "estrecho", "cadiz"],
                        "keywords_prohibidas": ["llama al 112", "auxilio"]
                    }
                ]
            },
            "parajes_senderos": {
                "nombre": "Parajes y Montaña",
                "casos": [
                    {
                        "titulo": "Sendero del Pinsapar",
                        "query": "Donde esta el sendero del Pinsapar de Grazalema",
                        "categorias_validas": ["geografia"],
                        "keywords_esperadas": ["pinsapar", "grazalema", "benamahoma", "canteras"],
                        "keywords_prohibidas": ["llama al 112", "auxilio"]
                    },
                    {
                        "titulo": "Playa de Bolonia",
                        "query": "Donde esta la playa de Bolonia y como se accede",
                        "categorias_validas": ["geografia"],
                        "keywords_esperadas": ["bolonia", "tarifa", "playa"],
                        "keywords_prohibidas": ["llama al 112", "auxilio"]
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
                        "categorias_validas": ["transporte"],
                        "keywords_esperadas": ["c-1", "cadiz", "jerez", "bahia sur", "san fernando", "puerto real"],
                        "keywords_prohibidas": ["inmovil", "hipotermia", "llama al 112", "auxilio"]
                    },
                    {
                        "titulo": "Tren de Jerez a Cádiz",
                        "query": "Hay tren de cercanias entre Jerez de la Frontera y Cadiz",
                        "categorias_validas": ["transporte"],
                        "keywords_esperadas": ["c-1", "jerez", "cadiz", "cercanias"],
                        "keywords_prohibidas": ["inmovil", "hipotermia", "llama al 112", "auxilio"]
                    }
                ]
            },
            "autobuses": {
                "nombre": "Autobuses Consorcio",
                "casos": [
                    {
                        "titulo": "Línea M-010 Bahía de Cádiz",
                        "query": "Que recorrido hace la linea de autobus M-010 en Cadiz",
                        "categorias_validas": ["transporte"],
                        "keywords_esperadas": ["m-010", "cadiz", "san fernando", "cortadura"],
                        "keywords_prohibidas": ["inmovil", "hipotermia", "llama al 112", "auxilio"]
                    },
                    {
                        "titulo": "Autobús Cádiz - Puerto Real",
                        "query": "Que lineas de autobus conectan Cadiz con Puerto Real",
                        "categorias_validas": ["transporte"],
                        "keywords_esperadas": ["m-030", "puerto real", "cadiz"],
                        "keywords_prohibidas": ["inmovil", "hipotermia", "llama al 112", "auxilio"]
                    }
                ]
            },
            "estaciones": {
                "nombre": "Estaciones de Tren",
                "casos": [
                    {
                        "titulo": "Estación de San Fernando Bahía Sur",
                        "query": "Donde esta la estacion de tren de San Fernando Bahia Sur",
                        "categorias_validas": ["transporte"],
                        "keywords_esperadas": ["san fernando", "bahia sur", "estacion", "36.", "36.468"],
                        "keywords_prohibidas": ["inmovil", "hipotermia", "llama al 112", "auxilio"]
                    },
                    {
                        "titulo": "Estación de Puerto Real",
                        "query": "Donde se ubica la estacion de ferrocarril de Puerto Real",
                        "categorias_validas": ["transporte"],
                        "keywords_esperadas": ["puerto real", "estacion", "36.", "37."],
                        "keywords_prohibidas": ["inmovil", "llama al 112", "auxilio"]
                    }
                ]
            }
        }
    },
    "directorios": {
        "nombre": "📞 Directorios y Cuarteles (Solicitud explícita de teléfono)",
        "tipos": {
            "guardia_civil": {
                "nombre": "Puestos Guardia Civil",
                "casos": [
                    {
                        "titulo": "Puesto Guardia Civil de Chiclana",
                        "query": "Telefono y direccion del puesto de la Guardia Civil de Chiclana",
                        "categorias_validas": ["directorios"],
                        "keywords_esperadas": ["956 40 01 02", "chiclana", "musica"],
                        "keywords_prohibidas": ["inmovil", "hipotermia"]
                    },
                    {
                        "titulo": "Puesto Guardia Civil de Chipiona",
                        "query": "Telefono de la Guardia Civil en Chipiona",
                        "categorias_validas": ["directorios"],
                        "keywords_esperadas": ["956 37 02 01", "chipiona"],
                        "keywords_prohibidas": ["inmovil"]
                    },
                    {
                        "titulo": "Puesto Guardia Civil de El Bosque",
                        "query": "Telefono del cuartel de la Guardia Civil en El Bosque",
                        "categorias_validas": ["directorios"],
                        "keywords_esperadas": ["956 71 60 03", "el bosque"],
                        "keywords_prohibidas": ["inmovil"]
                    }
                ]
            },
            "emergencias_tlf": {
                "nombre": "Teléfonos Únicos",
                "casos": [
                    {
                        "titulo": "Diferencia 112 y 061",
                        "query": "Para que sirve el 112 y cuando llamar al 061",
                        "categorias_validas": ["directorios", "supervivencia"],
                        "keywords_esperadas": ["112", "061", "sanitaria", "emergencia"],
                        "keywords_prohibidas": []
                    },
                    {
                        "titulo": "Teléfono 016 violencia",
                        "query": "Cual es el telefono de atencion 016 y como funciona",
                        "categorias_validas": ["directorios"],
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
                        "categorias_validas": ["proteccion_civil", "primeros_auxilios"],
                        "keywords_esperadas": ["viento", "quemada", "fuego", "flamas", "alej"],
                        "keywords_prohibidas": ["llama al 112", "llamar al 112"]
                    }
                ]
            },
            "inundaciones": {
                "nombre": "Inundaciones y Riadas",
                "casos": [
                    {
                        "titulo": "Coche atrapado por riada",
                        "query": "Que hacer si el agua sube y atrapa mi coche en una crecida",
                        "categorias_validas": ["proteccion_civil", "supervivencia"],
                        "keywords_esperadas": ["techo", "ventanilla", "salir", "vehiculo"],
                        "keywords_prohibidas": ["permanecer dentro", "vadear", "llama al 112", "llamar al 112"]
                    }
                ]
            },
            "sismos": {
                "nombre": "Terremotos",
                "casos": [
                    {
                        "titulo": "Conducta durante un terremoto",
                        "query": "Que hacer dentro de una casa durante un terremoto",
                        "categorias_validas": ["proteccion_civil", "primeros_auxilios"],
                        "keywords_esperadas": ["mueble", "dintel", "mesa", "proteger", "puerta"],
                        "keywords_prohibidas": ["usa el ascensor", "usar el ascensor", "llama al 112", "llamar al 112"]
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
                        "categorias_validas": ["toxicologia", "fauna"],
                        "keywords_esperadas": ["toxina", "paralizante", "marisco", "prohib", "molusco", "marea roja"],
                        "keywords_prohibidas": ["la coccion elimina la toxina", "llama al 112", "llamar al 112"]
                    }
                ]
            },
            "quimicos": {
                "nombre": "Químicos Domésticos",
                "casos": [
                    {
                        "titulo": "Ingestión de lejía o cáustico",
                        "query": "Un niño ha bebido lejia que debo hacer provocar el vomito",
                        "categorias_validas": ["toxicologia", "primeros_auxilios"],
                        "keywords_esperadas": ["vomito", "envase", "calma", "esofago", "lejia", "quimic", "beber"],
                        "keywords_prohibidas": ["provocar el vomito", "dar leche", "dar vinagre", "llama al 112", "llamar al 112"]
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
                        "categorias_validas": ["apoyo_psicosocial", "primeros_auxilios"],
                        "keywords_esperadas": ["calma", "respirar", "4", "sentidos", "anclaje", "acompañar"],
                        "keywords_prohibidas": ["llama al 112", "llamar al 112"]
                    },
                    {
                        "titulo": "Cuidado emocional infantil",
                        "query": "Como atender emocionalmente a un niño tras una evacuacion",
                        "categorias_validas": ["apoyo_psicosocial"],
                        "keywords_esperadas": ["afecto", "seguridad", "calma", "rutina", "escuchar"],
                        "keywords_prohibidas": ["llama al 112", "llamar al 112"]
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
                        "categorias_validas": ["clima", "primeros_auxilios"],
                        "keywords_esperadas": ["agua", "sombra", "sol", "fresco", "calor"],
                        "keywords_prohibidas": ["llama al 112", "llamar al 112"]
                    },
                    {
                        "titulo": "Golpe de calor síntomas",
                        "query": "Sintomas de golpe de calor y que hacer",
                        "categorias_validas": ["clima", "primeros_auxilios"],
                        "keywords_esperadas": ["piel caliente", "sombra", "fresco", "paño", "agua"],
                        "keywords_prohibidas": ["llama al 112", "llamar al 112"]
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
                        "categorias_validas": ["fauna", "transporte"],
                        "keywords_esperadas": ["no frotar", "agua", "veterinario", "urticante", "lavar"],
                        "keywords_prohibidas": ["llama al 112", "llamar al 112"]
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
                        "categorias_validas": [None, "general"],
                        "keywords_esperadas": ["fuera del ambito", "emergencias"],
                        "keywords_prohibidas": ["llama al 112", "inmovilizar", "canberra", "sydney"]
                    },
                    {
                        "titulo": "Receta de cocina",
                        "query": "Como hacer una tarta de chocolate paso a paso",
                        "categorias_validas": [None, "general"],
                        "keywords_esperadas": ["fuera del ambito", "emergencias"],
                        "keywords_prohibidas": ["llama al 112", "inmovilizar", "harina", "horno"]
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
    valid_cats = caso.get("categorias_validas", [cat_key])
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

    # 2. Comprobación de categoría RAG
    if cat_key != "anti_alucinacion":
        if frags_count == 0:
            alertas.append("RAG no recuperó ningún fragmento (0 contexto)")
        if cat_rec not in valid_cats:
            alertas.append(f"Categoría recuperada no válida ({cat_rec} not in {valid_cats})")

    # 3. Comprobación de keywords prohibidas (detección de 'llama al 112', alucinaciones, etc.)
    texto_completo = " ".join(mensajes).lower()
    for kw in prohibidas:
        if kw.lower() in texto_completo:
            alertas.append(f"Prohibido detectado (inútil sin cobertura): '{kw}'")

    # 4. Comprobación de keywords esperadas
    coincidencias = sum(1 for kw in esperadas if kw.lower() in texto_completo)
    if esperadas and coincidencias == 0:
        alertas.append(f"No incluye conceptos prácticos esperados ({', '.join(esperadas[:3])})")

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
        f"# Informe de Evaluación Masiva — Asistente Offline (Último Recurso)",
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
    parser.add_argument("--output", default="data/logs/eval_report_banco.md", help="Archivo de salida para el informe Markdown")
    parser.add_argument("--json", default="", help="Ruta opcional para volcar resultados en JSON")
    args = parser.parse_args()

    print("=" * 80)
    print("🚀 EJECUTOR MASIVO DEL BANCO DE PRUEBAS — ASISTENTE OFFLINE ÚLTIMO RECURSO")
    print(f"🎯 Servidor objetivo: {args.url}")
    print("=" * 80)
    print()

    total_casos = sum(len(sub["casos"]) for cat in BANCO_PRUEBAS.values() for sub in cat["tipos"].values())
    print(f"📦 Total de casos a evaluar: {total_casos}")
    print("⏳ Iniciando inferencias... (validando que las respuestas sean prácticas y sin 'llama al 112')\n")

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

    informe_md = generar_informe_markdown(resultados, args.url)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
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
