# Cosas a valorar

> Evaluación y organización resultantes: [`docs/rag/catalogo-adquisicion.md`](../../docs/rag/catalogo-adquisicion.md). El listado original se conserva como entrada y trazabilidad de la planificación; no implica que sus enlaces estén aprobados para descarga o indexación.

La información que sea localizada se tiene que aplicar para todas las localidades/pedanías/ciudades/pueblos de la provincia de cádiz entera.

- 230 bytes por mensaje máximo (el límite real es lo que deja enviar por RF meshtastic que es la red con más limitación de todas)
- Máximo 3 mensajes por pregunta, se devolverá por la api cada pregunta enumerada
- La lista final de descarga debe ser un archivo dónde se describa cada elemento que se quiere desarcargar y dentro de su bloque tenga los enlaces con información de que hay en cada enlace y si es necesario un mapeo de datos
- En el listado de decargar que hay más abajo, los enlaces son "para valorar" y no para descargar directamente o sacar el primer dato que se vea a ciegas.
- Añade en cada bloque la fiabilidad de la información, si es oficial, si es de un organismo de confianza, si es de un usuario registrado, etc.
- Los enlaces adjuntos no tienen por que aportar toda la información, usarlo para mirar si hay información relevante pero no limitarse solo a esa fuente.

## Fuentes fiables (no se limita a estas, es orientativa pero todo lo de ellas marcar fiable)

Todos los subdominios de estos son igual de fiables.

- https://www.boe.es, https://boe.es
- https://policia.es/_es/index.php
- https://european-union.europa.eu/index_es
- https://www.juntadeandalucia.es
- https://web.guardiacivil.es y https://www.guardiacivil.es
- https://www2.cruzroja.es
- https://www.proteccioncivil.es/
- https://www.dipucadiz.es/
- https://www.sepe.es
- https://www.bopcadiz.es/
- https://www.cadizturismo.com
- https://datos.gob.es, https://gob.es
- https://www.dgt.es
- https://www.sanidad.gob.es

## Descargar, parsear y almacenar en el RAG esta información

- Manual de primeros auxilios atención básica
- Manual de primeros auxilios atención urgencias o graves
- Instrucciones para intervenciones de urgencias: parto, traqueostomía, atragantamiento severo, caídas, esguinces o huesos rotos,
- Leyes españolas
- Rutas de trenes de cadiz
- Rutas de autobuses de cadiz
- Base de datos de flora de cadiz
- Base de datos de Fauna de cadiz
- Playas, rios, mar,oceano, afluentes, embalses de cadiz completos con geolocalización de zona
- guías de protección civil
- guías de cruz roja
- sustancias estupefacientes con síntomas + efectos + posibles riesgos inmediatos:  necesario por si hay intoxicación de riesgo accidental o cualquier motivo (como libro PHARMACOTEON)
- manual de supervivencia básico
- manual de supervivencia avanzado
- Todas las ciudades de la provincia con historia e información de lugares históricos o relevante
- Calendario de festivos del año actual para toda la provincia
- Actuación ante: inundaciones, terremotos, incendios... cuando nos veamos atrapados
- Lista de alimentos a tener guardados para emergencias (conservas, miel...)
- guía para potabilizar agua
- Guía de meshtastic
-  VADEMECUM  REMER (descargado en directorio raw como "Vademecum_Remer_2017.rar" también descomprimido sin "rar" y es lo mismo que hay en la versión online): https://www.ea1uro.com/proteccioncivil/vade01.htm;https://cpage.mpr.gob.es/publicacion/vademecum-remer-2017-126170195-0000/;https://vademecum.stage7.net/;https://vademecum.stage7.net/
- Guías de seguridad ofrecidas por Guardia civil
- Guías de seguridad ofrecidas por Policía Nacional
- Peces de la zona y zonas algo más alejadas pero que puedan aparecer aquí. Indicar si se pueden comer o tienen toxinas.
- Problemas de contaminación en flora y fauna
- Kit de emergencias para casa
- Kit de emergencias para montaña
- Kit de emergencias para coche
- Direcciones de cuerpos de seguridad (policía local, guardia rural, guardia civil, policia nacional), centros médicos y hospitales, lugar de protección civil y cruz roja... cualquier dirección útil de las ciudades en cádiz provincia
- Guía de cultivo para productos que hay habitualmente cultivados en campos caditanos
- Listado de cultivos típicos en la provincia de cádiz, propiedades + descripción + forma de cultivarlos
- Listado de ganado típico en la provincia de cádiz, propiedades, cuidados, reproducción, fechas en las que necesita atención especial.
- Plantas y remedios medicinales (descargado en raw/Dioscórides_Plantas_y_remedios_medicinales_Libros_I_III_ocr_G_1998.pdf)
- Atención psicológica ante catástrofes, accidentes etc... como tratar a personas que acaban de sufrir un accidente o recibir una mala noticia.
- Guía oficial de meshtastic
- Guía oficial de Winlink, vara hf, VarAC, PinPoint APRS
- Frecuencias comunes en emergencias por radiofrecuencia
- Derechos humanos: https://eur-lex.europa.eu/legal-content/ES/TXT/HTML/?uri=CELEX:12012P/TXT&from=ES
- Código civil: https://www.boe.es/biblioteca_juridica/codigos/codigo.php?id=034_Codigo_Civil_y_legislacion_complementaria&modo=2
- Constitución española: https://constitucion.congreso.es/constitucion-1978/descarga-constitucion; https://www.boe.es/biblioteca_juridica/abrir_pdf.php?id=PUB-PB-2026-116
- Manual sobre Telecomunicaciones de emergencia https://www.itu.int/pub/D-HDB-HET/es
- Teléfonos de emergencias generales de andalucia y la provincia de cádiz pero también los concretos en cada ciudad (descargados los de cada ciudad en csv/telefonos_emergencia_cadiz_municipios.csv pero verificar que se generó con ia y puede estar mal). Los de provincia: https://institucional.cadiz.es/area/Urgencias-092/143
- Calendario astronómico
- Almanaque náutico "https://www.nauticalalmanac.it/es/astronomia-navegacion/almanaque-nautico", descargas "https://www.nauticalalmanac.it/es/pd-esp-almnau" y "https://www.nauticalalmanac.it/es/pd-esp-almnau"
- calendario de mareas
- calendario lunar
- calendario solar
- guía astronómica para ubicarse por las estrellas
- guía de ingienería básica para la supervivencia: pólvora, jabón
- Fabricar cerveza, whisky, ginebra hidromiel
- problemas de salud comunes y tratamientos (ampollas, gripe, resfriados, fiebre, tos, dolor de cabeza, quemadura solar, golpe en la cabeza etc.)
- Parques naturales con detalles
- Listado de senderos con detalles

