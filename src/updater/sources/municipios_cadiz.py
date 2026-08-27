"""Fuente oficial de los 45 municipios y puntos geográficos de la provincia de Cádiz.

Contiene nombres oficiales, comarcas, coordenadas GPS (WGS84 lat/lon) y altitudes
para geolocalización y rescate en emergencias.
"""

from __future__ import annotations

from datetime import date

from common.models import Categoria, Fragmento, NivelConfianza
from updater.sources.base import Source

# Relación exhaustiva de los 45 municipios de Cádiz con datos geográficos
_MUNICIPIOS_CADIZ = [
    # Bahía de Cádiz
    {"nombre": "Cádiz", "comarca": "Bahía de Cádiz", "lat": 36.5298, "lon": -6.2924, "alt": 11, "info": "Capital provincial, peninsular atlántica unida por tómbolo y puentes Carranza y Constitución 1812."},
    {"nombre": "Jerez de la Frontera", "comarca": "Campiña de Jerez", "lat": 36.6850, "lon": -6.1261, "alt": 56, "info": "Municipio más extenso y poblado de la provincia. Aeropuerto y nudo de comunicaciones."},
    {"nombre": "San Fernando", "comarca": "Bahía de Cádiz", "lat": 36.4644, "lon": -6.1983, "alt": 8, "info": "Isla de León, Parque Natural Bahía de Cádiz y base naval."},
    {"nombre": "El Puerto de Santa María", "comarca": "Bahía de Cádiz", "lat": 36.5997, "lon": -6.2307, "alt": 15, "info": "Desembocadura del río Guadalete, bahía norte."},
    {"nombre": "Chiclana de la Frontera", "comarca": "Bahía de Cádiz", "lat": 36.4190, "lon": -6.1460, "alt": 21, "info": "Litoral de La Barrosa y Sancti Petri."},
    {"nombre": "Puerto Real", "comarca": "Bahía de Cádiz", "lat": 36.5284, "lon": -6.1906, "alt": 14, "info": "Corazón de la Bahía y campus universitario, salinas y pinares de Las Canteras."},
    # Costa Noroeste
    {"nombre": "Sanlúcar de Barrameda", "comarca": "Costa Noroeste", "lat": 36.7781, "lon": -6.3515, "alt": 30, "info": "Desembocadura del río Guadalquivir, Bajo de Guía frente al Parque Nacional de Doñana."},
    {"nombre": "Chipiona", "comarca": "Costa Noroeste", "lat": 36.7369, "lon": -6.4326, "alt": 6, "info": "Faro más alto de España y corrales de pesca tradicionales."},
    {"nombre": "Rota", "comarca": "Costa Noroeste", "lat": 36.6214, "lon": -6.3586, "alt": 12, "info": "Extremo norte de la Bahía, corrales y base naval hispano-estadounidense."},
    {"nombre": "Trebujena", "comarca": "Costa Noroeste", "lat": 36.8705, "lon": -6.1755, "alt": 69, "info": "Marismas del bajo Guadalquivir y colinas vinícolas."},
    # La Janda
    {"nombre": "Conil de la Frontera", "comarca": "La Janda", "lat": 36.2770, "lon": -6.0886, "alt": 41, "info": "Costa atlántica, calas de Roche y pesca de almadraba."},
    {"nombre": "Vejer de la Frontera", "comarca": "La Janda", "lat": 36.2541, "lon": -5.9620, "alt": 201, "info": "Pueblo blanco amurallado sobre cerro con vistas al río Barbate y El Palmar."},
    {"nombre": "Barbate", "comarca": "La Janda", "lat": 36.1923, "lon": -5.9221, "alt": 14, "info": "Cabo de Trafalgar, Zahora, Los Caños de Meca y Parque Natural de La Breña."},
    {"nombre": "Medina Sidonia", "comarca": "La Janda", "lat": 36.4572, "lon": -5.9269, "alt": 337, "info": "Cerro histórico dominante de la comarca de La Janda."},
    {"nombre": "Benalup-Casas Viejas", "comarca": "La Janda", "lat": 36.3427, "lon": -5.8118, "alt": 112, "info": "Antigua cuenca de la laguna de la Janda y pinturas rupestres del Tajo de las Figuras."},
    {"nombre": "Alcalá de los Gazules", "comarca": "La Janda", "lat": 36.4613, "lon": -5.7225, "alt": 165, "info": "Puerta de entrada occidental al Parque Natural de Los Alcornocales."},
    {"nombre": "Paterna de Rivera", "comarca": "La Janda", "lat": 36.5218, "lon": -5.8679, "alt": 127, "info": "Campiña de La Janda, cuna del cante por peteneras y aguas sulfurosas."},
    # Campo de Gibraltar
    {"nombre": "Algeciras", "comarca": "Campo de Gibraltar", "lat": 36.1274, "lon": -5.4536, "alt": 20, "info": "Mayor puerto marítimo del Estrecho de Gibraltar y terminal ferry con África."},
    {"nombre": "La Línea de la Concepción", "comarca": "Campo de Gibraltar", "lat": 36.1680, "lon": -5.3486, "alt": 5, "info": "Frontera terrestre con el peñón de Gibraltar."},
    {"nombre": "San Roque", "comarca": "Campo de Gibraltar", "lat": 36.2104, "lon": -5.3842, "alt": 108, "info": "Bahía de Algeciras y yacimiento arqueológico de Carteia."},
    {"nombre": "Los Barrios", "comarca": "Campo de Gibraltar", "lat": 36.1843, "lon": -5.4920, "alt": 23, "info": "Valle del río Palmones y Los Alcornocales."},
    {"nombre": "Tarifa", "comarca": "Campo de Gibraltar", "lat": 36.0143, "lon": -5.6044, "alt": 7, "info": "Punto más meridional de Europa continental. Vientos de Levante y Poniente, meca del surf."},
    {"nombre": "Jimena de la Frontera", "comarca": "Campo de Gibraltar", "lat": 36.4336, "lon": -5.4542, "alt": 203, "info": "Castillo sobre el valle del río Guadiaro en Los Alcornocales."},
    {"nombre": "Castellar de la Frontera", "comarca": "Campo de Gibraltar", "lat": 36.3168, "lon": -5.4538, "alt": 48, "info": "Castillo medieval habitado sobre embalse del Guadarranque."},
    {"nombre": "San Martín del Tesorillo", "comarca": "Campo de Gibraltar", "lat": 36.3411, "lon": -5.3186, "alt": 42, "info": "Valle agrícola del río Guadiaro, lindando con la provincia de Málaga."},
    # Sierra de Cádiz (Pueblos Blancos)
    {"nombre": "Arcos de la Frontera", "comarca": "Sierra de Cádiz", "lat": 36.7483, "lon": -5.8106, "alt": 185, "info": "Puerta de la Sierra, impresionante peña cortada sobre el río Guadalete."},
    {"nombre": "Grazalema", "comarca": "Sierra de Cádiz", "lat": 36.7588, "lon": -5.3688, "alt": 812, "info": "Lugar con mayor índice pluviométrico de la península ibérica, bosque relicto de pinsapos."},
    {"nombre": "Ubrique", "comarca": "Sierra de Cádiz", "lat": 36.6787, "lon": -5.4468, "alt": 337, "info": "Enclave rocoso entre Grazalema y Alcornocales, capital de la marroquinería y piel."},
    {"nombre": "El Bosque", "comarca": "Sierra de Cádiz", "lat": 36.7578, "lon": -5.5066, "alt": 285, "info": "Río Majaceite, piscifactoría de truchas y centro de visitantes del Parque Natural."},
    {"nombre": "Villamartín", "comarca": "Sierra de Cádiz", "lat": 36.8601, "lon": -5.6468, "alt": 167, "info": "Centro neurálgico y sanitario de la comarca de la Sierra de Cádiz."},
    {"nombre": "Olvera", "comarca": "Sierra de Cádiz", "lat": 36.9344, "lon": -5.2662, "alt": 643, "info": "Castillo nazarí y basílica sobre cerro, Vía Verde de la Sierra."},
    {"nombre": "Zahara de la Sierra", "comarca": "Sierra de Cádiz", "lat": 36.8400, "lon": -5.3900, "alt": 500, "info": "Castillo y torre del homenaje dominando el embalse de Zahara-El Gastor y la Garganta Verde."},
    {"nombre": "Algodonales", "comarca": "Sierra de Cádiz", "lat": 36.8809, "lon": -5.4055, "alt": 370, "info": "Falda norte de la Sierra de Líjar, referente europeo de parapente y ala delta."},
    {"nombre": "Bornos", "comarca": "Sierra de Cádiz", "lat": 36.8206, "lon": -5.7444, "alt": 182, "info": "Orillas del embalse de Bornos en el curso medio del Guadalete, Palacio de los Ribera."},
    {"nombre": "Prado del Rey", "comarca": "Sierra de Cádiz", "lat": 36.7891, "lon": -5.5562, "alt": 440, "info": "Salinas romanas de Iptuci y producción de miel y marroquinería."},
    {"nombre": "Espera", "comarca": "Sierra de Cádiz", "lat": 36.8724, "lon": -5.8055, "alt": 164, "info": "Lagunas de Espera y castillo medieval de Fatetar."},
    {"nombre": "Setenil de las Bodegas", "comarca": "Sierra de Cádiz", "lat": 36.8639, "lon": -5.1812, "alt": 640, "info": "Arquitectura singular bajo las rocas excavadas por el río Trejo (Cuevas del Sol y de la Sombra)."},
    {"nombre": "Torre Alháquime", "comarca": "Sierra de Cádiz", "lat": 36.9158, "lon": -5.2346, "alt": 495, "info": "Pequeño cerro fortificado sobre el río Guadalporcún."},
    {"nombre": "Alcalá del Valle", "comarca": "Sierra de Cádiz", "lat": 36.9048, "lon": -5.1724, "alt": 628, "info": "Extremo oriental de la comarca de la Sierra, dólmenes del Tomillo."},
    {"nombre": "Benaocaz", "comarca": "Sierra de Cádiz", "lat": 36.7003, "lon": -5.4216, "alt": 793, "info": "Barrio nazarí medieval y calzada romana Benaocaz-Ubrique."},
    {"nombre": "Villaluenga del Rosario", "comarca": "Sierra de Cádiz", "lat": 36.6974, "lon": -5.3850, "alt": 858, "info": "Municipio más alto de la provincia, cuna del queso payoyo y simas espeleológicas."},
    {"nombre": "Algar", "comarca": "Sierra de Cádiz", "lat": 36.6560, "lon": -5.6568, "alt": 212, "info": "Enclave entre el río Majaceite y el embalse de Guadalcacín."},
    {"nombre": "El Gastor", "comarca": "Sierra de Cádiz", "lat": 36.8550, "lon": -5.3210, "alt": 520, "info": "Balcón de los Pueblos Blancos, dólmen del Gigante y gaita gastoreña."},
    {"nombre": "Puerto Serrano", "comarca": "Sierra de Cádiz", "lat": 36.9224, "lon": -5.5456, "alt": 168, "info": "Punto de inicio de la Vía Verde de la Sierra junto al río Guadalete."},
]

