Estamos en una etapa que analizamos información, planteamos un RAG de conocimientos para una pequeña ia local en una raspberry pi 5 con qwen 2.5 enfocada a resolver problemas de emergencias en lugares dónde no tendremos acceso a internet o cobertura telefónica.

Estoy agrupando información y planteando la base de dónde extraer posteriormente conocimientos.

Planteo actualmente fichas de especificación en `docs/rag/` y datos procesados en `data/processed/`.

En el directorio docs/rag hay ficheros de especificación de fuentes y checklists para garantizar la calidad de los datos.

Aquí tenemos una ficha que agrupa cada grupo de información antes de procesarlo y extraer los conocimientos necesarios dentro de data/processed/.

## data/processed/

En data/processed/ hay que tener estos datos y cumplir estas condiciones:

- Un directorio por cada tipo de dato
- Un fichero por cada dato de ese tipo
- Un archivo README.md en cada directorio con la descripción de los datos y las condiciones de uso

## docs/rag

Necesito que tenga la máxima información posible para llevar un control perfecto de los datos que necesitaré en el RAG y fichas muy detalladas para que en el futuro cuando se actualicen las fuentes de datos con nueva información poder actualizar generando los datos otra vez minimizando los problemas + evitando problemas resueltos anteriormente + evitando mapear datos que ya se habían mapeado antes reduciendo consumo de tokens.
Las fichas deben tener toda la información necesaria para generar los datos del RAG en el futuro.
La información que aquí adjunto es lo que considero base mínima para este control pero no debemos limitarnos a ella y hay que investigar más.

En docs/rag hay que tener estos datos y cumplir estas condiciones:

- Anotar restricciones y limitaciones de la fuente de datos
- Separación atómica de datos necesarios agrupando por una sección
- Un checklist al final del archivo con cada sección
- Fecha de creación
- Fecha de última actualización
- Fecha de última vez que se estrajeron datos y se procesaron a partir de la fuente para generar los conocimientos en `data/processed/`
- Fecha recomendada para la próxima actualización y generar conocimientos
- Descripción detallada del bloque justo debajo de su título
- Descripción detallada de la sección justo debajo de su título
- Anotación de problemas encontrados
- Mapeo de datos por ejemplo si hay que especificar/aclarar campos o traducir entre ellos, para tenerlo claro si ya resolvimos el problema
- Enlace al archivo que generará en data/processed/
- Licencia si es necesario

Los archivos markdown que se crearán en rag estarán agrupados así (no digo que sea exactamente este nombre):

- Agricultura
- Ganadería
- apoyo psicosocial
- astronomia
- mareas
- puertos
- faros
- territorio medio natural (playas, rios, embalses, senderos...)
- geografia-municipios
- geografia-localizaciones-criticas (ubicaciones asociadas a cada municipio para cruz roja, policia, hospitales,guardia civil, guardia rural... cualquier ubicación crítica de interés)
- fiestas
- tradiciones
- historia-patrimonio
- legislacion-derechos
- preparacion-prevención
- preparacion-supervivencia
- guias-proteccion-civil
- guias-guardia-civil
- guias-cruz-roja
- guias-dgt
- radio-comunicaciones
- primeros auxilios
- toxicologia-sustancias
- transporte-publico
