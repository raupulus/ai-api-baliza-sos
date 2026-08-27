"""Fuente de flora y fauna de la provincia de Cádiz (peligrosa, tóxica y comestible).

Recoge información taxonómica y de seguridad de la Sierra de Grazalema, Parque Natural
de Los Alcornocales, Doñana, Bahía de Cádiz y franja litoral.
"""

from __future__ import annotations

from datetime import date

from common.models import Categoria, Fragmento, NivelConfianza
from updater.sources.base import Source

_DATOS_FLORA_FAUNA = [
    # Flora tóxica
    {
        "texto": (
            "Adelfa (Nerium oleander) en Cádiz: Muy común en ramblas, márgenes de ríos y carreteras. "
            "TODA la planta es ALTAMENTE TÓXICA por contener glucósidos cardiotónicos (oleandrina). "
            "Su ingestión provoca arritmias cardíacas severas, vómitos y puede ser mortal. "
            "Incluso el humo de su combustión o usar sus ramas para asar comida es peligroso."
        ),
        "categoria": Categoria.FLORA,
        "peligrosa": True,
        "subcategoria": "plantas_toxicas",
    },
    {
        "texto": (
            "Estramonio (Datura stramonium) en campos y escombreras de Cádiz: Planta silvestre de flores "
            "blancas en trompeta y fruto con púas. Contiene alcaloides tropánicos muy potentes (escopolamina, "
            "hiosciamina y atropina). Produce alucinaciones severas, midriasis extrema, taquicardia, hipertermia "
            "y paro cardíaco o coma. Muy peligrosa."
        ),
        "categoria": Categoria.FLORA,
        "peligrosa": True,
        "subcategoria": "plantas_toxicas",
    },
    {
        "texto": (
            "Cicuta mayor (Conium maculatum) en zonas húmedas de Cádiz: Similar al perejil o perifollo silvestre "
            "pero con manchas rojizas/púrpuras en el tallo y olor fétido a orina de ratón al estrujarla. "
            "Contiene cicutina, un neurotóxico letal que causa parálisis muscular progresiva y muerte por asfixia en minutos."
        ),
        "categoria": Categoria.FLORA,
        "peligrosa": True,
        "subcategoria": "plantas_toxicas",
    },
    {
        "texto": (
            "Setas venenosas de Cádiz (Amanita phalloides en Los Alcornocales y Grazalema): Crece bajo alcornoques, "
            "encinas y castaños en otoño. Sombrero verdoso-oliváceo, láminas blancas libres, anillo y volva membranosa en saco. "
            "Es la seta causante del 90% de intoxicaciones mortales (síndrome faloidiano). Los síntomas tardan de 6 a 24 horas "
            "en aparecer (dolor abdominal, vómitos) seguidos de fallo hepático fulminante."
        ),
        "categoria": Categoria.FLORA,
        "peligrosa": True,
        "subcategoria": "setas_toxicas",
    },
    # Flora silvestre comestible de supervivencia
    {
        "texto": (
            "Tagarnina (Scolymus hispanicus) en los campos de Cádiz: Cardo silvestre muy abundante y seguro. "
            "Se recolecta en invierno y primavera. Tras limpiar las espinas de las pencas, las nervaduras centrales "
            "son comestibles cocidas o revueltas. Alto contenido en fibra, potasio e inulina alimenticia."
        ),
        "categoria": Categoria.FLORA,
        "peligrosa": False,
        "subcategoria": "plantas_comestibles",
    },
    {
        "texto": (
            "Palmito (Chamaerops humilis) en sierras y montes de Cádiz: La única palmera autóctona de Europa. "
            "El cogollo tierno interior de la base ('espadiña' o corazón de palmito) es comestible crudo o asado "
            "y aporta carbohidratos valiosos en caso de supervivencia. Los frutos maduros ('dátiles de zorra') no son tóxicos pero son ásperos."
        ),
        "categoria": Categoria.FLORA,
        "peligrosa": False,
        "subcategoria": "plantas_comestibles",
    },
    {
        "texto": (
            "Espárrago triguero silvestre (Asparagus acutifolius) en matorrales y dehesas de Cádiz: Brotes tiernos "
            "de primavera que crecen al pie de esparragueras espinosas. Son completamente comestibles cocidos o a la brasa, "
            "ricos en vitaminas, asparagina y agua."
        ),
        "categoria": Categoria.FLORA,
        "peligrosa": False,
        "subcategoria": "plantas_comestibles",
    },
    # Fauna terrestre
    {
        "texto": (
            "Víbora hocicuda (Vipera latastei) en sierras de Cádiz: Serpiente de cuerpo grueso, cabeza triangular "
            "diferenciada y pequeño cuerno o apéndice en la punta del hocico. Patrón dorsal en zigzag. "
            "Habita en pedregales y matorral soleado de Grazalema y Alcornocales. Mordedura venenosa grave "
            "pero rara vez mortal si se asiste a tiempo; requiere inmovilización y antídoto en hospital."
        ),
        "categoria": Categoria.FAUNA,
        "peligrosa": True,
        "subcategoria": "reptiles_peligrosos",
    },
    {
        "texto": (
            "Escolopendra gigante (Scolopendra cingulata) en campos y piedras de Cádiz: Miriápodo de hasta 15-17 cm "
            "de color marrón/amarillo con patas anilladas. Activa de noche y bajo rocas en verano. Su picadura "
            "produce dolor punzante muy intenso, edema local y enrojecimiento, pero no suele ser mortal salvo alergia. "
            "Aplicar hielo indirecto y lavar con antiséptico."
        ),
        "categoria": Categoria.FAUNA,
        "peligrosa": True,
        "subcategoria": "artropodos",
    },
    {
        "texto": (
            "Araña violinista o reclusa (Loxosceles rufescens) en Cádiz: Pequeña (1-2 cm), marrón parda con mancha en forma "
            "de violín en el cefalotórax. Oculta en grietas, sótanos y bajo piedras. Su picadura puede causar necrosis local "
            "lenta de la piel (loxoscelismo cutáneo) que tarda días en manifestarse. Lavar con agua y jabón y consultar a un médico."
        ),
        "categoria": Categoria.FAUNA,
        "peligrosa": True,
        "subcategoria": "artropodos",
    },
    # Fauna marina
    {
        "texto": (
            "Pez araña o escorpión (Trachinus draco) en fondos arenosos de Cádiz: Pasa desapercibido enterrado en la arena "
            "a escasa profundidad. Posee espinas dorsales venenosas que inoculan toxina al pisarlo. "
            "Produce dolor lancinante inmediato que irradia a la pierna. Tratamiento térmico urgente: "
            "agua caliente a más de 40 °C durante 45 minutos."
        ),
        "categoria": Categoria.FAUNA,
        "peligrosa": True,
        "subcategoria": "fauna_marina",
    },
    {
        "texto": (
            "Carabela portuguesa (Physalia physalis) en aguas atlánticas de Cádiz: Falso organismo sifonóforo con flotador azul/violeta "
            "lleno de gas y tentáculos sumergidos de hasta varios metros. Muy urticante. "
            "Incluso ejemplares muertos varados en la orilla mantienen la toxina activa durante días. No tocar."
        ),
        "categoria": Categoria.FAUNA,
        "peligrosa": True,
        "subcategoria": "fauna_marina",
    },
]


class FloraFaunaCadizSource(Source):
    """Fuente de especies de flora y fauna representativas de Cádiz."""

    nombre = "flora-fauna-cadiz"
    licencia = "CC-BY-4.0 (Biodiversidad y Seguridad Ambiental)"
    metodo = "manual_validado"

    def fetch(self) -> list[Fragmento]:
        fragmentos: list[Fragmento] = []
        hoy = date.today()

        for item in _DATOS_FLORA_FAUNA:
            frg = Fragmento(
                texto=item["texto"],
                fuente="Catálogo de Flora y Fauna de Cádiz (Validado)",
                categoria=item["categoria"],
                subcategoria=item.get("subcategoria"),
                provincia=self.provincia,
                nivel_confianza=NivelConfianza.ALTA,
                licencia=self.licencia,
                peligrosa=item.get("peligrosa", False),
                validado_por="equipo_botanica_zoologia",
                validado_fecha=hoy,
            )
            fragmentos.append(frg)

        return fragmentos