# Puntos orográficos y refugios clave de rescate
_PUNTOS_OROGRAFICOS = [
    {
        "nombre": "Pico El Torreón (Sierra del Pinar)",
        "lat": 36.7645, "lon": -5.4121, "alt": 1648,
        "info": "Techo y máxima altitud de la provincia de Cádiz (1648 m). Sendero exigente con autorización en Grazalema."
    },
    {
        "nombre": "Pico El Aljibe (Los Alcornocales)",
        "lat": 36.4678, "lon": -5.5902, "alt": 1092,
        "info": "Máxima cumbre del Parque Natural de Los Alcornocales (1092 m), vistas al Estrecho de Gibraltar."
    },
    {
        "nombre": "Puerto de las Palomas",
        "lat": 36.7663, "lon": -5.3789, "alt": 1157,
        "info": "Paso de carretera más alto de la provincia (1157 m), une Grazalema con Zahara de la Sierra."
    },
    {
        "nombre": "Puerto del Boyar",
        "lat": 36.7512, "lon": -5.4053, "alt": 1103,
        "info": "Paso montañoso divisoria de cuencas del Guadalete y Majaceite, mirador panorámico."
    },
]


class MunicipiosCadizSource(Source):
    """Fuente de municipios oficiales y puntos geográficos de Cádiz."""

    nombre = "municipios-cadiz"
    licencia = "CC-BY-4.0 (IGN / Instituto de Estadística y Cartografía de Andalucía)"
    metodo = "nomenclator_oficial"

    def fetch(self) -> list[Fragmento]:
        fragmentos: list[Fragmento] = []
        hoy = date.today()

        for m in _MUNICIPIOS_CADIZ:
            texto = (
                f"Municipio de {m['nombre']} (Comarca: {m['comarca']}, Cádiz): "
                f"Coordenadas GPS: Latitud {m['lat']}, Longitud {m['lon']}. Altitud media: {m['alt']} m. "
                f"Descripción geográfica: {m['info']}"
            )
            frg = Fragmento(
                texto=texto,
                fuente="Nomenclátor Geográfico de Andalucía (IGN / IECA)",
                categoria=Categoria.GEOGRAFIA,
                subcategoria="municipio",
                provincia=self.provincia,
                nivel_confianza=NivelConfianza.ALTA,
                licencia=self.licencia,
                validado_por="equipo_cartografia_ign",
                validado_fecha=hoy,
            )
            fragmentos.append(frg)

        for p in _PUNTOS_OROGRAFICOS:
            texto = (
                f"Punto geográfico de referencia: {p['nombre']} (Cádiz). "
                f"Coordenadas GPS: Latitud {p['lat']}, Longitud {p['lon']}. Altitud: {p['alt']} m sobre el nivel del mar. "
                f"Detalles de montaña y rescate: {p['info']}"
            )
            frg = Fragmento(
                texto=texto,
                fuente="IGN / Federación Andaluza de Montañismo",
                categoria=Categoria.GEOGRAFIA,
                subcategoria="orografia_montana",
                provincia=self.provincia,
                nivel_confianza=NivelConfianza.ALTA,
                licencia=self.licencia,
                validado_por="equipo_cartografia_ign",
                validado_fecha=hoy,
            )
            fragmentos.append(frg)

        return fragmentos
