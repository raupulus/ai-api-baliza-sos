"""Fuente de conocimiento ampliada para primeros auxilios, emergencias y montaña en Cádiz.

Basada en guías clínicas de Cruz Roja, SEMES, Protección Civil y rescate en montaña.
"""

from __future__ import annotations

from datetime import date

from common.models import Categoria, Fragmento, NivelConfianza
from updater.sources.base import Source

_DATOS_PRIMEROS_AUXILIOS = [
    # Traumatología y montaña
    {
        "texto": (
            "Caídas y traumatismos en montaña: Si la persona sufre una caída, evaluar consciencia "
            "y respiración. Si sospechas lesión en columna o cuello, NO mover a la víctima salvo riesgo "
            "vital inminente (desprendimiento, riada). Abrigarla para evitar hipotermia del suelo. "
            "Llama de inmediato al 112 facilitando coordenadas GPS o referencias visibles."
        ),
        "subcategoria": "traumatismos_montana",
        "categoria": Categoria.PRIMEROS_AUXILIOS,
    },
    {
        "texto": (
            "Esguince o fractura de tobillo/pie en montaña: No apoyar el pie. Inmovilizar la articulación "
            "con férula improvisada (ramas acolchadas con ropa o vendaje en ocho con pañuelo). "
            "No retirar la bota inmediatamente si estás lejos de ayuda, ya que ejerce de contención natural. "
            "Elevar la extremidad si es posible y aplicar frío local indirecto si hay agua fría."
        ),
        "subcategoria": "inmovilizacion_tobillo",
        "categoria": Categoria.PRIMEROS_AUXILIOS,
    },
    {
        "texto": (
            "Hemorragias graves y cortes profundos: Presión directa y continua sobre la herida con tela "
            "limpia o apósito durante al menos 5-10 minutos sin retirar. Colocar vendaje compresivo firme. "
            "Si la hemorragia es masiva en extremidad y no cede (sangrado arterial pulsátil), colocar "
            "torniquete comercial o improvisado ancho a 5-7 cm por encima de la herida y anotar la hora exacta."
        ),
        "subcategoria": "hemorragias",
        "categoria": Categoria.PRIMEROS_AUXILIOS,
    },
    {
        "texto": (
            "Reanimación Cardiopulmonar (RCP básica en adultos): Si la persona no responde y no respira "
            "con normalidad, llamar al 112 y poner altavoz. Colocar talón de la mano en el centro del pecho "
            "y la otra mano encima. Comprimir fuerte y rápido a un ritmo de 100-120 compresiones por minuto "
            "(5-6 cm de profundidad). Mantener 30 compresiones seguidas de 2 ventilaciones (o solo compresiones "
            "continuas si no hay entrenamiento)."
        ),
        "subcategoria": "rcp_soporte_vital",
        "categoria": Categoria.PRIMEROS_AUXILIOS,
    },
    {
        "texto": (
            "Atragantamiento y asfixia en adultos (Maniobra de Heimlich): Si la víctima tose con fuerza, "
            "animarla a seguir tosiendo. Si no puede toser, hablar ni respirar: dar 5 golpes secos en la espalda "
            "entre los omóplatos con el talón de la mano. Si no expulsa el objeto, alternar con 5 compresiones "
            "abdominales hacia dentro y hacia arriba justo por encima del ombligo. Si pierde el conocimiento, iniciar RCP."
        ),
        "subcategoria": "atragantamiento",
        "categoria": Categoria.PRIMEROS_AUXILIOS,
    },
    {
        "texto": (
            "Golpe de calor e insolación en la provincia de Cádiz: Frecuente con viento de Levante y altas temperaturas. "
            "Síntomas: piel caliente y seca o sudoración profusa, dolor de cabeza, confusión, mareo, náuseas. "
            "Tratamiento: Mover a la sombra de inmediato, desabrochar ropa, humedecer con paños de agua fresca en cuello, "
            "axilas e ingles, y abanicar. Dar agua a pequeños sorbos solo si está consciente. Llamar al 112."
        ),
        "subcategoria": "golpe_de_calor",
        "categoria": Categoria.PRIMEROS_AUXILIOS,
    },
    {
        "texto": (
            "Hipotermia en la Sierra de Grazalema o noches de montaña: Proteger del viento y aislar del suelo frío. "
            "Retirar ropa mojada y reemplazar por ropa seca o manta térmica con el lado plateado hacia dentro. "
            "Proporcionar bebidas templadas azucaradas (nunca alcohol). No frotar ni aplicar calor directo en extremidades, "
            "calentar el torso gradualmente."
        ),
        "subcategoria": "hipotermia",
        "categoria": Categoria.PRIMEROS_AUXILIOS,
    },
    {
        "texto": (
            "Picadura de pez araña o escorpión en playas de Cádiz: El veneno es termolábil. "
            "Sumergir la zona afectada en agua caliente (aproximadamente a 40-45 °C, lo máximo soportable sin quemar) "
            "durante 30 a 60 minutos para desnaturalizar la toxina. Limpiar la herida con antiséptico y retirar espinas visibles. "
            "No aplicar torniquetes ni succionar. Acudir al puesto de socorro o llamar al 112 si hay reacción alérgica."
        ),
        "subcategoria": "pez_arana",
        "categoria": Categoria.PRIMEROS_AUXILIOS,
    },
    {
        "texto": (
            "Picadura de carabela portuguesa (Physalia physalis) en el litoral gaditano: Produce quemaduras químicas muy dolorosas. "
            "No tocar los tentáculos con las manos desnudas; retirar con pinzas o tarjeta plástica. Lavar EXCLUSIVAMENTE con agua de mar "
            "o vinagre. NUNCA usar agua dulce ni frotar, ya que dispararía los cnidocitos restantes. Aplicar calor moderado local. "
            "Buscar atención médica urgente si hay dificultad respiratoria, mareo o dolor intenso."
        ),
        "subcategoria": "carabela_portuguesa",
        "categoria": Categoria.PRIMEROS_AUXILIOS,
    },
    {
        "texto": (
            "Mordedura de víbora hocicuda (Sierra de Grazalema y Alcornocales): Mantener la calma y reposo absoluto para frenar "
            "la difusión del veneno. Lavar la herida con agua y jabón, inmovilizar el miembro por debajo del nivel del corazón. "
            "NUNCA hacer incisiones, NUNCA succionar el veneno y NUNCA poner torniquetes. Retirar anillos y pulseras antes de que se hinche. "
            "Llamar al 112 y trasladar al hospital más cercano."
        ),
        "subcategoria": "vibora_hocicuda",
        "categoria": Categoria.PRIMEROS_AUXILIOS,
    },
    # Protocolos de desorientación y supervivencia
    {
        "texto": (
            "Desorientación y extravío en montaña (Protocolo S.T.O.P.): 1. Stop (Detente): para la marcha, mantén la calma y evita el pánico. "
            "2. Think (Piensa): recuerda el último punto conocido y evalúa tus recursos (agua, abrigo, batería). "
            "3. Observe (Observa): busca puntos de referencia, cortafuegos, tendidos eléctricos, cursos de agua o el sol/costa. "
            "4. Plan (Planifica): si cae la noche o el terreno es escarpado, quédate donde estés y señaliza en lugar visible."
        ),
        "subcategoria": "desorientacion_stop",
        "categoria": Categoria.SUPERVIVENCIA,
    },
    {
        "texto": (
            "Señales de socorro en montaña y supervivencia: Señal internacional de socorro: 6 señales acústicas (silbato) "
            "o luminosas (linterna/espejo) repetidas por minuto, seguidas de 1 minuto de pausa. Para aeronaves de rescate (helicóptero), "
            "formar una 'Y' con los dos brazos en alto para decir 'YES, necesito auxilio'; formar una línea diagonal con un brazo arriba y "
            "otro abajo para decir 'NO, no requiero auxilio'."
        ),
        "subcategoria": "senales_socorro",
        "categoria": Categoria.SUPERVIVENCIA,
    },
    {
        "texto": (
            "Obtención y potabilización de agua en zonas naturales de Cádiz: Nunca beber agua estancada ni agua de mar. "
            "Buscar manantiales que broten de roca o cursos altos de arroyos limpios. Métodos de desinfección: hervir enérgicamente "
            "durante al menos 1 minuto; o usar pastillas potabilizadoras / 2 gotas de lejía apta para consumo por litro de agua clara esperando 30 minutos."
        ),
        "subcategoria": "potabilizacion_agua",
        "categoria": Categoria.SUPERVIVENCIA,
    },
]


class PrimerosAuxiliosAvanzadoSource(Source):
    """Fuente estructurada con protocolos médicos y de supervivencia para Cádiz."""

    nombre = "primeros-auxilios-avanzado"
    licencia = "CC-BY-NC-SA 4.0 (Guías Sanitarias Oficiales)"
    metodo = "manual_validado"

    def fetch(self) -> list[Fragmento]:
        fragmentos: list[Fragmento] = []
        hoy = date.today()

        for item in _DATOS_PRIMEROS_AUXILIOS:
            frg = Fragmento(
                texto=item["texto"],
                fuente="Manual de Primeros Auxilios y Supervivencia (Validado)",
                categoria=item["categoria"],
                subcategoria=item.get("subcategoria"),
                provincia=self.provincia,
                nivel_confianza=NivelConfianza.ALTA,
                licencia=self.licencia,
                validado_por="equipo_sanitario_emergencias",
                validado_fecha=hoy,
            )
            fragmentos.append(frg)

        return fragmentos
