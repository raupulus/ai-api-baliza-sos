# 01 · Visión y requisitos

> **Última actualización:** 2026-08-27  
> **Ámbito:** Visión de producto, casos de uso, restricciones LoRa/RF y requisitos.

[← Volver al Índice de Documentación Técnica](README.md)

---

## 1. Visión

Un **asistente de emergencia y supervivencia offline** para la provincia de
Cádiz, accesible desde redes sin internet (**Meshtastic/LoRa**) y desde
Telegram. Ante una persona perdida, herida o ante un peligro natural, el sistema
devuelve indicaciones **breves, fiables y en español**, apoyándose en una base
de conocimiento local verificada y un modelo de lenguaje pequeño que corre en
una Raspberry Pi.

El valor diferencial es funcionar **sin conexión**: la inteligencia, el
conocimiento y los datos viven en el dispositivo.

## 2. Casos de uso objetivo

1. **Orientación.** "Estoy perdido, veo un faro a la derecha y un río." → El bot
   cruza referencias geográficas locales y sugiere dirección/puntos conocidos.
2. **Fauna peligrosa.** "Me ha picado una medusa en Zahara." → Identificación
   probable + primeros auxilios verificados + cuándo llamar al 112.
3. **Primeros auxilios.** "Mi amigo se ha cortado y sangra mucho." → Pasos
   básicos validados por fuente oficial.
4. **Supervivencia básica.** Agua, refugio, señalización, hipotermia/golpe de
   calor, según material oficial reutilizable.
5. **Geografía/playas/accesos.** Caminos, accesos, referencias costeras.

## 3. Actores

- **Cliente Meshtastic/LoRa** (externo): canal principal, muy limitado en ancho
  de banda y longitud de mensaje. Condiciona el formato de respuesta.
- **Cliente Telegram** (externo): canal secundario cuando hay datos/cobertura.
- **Operador/curador** (humano): valida el contenido sensible antes de indexar.
- **Backend** (este repo): API + RAG + LLM + actualizador de contexto.

## 4. Requisitos funcionales

- **RF1.** Exponer una API HTTP que reciba una consulta en lenguaje natural y
  devuelva **siempre un JSON** con la respuesta.
- **RF2.** La respuesta se divide en **1–3 mensajes de ≤ 250 caracteres**.
  Objetivo: 1 mensaje; usar 3 solo si es estrictamente necesario.
- **RF3.** Recuperar contexto relevante (RAG) de una base de conocimiento local
  antes de generar la respuesta.
- **RF4.** Responder **en español**.
- **RF5.** Permitir elegir el **modelo LLM por variable de entorno**.
- **RF6.** Permitir adaptar la **provincia por variables de entorno** sin tocar
  código.
- **RF7.** Un servicio independiente actualiza la base de conocimiento mediante
  ingesta por API y scraping puntual, con **validación humana** del contenido
  sensible antes de indexar.
- **RF8.** En respuestas médicas/de riesgo vital, incluir un **aviso** breve
  ("Info orientativa. Llama al 112.").

## 5. Requisitos no funcionales

- **RNF1 · Hardware mínimo.** Funcionar en **Raspberry Pi 4, 4 GB RAM**. Diseño
  escalable: en RPi5/8 GB debe poder usarse un modelo mayor solo cambiando env.
- **RNF2 · Offline.** En operación normal no depende de internet. Solo el
  actualizador de contexto necesita red, y de forma puntual/programada.
- **RNF3 · Tiempo de respuesta.** La API admite hasta **5 minutos** de espera
  por petición (límite duro). Objetivo realista: respuesta útil en menos tiempo;
  se corta la generación antes de los 5 min.
- **RNF4 · Concurrencia.** Pocos clientes simultáneos. Una única inferencia LLM
  a la vez (cola/semaforo) para proteger la RAM.
- **RNF5 · Fiabilidad del contenido.** Cero alucinaciones en contenido crítico:
  el LLM solo debe apoyarse en fragmentos recuperados y verificados; si no hay
  contexto suficiente, lo indica en lugar de inventar.
- **RNF6 · Simplicidad operativa.** Despliegue nativo con systemd, sin
  orquestadores ni dependencias innecesarias. Debe poder arrancar tras un
  reinicio sin intervención.
- **RNF7 · Solo Linux.** Foco en Raspberry Pi OS última versión.

## 6. Fuera de alcance (de este repositorio)

- Los **clientes** (bots de Telegram y Meshtastic): viven en otros proyectos.
- Entrenamiento o fine-tuning de modelos.
- Cartografía interactiva o navegación GPS en tiempo real.
- Alta disponibilidad / clúster: es un único dispositivo.

## 7. Restricciones y riesgos transversales

- **Legal/ético (médico).** No somos un servicio sanitario. El contenido de
  primeros auxilios debe provenir de fuentes oficiales reutilizables y mostrar
  aviso. Ante riesgo vital, dirigir al 112.
- **Licencias de datos.** Cada fuente tiene su licencia; se respeta y se cita
  (ver `docs/info/05-contratos-datos.md` y el módulo de fuentes).
- **Memoria.** El mayor riesgo técnico es quedarse sin RAM. Todo el diseño se
  somete al presupuesto de `docs/info/04-presupuesto-recursos.md`.
- **Calidad del RAG.** Recuperación pobre = respuesta pobre. La curación y el
  formato de fragmento son tan importantes como el modelo.

---

[← Volver al Índice de Documentación Técnica](README.md)