##  Kit de emergencias para el coche

En caso de que haya una previsión meteorológica de riesgo y te sea imprescindible coger el coche, deberías llevar un kit de emergencias por si tienes que pasar más tiempo del normal o te encuentras alguna incidencia con el mal tiempo.

¿Qué debe contener el kit de emergencias?

    Agua potable
    Alimentos que no se estropeen y energéticos
    Manta o ropa de abrigo
    Cadenas para las ruedas
    Caja de herramientas polivalentes
    Linterna con pilas de repuesto
    Pala o cepillo de nieve
    A partir del 1 de enero de 2026 es obligatorio en todo el Estado llevar en el coche un dispositivo luminoso de color amarillo, conocido como baliza V16, que sustituye los triángulos reflectantes
    Botiquín de primeros auxilios con gasas, cinta adhesiva, bendiciones, pomada antibiótica, analgésico, guantes sin látex, tijeras, hidrocortisona, termómetro, pinzas y compresa fría instantánea

##  Material adicional para mascotas

Los animales pueden estresarse o espantarse durante una situación de emergencia: tu mascota debe formar parte de tu plan de emergencias antes, durante y después para minimizar el impacto que pueda tener durante las situaciones de riesgo.

¿Qué material adicional debe contener el kit básico?

    Comprobante de identificación o propiedad (Registro general de animales de compañíaSe abre en una nueva pestaña) y fotografía con la mascota) y fotografía con la mascota
    Comida y agua para unos cuantos días
    Registro médico, cartilla veterinaria actualizada y la medicación que pueda estar tomando
    Jaula o transportín
    Correa, morrión
    Manta, sábana o juguetes
    Útiles higiénicos para recoger los excrementos y lavarla si fuera necesario

En caso de emergencia, sigue estos consejos:

    Asegúrate de que tu mascota está bien identificada con el chip y que los datos están actualizados.
    Busca algún responsable, como un vecino o familiar, que se pueda hacer cargo de la evacuación de tu mascota si tú no estás en casa o si en el lugar donde te evacuan no aceptan animales.
    Haz una lista de lugares como hoteles o albergues donde acepten mascotas en caso de que tengas que pasar alguna noche fuera de casa y nadie la pueda cuidar.
    Practica devez en cuando cómo moverla en transportín o jaula para que esté acostumbrada a ella.
    Haz una lista de veterinarios en posibles zonas donde puedas ser reubicado y tengas a mano el teléfono de tu veterinario habitual.

## Kit de emergencias básico

Si te quedas aislado en casa o sin suministros básicos es necesario que tengas un kit de emergencias con las provisiones básicas para ser autosuficiente durante algunas horas o días.

    Agua potable (1,5 litros por persona y día, como mínimo)
    Botiquín y medicación crónica
    Linterna con pilas de repuesto o frontal
    Radio con pilas
    Documentación personal (DNI, tarjeta sanitaria, pólizas de seguros...), preferiblemente en una bolsa impermeable
    Dinero en efectivo y tarjeta bancaria
    Teléfono móvil con cargador y, si es posible, una batería externa
    Productos de apoyo, como gafas, muletas, bastón, andador, audífono y pilas, dispositivo de respiración, etc.

    Alimentos de larga duración que no requieran ser cocinados.

Si las autoridades ordenan la evacuación, es posible que no puedas volver a casa durante un tiempo. Por ello, completa el kit básico con estos elementos adicionales:

    Ropa y zapatos de repuesto.
    Impermeable.
    Productos de higiene personal.
    Llaves de casa y del coche.

¡Atención!

No te olvides también de las necesidades específicas de los miembros de la familia que son más vulnerables en una situación de emergencia, como personas con discapacidad, personas mayores o niños. Para los niños, usar una pulsera identificadora por si se pierden o se desorientan.
