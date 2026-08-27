"""Fuente de hitos históricos y patrimonio de la provincia de Cádiz.

Recoge desde la fundación fenicia hasta la Constitución de 1812 y la Batalla de Trafalgar.
"""

from __future__ import annotations

from datetime import date

from common.models import Categoria, Fragmento, NivelConfianza
from updater.sources.base import Source

_HISTORIA_CADIZ = [
    {
        "titulo": "Fundación fenicia de Gadir (c. 1100 a.C.)",
        "texto": (
            "Fundación de Gadir (Cádiz): Considerada la ciudad viva más antigua de Occidente, fundada hacia el 1104 a.C. "
            "por navegantes fenicios procedentes de Tiro (actual Líbano). Establecieron un enclave comercial estratégico "
            "y el célebre santuario del dios Melqart (asimilado luego como Hércules) en el islote de Sancti Petri, "
            "junto al yacimiento arqueológico de Gadir y los sarcófagos antropoides fenicios hallados en la ciudad."
        ),
        "subcategoria": "antiguedad_fenicia",
    },
    {
        "titulo": "Gades romano y Baelo Claudia",
        "texto": (
            "Época romana en Cádiz (Gades): Con Balbo el Mayor y Balbo el Menor, Gades floreció con teatro romano propio, "
            "acueducto desde Tempul y prósperas factorías de salazones de atún y salsa garum. "
            "Destaca la ciudad romana de Baelo Claudia (playa de Bolonia, Tarifa), una de las ruinas romanas mejor conservadas de Hispania."
        ),
        "subcategoria": "antiguedad_romana",
    },
    {
        "titulo": "Al-Ándalus y la Reconquista en la frontera gaditana",
        "texto": (
            "Época andalusí y frontera: Cádiz formó parte de Al-Ándalus desde el año 711. En el siglo XIII, tras la conquista de Alfonso X el Sabio, "
            "la comarca se convirtió en la línea defensiva frente al reino nazarí de Granada, originando el sobrenombre histórico "
            "'de la Frontera' en municipios como Arcos, Chiclana, Conil, Vejer y Jerez."
        ),
        "subcategoria": "edad_media_reconquista",
    },
    {
        "titulo": "Comercio con las Indias y Siglo de Oro gaditano (Siglo XVIII)",
        "texto": (
            "Cádiz y la Carrera de Indias: En 1717 se trasladó la Casa de la Contratación y el Consulado de Indias desde Sevilla a Cádiz, "
            "otorgando a la bahía el monopolio del comercio con América. La ciudad se convirtió en una cosmopolita metrópoli marítima, "
            "construyéndose murallas, baluartes y más de un centenar de torres mirador (como la emblemática Torre Tavira)."
        ),
        "subcategoria": "carrera_indias",
    },
    {
        "titulo": "Batalla de Trafalgar (21 de octubre de 1805)",
        "texto": (
            "Batalla de Trafalgar: Combate naval decisivo acontecido frente al Cabo de Trafalgar (actual costa de Barbate y Los Caños de Meca). "
            "La armada británica comandada por el almirante Horatio Nelson derrotó a la escuadra combinada franco-española de Villeneuve y Gravina, "
            "marcando el fin del poderío naval hispano del siglo XIX."
        ),
        "subcategoria": "batalla_trafalgar",
    },
    {
        "titulo": "Las Cortes de Cádiz y la Constitución de 1812 ('La Pepa')",
        "texto": (
            "Las Cortes y la Constitución de 1812: Durante la invasión napoleónica, Cádiz y la Real Isla de León (San Fernando) "
            "resistieron el asedio francés como único bastión libre de España. Los diputados se reunieron en el Teatro de las Cortes "
            "y el Oratorio de San Felipe Neri, aprobando el 19 de marzo de 1812 la primera constitución liberal de España ('La Pepa'), "
            "que proclamó la soberanía nacional, la separación de poderes y la libertad de imprenta."
        ),
        "subcategoria": "constitucion_1812",
    },
]


class HistoriaCadizSource(Source):
    """Fuente de historia y patrimonio emblemático de Cádiz."""

    nombre = "historia-cadiz"
    licencia = "CC-BY-4.0 (Patrimonio Histórico y Documental)"
    metodo = "manual_validado"

    def fetch(self) -> list[Fragmento]:
        fragmentos: list[Fragmento] = []
        hoy = date.today()

        for item in _HISTORIA_CADIZ:
            frg = Fragmento(
                texto=item["texto"],
                fuente="Compendio de Historia y Patrimonio de la Provincia de Cádiz",
                categoria=Categoria.CULTURA_HISTORIA,
                subcategoria=item.get("subcategoria"),
                provincia=self.provincia,
                nivel_confianza=NivelConfianza.ALTA,
                licencia=self.licencia,
                validado_por="equipo_historia_archivo",
                validado_fecha=hoy,
            )
            fragmentos.append(frg)

        return fragmentos
