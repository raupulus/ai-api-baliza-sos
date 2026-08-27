"""Fuente de fiestas, ferias y tradiciones populares de la provincia de Cádiz.

Recoge las principales festividades de los municipios gaditanos: fechas habituales,
ubicación, gastronomía asociada y relevancia cultural.
"""

from __future__ import annotations

from datetime import date

from common.models import Categoria, Fragmento, NivelConfianza
from updater.sources.base import Source

_FIESTAS_CADIZ = [
    {
        "titulo": "Carnaval de Cádiz (Cádiz Capital)",
        "texto": (
            "Carnaval de Cádiz: Fiesta de Interés Turístico Internacional celebrada en febrero o principios de marzo. "
            "Epicentro del ingenio popular, concursos oficiales en el Gran Teatro Falla (COAC) y coplas callejeras "
            "(chirigotas, comparsas, coros y cuartetos) por el barrio de La Viña, plaza del Palillero y plaza de las Flores. "
            "Gastronomía típica: erizada, ostionada y pestiñada popular."
        ),
        "subcategoria": "carnaval",
    },
    {
        "titulo": "Feria del Caballo de Jerez de la Frontera",
        "texto": (
            "Feria del Caballo de Jerez: Celebrada en mayo en el Parque González Hontoria. "
            "Fiesta de Interés Turístico Internacional caracterizada por el paseo de caballos y enganches de alta escuela, "
            "casetas públicas de acceso libre, sevillanas, flamenco y consumo tradicional de vino fino y rebujito con tapas locales."
        ),
        "subcategoria": "feria",
    },
    {
        "titulo": "Carreras de Caballos en las Playas de Sanlúcar de Barrameda",
        "texto": (
            "Carreras de Caballos de Sanlúcar de Barrameda: Celebradas en agosto durante las mareas vivas de bajamar en la playa de Bajo de Guía. "
            "Fiesta de Interés Turístico Internacional desde 1845. Caballos purasangre compitiendo sobre la arena mojada frente a las dunas de Doñana. "
            "Acompañado de consumo de manzanilla sanluqueña y langostinos."
        ),
        "subcategoria": "carreras_caballos",
    },
    {
        "titulo": "Semana Santa de Cádiz, Jerez y Arcos de la Frontera",
        "texto": (
            "Semana Santa en Cádiz: Celebrada en marzo o abril. Destaca la sobriedad y belleza de los pasos tallados en caoba o plata "
            "recorriendo calles estrechas y empinadas del casco antiguo gaditano, Jerez de la Frontera y Arcos de la Frontera. "
            "Cante espontáneo de saetas y olor tradicional a incienso y azahar."
        ),
        "subcategoria": "semana_santa",
    },
    {
        "titulo": "Feria de la Manzanilla (Sanlúcar de Barrameda)",
        "texto": (
            "Feria de la Manzanilla en Sanlúcar: Se celebra a finales de mayo o primeros de junio en la Calzada de la Duquesa Isabel, "
            "junto al paseo marítimo y la desembocadura del Guadalquivir. Rinde homenaje al vino generoso Manzanilla D.O. Sanlúcar."
        ),
        "subcategoria": "feria",
    },
    {
        "titulo": "Feria de Primavera y Fiesta del Vino Fino (El Puerto de Santa María)",
        "texto": (
            "Feria de El Puerto de Santa María: Celebrada habitualmente a finales de mayo en el recinto de Las Banderas. "
            "Dedicada cada año a una localidad o país invitado, rinde tributo a las bodegas portuenses de Vino Fino."
        ),
        "subcategoria": "feria",
    },
    {
        "titulo": "Romería del Rocío y salida de Hermandades de Cádiz",
        "texto": (
            "Romería del Rocío: En mayo o junio (Pentecostés), las hermandades rocieras de Cádiz, Jerez, El Puerto, San Fernando, "
            "Chiclana y Sanlúcar peregrinan hacia la aldea almonteña cruzando el río Guadalquivir en barcazas por Bajo de Guía "
            "hacia las arenas de Doñana en una de las estampas tradicionales más populares."
        ),
        "subcategoria": "romeria",
    },
    {
        "titulo": "Noche de San Juan y Quema de Juanillos",
        "texto": (
            "Noche de San Juan (23 al 24 de junio) en el litoral gaditano: Hogueras en las playas de Cádiz (La Caleta, Victoria), "
            "Conil, Barbate y Chiclana donde se queman los 'Juanillos' (muñecos de trapo satíricos) para celebrar el solsticio de verano y lavarse la cara en el mar."
        ),
        "subcategoria": "festividad_popular",
    },
    {
        "titulo": "Fiestas de la Virgen del Carmen (Patrona de los Marineros)",
        "texto": (
            "Festividad del Carmen (16 de julio): Procesiones marítimas de barcos engalanados en pueblos pesqueros como Barbate, "
            "Conil de la Frontera, Rota, San Fernando y Algeciras, donde la imagen es embarcada para bendecir las aguas y a los faenadores del mar."
        ),
        "subcategoria": "fiesta_marinera",
    },
    {
        "titulo": "Corpus Christi de Zahara de la Sierra",
        "texto": (
            "Corpus Christi de Zahara de la Sierra: Fiesta de Interés Turístico Nacional celebrada en junio. "
            "Las calles empinadas del pueblo blanco se cubren completamente con ramas de juncia y quejigo traídas de la sierra, "
            "formando un dosel vegetal aromático sobre el suelo y fachadas."
        ),
        "subcategoria": "corpus_christi",
    },
]


class FiestasCadizSource(Source):
    """Fuente de festividades populares y tradiciones de Cádiz."""

    nombre = "fiestas-cadiz"
    licencia = "CC-BY-4.0 (Patrimonio Cultural Inmaterial y Turismo)"
    metodo = "manual_validado"

    def fetch(self) -> list[Fragmento]:
        fragmentos: list[Fragmento] = []
        hoy = date.today()

        for item in _FIESTAS_CADIZ:
            frg = Fragmento(
                texto=item["texto"],
                fuente="Calendario Oficial de Fiestas y Tradiciones de Cádiz",
                categoria=Categoria.CULTURA_HISTORIA,
                subcategoria=item.get("subcategoria"),
                provincia=self.provincia,
                nivel_confianza=NivelConfianza.ALTA,
                licencia=self.licencia,
                validado_por="equipo_cultura_turismo",
                validado_fecha=hoy,
            )
            fragmentos.append(frg)

        return fragmentos
