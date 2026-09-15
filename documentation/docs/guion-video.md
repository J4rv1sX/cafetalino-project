---
title: Guion de la presentación en vídeo — Trabajo de Innovación
proyecto: Cerebro Predictivo y Optimización Logística para Máquinas Expendedoras de Bebidas
duracion: 10 minutos
estado: borrador — pendiente de imágenes, capturas y ensayo cronometrado
---

# Guion de la presentación en vídeo

Borrador completo para montar las diapositivas sobre
`plantilla_video.ppt` y grabar el vídeo de la entrega final.

## Cómo usar este documento

Cada integrante graba **su propio vídeo**: el documento se evalúa en conjunto,
pero la exposición se califica individualmente (`guia.md:42`). El guion está
escrito en primera persona del plural para que sirva a los cuatro sin
reescribirlo; solo hay que sustituir `[TU NOMBRE]` en la portada.

**El guion no se lee.** La rúbrica reserva su calificación más baja para quien
«lee el contenido de un papel», y es el indicador de mayor peso del bloque de
exposición: 20 % de la nota final (`rubrica.md:177-191`). Sirve para
interiorizar el hilo y cronometrar; frente a la cámara se habla con las
diapositivas como apoyo.

### Requisitos que fija el curso

| Requisito | Valor | Fuente |
|---|---|---|
| Duración | 10 minutos | `guia.md:168` |
| Formato | preferentemente MP4 | `guia.md:168` |
| Cámara | aparecer hablando a cámara, con diapositivas | `guia.md:168` |
| Herramientas sugeridas | Loom, OBS o similar (versión gratuita) | `guia.md:168` |
| Peso | 30 % de la nota de la asignatura | `guia.md:178` |
| Demo de funcionamiento | no la exige ningún documento del curso | — |

### Presupuesto de tiempo

16 diapositivas sobre las 7 secciones de la plantilla. El guion son **1 564
palabras**, que a un ritmo de 160 palabras por minuto ocupan **9:49** y dejan
unos diez segundos de margen para las transiciones. Los tiempos de cada
diapositiva se calcularon con ese ritmo a partir de su recuento real de
palabras, así que sirven como referencia de ensayo.

El total no debe superar los 10:00: ajustarse al tiempo es un criterio explícito
de la rúbrica. Si al cronometrar vas largo, las diapositivas 6 y 8 son las más
comprimibles; las 13 y 14 no deben tocarse, porque son las que la rúbrica lee
como validación.

### Convenciones de las diapositivas

- Máximo **7 palabras por viñeta** y **5 viñetas por diapositiva**. La guía pide
  expresamente «no abusar del texto» (`guia.md:174`).
- Las cifras van grandes y solas; el detalle se dice, no se escribe.
- Los datos de Cafetalino están **bajo NDA**: en las capturas hay que anonimizar
  los nombres de ubicación y consignarlo al pie.
- Ninguna cifra de este guion es nueva: todas proceden de `../capitulos/*.tex` o de
  `backend/docs/CONSUMPTION_MODEL.md`.

### Estructura

Las columnas «Sección» son las siete que impone `plantilla_video.ppt`.

| # | Sección de la plantilla | Diapositiva | Entra |
|---|---|---|---|
| 1 | Portada | Título, autor, UNIR | 00:00 |
| 2 | Índice | Las cinco entradas | 00:27 |
| 3 | Introducción | El problema | 00:46 |
| 4 | Introducción | La evidencia | 01:39 |
| 5 | Introducción | La propuesta | 02:22 |
| 6 | Introducción | Trabajos relacionados | 02:58 |
| 7 | Objetivos | General y específicos | 03:36 |
| 8 | Objetivos | Metodología | 04:15 |
| 9 | Desarrollo de la propuesta | Vista general del sistema | 04:53 |
| 10 | Desarrollo de la propuesta | Datos y modelo | 05:27 |
| 11 | Desarrollo de la propuesta | Enrutamiento dinámico | 06:22 |
| 12 | Desarrollo de la propuesta | El sistema en uso | 06:54 |
| 13 | Evaluación | Desempeño medido | 07:33 |
| 14 | Evaluación | Cómo se decidirá si funciona | 08:22 |
| 15 | Conclusiones | Alcance y objetivos | 09:04 |
| 16 | Conclusiones | Trabajo futuro y cierre | 09:32 |

---

## Diapositiva 1 — Portada  [00:00 → 00:27] (27 s)

**En pantalla**
- Cerebro Predictivo y Optimización Logística para Máquinas Expendedoras de Bebidas
- Trabajo de Innovación — Maestría en Inteligencia Artificial
- `[TU NOMBRE]`
- Universidad Internacional de La Rioja

**Visual** — portada de la plantilla, sin añadidos. Es el único momento en el
que conviene que la cámara ocupe un espacio visible.

**Guion**

> Buenos días. Presento el trabajo de innovación «Cerebro predictivo y
> optimización logística para máquinas expendedoras de bebidas», de la Maestría
> en Inteligencia Artificial de la Universidad Internacional de La Rioja. Es un
> trabajo de equipo sobre un caso real: Cafetalino, la empresa que opera la red
> de máquinas de café de Sucre, en Bolivia. En diez minutos voy a contarles qué
> problema encontramos, qué construimos y hasta dónde podemos afirmar hoy que
> funciona.

**Notas** — la última frase anticipa la honestidad del cierre. Evita que el
tribunal espere resultados operativos que todavía no existen.

---

## Diapositiva 2 — Índice  [00:27 → 00:46] (19 s)

**En pantalla**
- Introducción
- Objetivos
- Desarrollo de la propuesta
- Evaluación
- Conclusiones

**Visual** — la diapositiva de índice de la plantilla, tal cual.

**Guion**

> El recorrido es el siguiente: primero el problema y la propuesta, frente a lo
> que ya se ha hecho en este campo; después los objetivos y la metodología; a
> continuación el sistema que construimos; luego cómo lo evaluamos; y por último
> las conclusiones y las líneas que el trabajo deja abiertas.

---

## Diapositiva 3 — El problema  [00:46 → 01:39] (53 s)

**En pantalla**
- Cafetalino · Sucre · desde 2018
- 17 ubicaciones activas
- Reabastecimiento por calendario fijo
- Doble coste: visitas inútiles y máquinas vacías

**Visual** — [IMAGEN: mapa de Sucre con los 17 puntos] o fotografía de una
máquina. Nada de texto adicional.

**Guion**

> Cafetalino nació en 2018 y es pionera del autoservicio de bebidas calientes en
> Sucre. Hoy opera diecisiete ubicaciones activas: el aeropuerto, hospitales,
> oficinas bancarias, centros educativos, mercados y centros comerciales. El
> reabastecimiento se organiza con rutas fijas y calendarios periódicos, apoyado
> en la experiencia del operador, y en ocasiones de forma reactiva, cuando un
> cliente reporta que una máquina falló.
>
> Ese esquema produce un problema con dos caras. Por un lado, el operador visita
> máquinas que todavía tienen insumos: gasta tiempo, combustible y jornada en
> recorridos que no generan valor. Por otro, hay máquinas que se agotan antes de
> la siguiente visita programada, interrumpen el servicio y dejan al cliente
> frente a una máquina vacía. Y la empresa no dispone de ningún indicador que le
> permita saber, antes de salir, cuál de las dos cosas va a ocurrir en cada
> punto.

**Notas** — el enunciado formal del problema está en
`../capitulos/01-introduccion.tex:17`. Si preguntan, la frase clave es «impacto
negativo doble».

---

## Diapositiva 4 — La evidencia  [01:39 → 02:22] (43 s)

**En pantalla**
- 1 de cada 10 visitas, innecesaria
- ~10 modificaciones de ruta al año
- Encuesta: 254 clientes en 15 máquinas
- 63,7 % tarda una semana o más en volver

**Visual** — las cuatro cifras, grandes. Opcionalmente reutilizar uno de los gráficos
de la encuesta (`../imagenes/grafico1-5.png`).

**Guion**

> No partimos de una intuición. Entrevistamos al gerente, que cuantificó el
> problema: una de cada diez visitas se hace a una máquina que no necesitaba
> recarga, y hay unos diez desvíos extraordinarios de ruta al año. Y encuestamos
> a doscientos cincuenta y cuatro clientes en quince máquinas.
>
> El ochenta y nueve por ciento son usuarios semanales. Entre quienes sufrieron
> un fallo, el noventa y uno reportó decepción y el setenta y ocho, frustración.
> Pero el dato que convierte esto en un problema económico es otro: casi el
> sesenta y cuatro por ciento tardó una semana o más en volver a usar el
> servicio. Cada máquina vacía no cuesta un reembolso; cuesta días de ventas.

**Notas** — la empresa ya intentó resolverlo con sensores, solo para vasos, y el
piloto fracasó por problemas de conectividad y por el presupuesto de ampliarlo.
Ese antecedente justifica toda nuestra restricción de diseño.

---

## Diapositiva 5 — La propuesta  [02:22 → 02:58] (36 s)

**En pantalla**
- Predecir el consumo con el histórico existente
- Decidir qué máquinas atender hoy
- Ordenar la visita sobre tiempos reales
- **Sin instrumentar las máquinas**

**Visual** — [IMAGEN: flujo de tres bloques → Predicción · Decisión · Ruta]

**Guion**

> Nuestra propuesta es un sistema de apoyo a la decisión con tres piezas
> encadenadas. Anticipa, para cada una de las diecisiete ubicaciones, cuánto se
> habrá consumido en una fecha dada. Convierte esa predicción en existencias
> restantes, que es la forma en que el operador decide. Y con las máquinas que
> él selecciona, construye el recorrido del día sobre tiempos reales.
>
> La restricción que define el trabajo es que todo esto se hace sin instalar un
> solo sensor: la única materia prima es el registro de recargas que la empresa
> ya lleva desde 2018 por obligación contable.

**Notas** — «sin instrumentar» es la frase que hay que dejar grabada. Es la
aportación del trabajo y el eje de todo lo que viene después.

---

## Diapositiva 6 — Trabajos relacionados  [02:58 → 03:36] (38 s)

**En pantalla**
- Mehmood (2023): predice, no despacha
- Aguas (2025): inventario sin enrutamiento
- Puma (2025): exige conectividad permanente
- Sensify, Azkoyen: dependen de IoT
- **Brecha: sin telemetría y de extremo a extremo**

**Visual** — tabla comparativa reducida a 4 filas + la nuestra destacada.

**Guion**

> El estado del arte muestra dos patrones. El primero: los trabajos que predicen
> demanda en expendedoras se detienen ahí. Mehmood y colaboradores comparan
> algoritmos supervisados pero no acoplan el resultado al despacho; Aguas y
> Echeverría predicen quiebres de stock dejando el enrutamiento al margen.
>
> El segundo es la dependencia de telemetría: Puma y colaboradores exigen datos
> en tiempo real, y las soluciones comerciales como Sensify o Azkoyen se apoyan
> en sensores conectados. Esa condición la cumple una red grande, no una pequeña
> empresa local. Nuestra brecha es doble: predecir sin hardware, y unir
> predicción y ruta en un mismo flujo.

---

## Diapositiva 7 — Objetivos  [03:36 → 04:15] (39 s)

**En pantalla**
- **General:** anticipar la demanda y planificar rutas dinámicas
- 1. Caracterizar los patrones históricos
- 2. Módulo de predicción, sin hardware adicional
- 3. Módulo de rutas dinámicas
- 4. Interfaz web de apoyo a la decisión

**Visual** — los cuatro específicos con un icono cada uno.

**Guion**

> El objetivo general fue desarrollar un sistema basado en inteligencia
> artificial para mejorar la gestión del reabastecimiento de la red de
> Cafetalino, mediante la predicción de la demanda y la planificación dinámica
> de rutas, con el fin de sostener la continuidad del servicio y reducir los
> costos logísticos.
>
> Lo desagregamos en cuatro específicos. Caracterizar los patrones históricos de
> consumo entre 2018 y 2026. Desarrollar un módulo de estimación mediante
> aprendizaje automático, con una condición explícita: sin hardware adicional.
> Desarrollar un módulo de rutas construidas sobre la demanda proyectada. Y una
> interfaz web concebida como apoyo a la decisión, no como sustituto de ella.

**Notas** — no leer el objetivo general completo: en el documento son sesenta
palabras. Lo que se dice aquí es su versión hablada.

---

## Diapositiva 8 — Metodología  [04:15 → 04:53] (38 s)

**En pantalla**
- Design Thinking: 5 fases, 4 alternativas evaluadas
- Scrum: 4 sprints de 2 semanas
- 20 historias · 5 épicas · 81 puntos
- LEAN: Construir – Medir – Aprender

**Visual** — [CAPTURA: tablero de Jira, del Anexo E] junto a la línea de tiempo
de los 4 sprints.

**Guion**

> Seguimos tres marcos con funciones distintas. Design Thinking ordenó el
> descubrimiento: las entrevistas y la encuesta son la fase de empatizar, y en
> la de idear evaluamos cuatro alternativas con criterios ponderados. Ganó el
> sistema predictivo con enrutamiento, con ocho sobre diez; la visión artificial
> se descartó al comprobar que los contenedores de insumos son opacos.
>
> Scrum estructuró la construcción: cuatro sprints de dos semanas, veinte
> historias en cinco épicas, ochenta y un puntos estimados con Fibonacci y
> gestionados en Jira. Y LEAN aportó el criterio de decisión, con cuatro
> hipótesis de valor sometidas al ciclo construir, medir y aprender.

---

## Diapositiva 9 — Vista general del sistema  [04:53 → 05:27] (34 s)

**En pantalla**
- Datos: SQLite + pandas
- Modelos: scikit-learn
- Rutas: Distance Matrix + OR-Tools
- API: FastAPI + Pydantic
- Web: React + TypeScript

**Visual** — [IMAGEN: diagrama de arquitectura de 5 capas, con los dos endpoints
marcados]

**Guion**

> La arquitectura tiene cinco capas y es deliberadamente conservadora. Los datos
> viven en SQLite, porque unos miles de registros no justifican un gestor
> servidor. Los modelos son de scikit-learn. La decisión logística combina la
> matriz de tiempos de Google con el resolutor OR-Tools. El servicio es FastAPI,
> y expone exactamente dos operaciones: el pronóstico de todas las máquinas para
> una fecha, y el recorrido ordenado. La presentación es React con TypeScript.
> Todo es software libre salvo la cartografía, confinada a un único módulo para
> poder sustituirla sin tocar el resto.

---

## Diapositiva 10 — Datos y modelo  [05:27 → 06:22] (55 s)

**En pantalla**
- 3 646 registros · 2018–2026
- 36 identificadores → **17 ubicaciones** por coordenada
- 2 439 observaciones de entrenamiento
- 5 modelos · HistGradientBoosting · 24 variables
- Descartadas por fuga: agua restante y vasos

**Visual** — embudo de depuración de los datos: 3 646 → 2 467 → 2 439.

**Guion**

> El histórico tiene tres mil seiscientos registros entre 2018 y 2026. Nos
> quedamos con los de máquinas activas y descartamos las primeras visitas de
> cada ubicación, que no tienen historial previo: quedan dos mil cuatrocientas
> treinta y nueve observaciones.
>
> La decisión de diseño más importante fue cómo identificar una máquina. El
> archivo tiene treinta y seis identificadores de equipo, pero solo diecisiete
> pares de coordenadas, porque los equipos rotan entre emplazamientos. Como lo
> que determina el consumo es el lugar y no el número de serie, consolidamos por
> coordenada.
>
> Entrenamos cinco modelos independientes, uno por insumo, con potenciación de
> gradiente y veinticuatro variables. Y descartamos dos columnas que parecían
> informativas —el porcentaje de agua restante y el conteo de vasos— porque se
> miden durante la misma visita que queremos anticipar. Usarlas exigiría estar
> ya frente a la máquina, que es justo lo que el sistema evita.

**Notas** — si preguntan por redes neuronales: se evaluaron y se descartaron
explícitamente; con 2 400 observaciones no superan a los métodos de conjunto
sobre árboles y solo añaden complejidad de infraestructura.

---

## Diapositiva 11 — Enrutamiento dinámico  [06:22 → 06:54] (32 s)

**En pantalla**
- Tiempos de conducción reales, no línea recta
- Origen: posición actual del operador
- +25 min de servicio por máquina
- Replanificable a mitad de jornada

**Visual** — [CAPTURA: mapa con la polilínea de la ruta]

**Guion**

> El recorrido usa tiempos de conducción reales, lo que importa en una ciudad de
> topografía irregular como Sucre, y se plantea como un problema del agente
> viajero con retorno al origen. Dos adaptaciones lo acercan a la operación
> real: el punto de partida no es un almacén sino la ubicación actual del
> operador, así que puede replanificar desde donde esté; y a cada parada le
> sumamos veinticinco minutos de servicio, que es lo que toma la recarga. Sin
> ese término la jornada estimada sería sistemáticamente optimista.

---

## Diapositiva 12 — El sistema en uso  [06:54 → 07:33] (39 s)

**En pantalla**
- Tres columnas: pronóstico → selección → ruta
- Ordenadas por urgencia
- Cada tarjeta muestra **el intervalo**, no solo la estimación

**Visual** — [CAPTURA 1: lista de pronóstico con intervalos] · [CAPTURA 2:
tarjetas arrastradas a «máquinas a recargar»] · [CAPTURA 3: mapa con la ruta y
la duración total]. Pie: «Nombres de ubicación anonimizados (NDA)».

**Guion**

> La interfaz reproduce la secuencia de la decisión del operador en tres
> columnas. A la izquierda, las diecisiete máquinas con su pronóstico, ordenadas
> por días desde la última recarga, con las más rezagadas arriba. El operador
> arrastra al centro las que decide atender, y a la derecha aparece el mapa con
> el recorrido y la duración estimada.
>
> Quiero destacar una decisión de diseño: cada tarjeta muestra siempre el
> intervalo, no solo la estimación puntual. Ocultar la incertidumbre habría dado
> una falsa sensación de precisión; mostrarla permite al operador reservar su
> criterio cuando la banda es ancha. El sistema informa la decisión, no la
> sustituye.

---

## Diapositiva 13 — Desempeño medido  [07:33 → 08:22] (49 s)

**En pantalla**
- Validación cruzada de 5 pliegues
- R² entre 0,274 y 0,371
- Cobertura de intervalos: 83 %
- Meta R² ≥ 0,30: **cumplimiento parcial**

**Visual** — [IMAGEN: tabla de desempeño o barras de MAE por insumo]. Fuente:
tabla `tab:desempeno-de-los-modelos` del capítulo 5.

**Guion**

> Evaluamos con validación cruzada de cinco pliegues. El error absoluto medio es
> de mil setecientos mililitros en agua, nueve vasos y entre veintidós y noventa
> gramos en las mezclas. El coeficiente de determinación queda entre cero coma
> veintisiete y cero coma treinta y siete.
>
> Nos habíamos comprometido con cero coma treinta en los cinco insumos. Se
> alcanza en tres; el chocolate queda marginalmente por debajo. Lo declaramos
> como cumplimiento parcial en lugar de ajustar el umbral después de conocer el
> resultado, porque eso privaría al criterio de su función. La causa no es
> algorítmica sino informativa: el histórico registra cuánto se repuso, pero no
> la afluencia que lo determina. Frente a la línea base real, que es el promedio
> histórico de cada máquina, el error es menor en los cinco.

**Notas** — si hay tiempo o preguntas, dos detalles que refuerzan el rigor:
(a) las bandas nominales del 80 % tenían una cobertura empírica real del 70 %, y
las ensanchamos a propósito hasta alcanzar el 83 % medido; (b) documentamos tres
ensayos que no funcionaron y no se incorporaron.

---

## Diapositiva 14 — Cómo se decidirá si funciona  [08:22 → 09:04] (42 s)

**En pantalla**
- Piloto de 8 semanas, en paralelo
- Cada máquina es su propio control
- Validar: exactitud ≥ 85 %, visitas inútiles ≤ 5 %
- **Pivotar si la exactitud cae por debajo de 75 %**

**Visual** — [IMAGEN: los tres desenlaces — perseverar, ajustar, pivotar]

**Guion**

> Eso dice que el modelo aprende algo aprovechable. La pregunta más exigente
> —si se traduce en menos visitas inútiles y menos máquinas vacías— la responde
> un piloto de ocho semanas que diseñamos, pero que excede el horizonte de este
> trabajo. Opera en paralelo al procedimiento actual y cada máquina es su propio
> control.
>
> El criterio está fijado por anticipado: exactitud del ochenta y cinco por
> ciento y visitas innecesarias por debajo del cinco; por debajo del setenta y
> cinco habría que pivotar hacia la captura directa de datos. Enunciar de
> antemano qué resultado nos obligaría a abandonar el enfoque es lo que hace de
> esto una validación y no una justificación.

**Notas** — es la diapositiva más delicada. Hay que decir con todas las letras
que el piloto **no se ejecutó**. Intentar insinuar lo contrario sería lo único
que podría hundir la evaluación.

---

## Diapositiva 15 — Conclusiones  [09:04 → 09:32] (28 s)

**En pantalla**
- Los 4 objetivos específicos, alcanzados
- Aportación: el dato que ya existe basta
- Límites: R² 0,27–0,37 · 17 ubicaciones · piloto pendiente

**Visual** — tabla de contraste objetivo → resultado, reducida a cuatro filas.

**Guion**

> Los cuatro objetivos específicos se alcanzaron, cada uno con su evidencia
> referenciada. La aportación no está en los algoritmos, que son estándar, sino
> en mostrar que un registro administrativo que la empresa ya lleva contiene
> señal suficiente para decidir la logística sin instrumentar las máquinas. Los
> límites son claros: buena parte de la variabilidad queda sin explicar, la red
> es pequeña, el recorrido no es un óptimo demostrado y la prueba operativa
> sigue pendiente.

---

## Diapositiva 16 — Trabajo futuro  [09:32 → 09:49] (17 s)

**En pantalla**
- Clima, calendario y eventos como variables
- Instrumentación selectiva híbrida
- Transferible a otras redes de reposición
- `www.unir.net`

**Visual** — cierre de la plantilla con el logo UNIR.

**Guion**

> El trabajo deja cuatro líneas abiertas: incorporar clima, calendario y eventos
> para superar el techo informativo; instrumentar solo las máquinas de mayor
> rotación y corregir con ellas el resto; extender el enfoque a otras redes de
> reposición periódica; y escalar a varios vehículos. Muchas gracias.

---

## Activos pendientes de producción

Para montar las diapositivas hay que generar estos elementos. Ninguno es
bloqueante para revisar el guion.

| Diapositiva | Activo | Notas |
|---|---|---|
| 3 | Mapa de Sucre con los 17 puntos | Las coordenadas están en `backend/data/consumo_insumos.csv` |
| 4 | Cifras de la encuesta | Se pueden reutilizar `../imagenes/grafico1-5.png` |
| 5 | Diagrama de flujo de 3 bloques | Predicción → Decisión → Ruta |
| 6 | Tabla comparativa del estado del arte | Reducir la del capítulo 3 a 5 filas |
| 8 | Captura del tablero de Jira | Ya existen en el Anexo E |
| 9 | Diagrama de arquitectura de 5 capas | Tabla del capítulo 5 como base |
| 10 | Embudo 3 646 → 2 467 → 2 439 | — |
| 11, 12 | 3 capturas de la interfaz | **Anonimizar nombres de ubicación (NDA)** |
| 13 | Tabla o gráfico de desempeño | Estilo de `../imagenes/regenerar-graficos.py` |
| 14 | Esquema perseverar / ajustar / pivotar | — |

### Clip de demostración (opcional)

Un clip de 30-40 segundos en la diapositiva 12 haría más concreta la propuesta,
pero **grabado aparte y montado**, nunca en vivo durante la exposición: no
conviene arriesgar minutos de los diez disponibles. Flujo a capturar: elegir
fecha → «Ver consumos» → arrastrar 4 o 5 máquinas → ajustar el marcador de
posición → «Calcular ruta».

### Reconstrucción del entorno para capturar

`backend/data/models/` y `backend/data/cafetalino.db` son generados y están
gitignored, así que hoy no existen en el repositorio. Desde WSL2:

```bash
cd backend
uv sync && ./regen_cuda_env.sh
uv run --env-file .env scripts/load_consumption.py
uv run --env-file .env scripts/train_consumption.py   # ~5-8 min
uv run --env-file .env uvicorn main:app --reload      # :8000
```

```bash
cd frontend
npm install && npm run dev                            # :5173
```

Hacen falta **dos claves de Google Maps distintas**, ninguna de las cuales está
en el repositorio:

- `GOOGLE_MAPS_API_KEY` en `backend/.env.local` — Distance Matrix, servidor.
- `VITE_GOOGLE_MAPS_API_KEY` en `frontend/.env.local` — mapa y rutas, cliente.

Sin ellas, las columnas de pronóstico y selección funcionan igual —son las
capturas 1 y 2— y solo el mapa muestra un aviso de configuración. El puerto de
Vite debe ser 5173: es el único que admite el CORS del backend.

## Antes de grabar

1. Leer el guion en voz alta con cronómetro y comprobar el ritmo real: los
   tiempos asumen 160 palabras por minuto.
2. Comprobar que ninguna diapositiva supera las 5 viñetas.
3. Verificar que las capturas no muestran nombres reales de ubicación.
4. Encuadre con la cámara visible y las diapositivas legibles; probar el audio
   con una grabación corta antes de la toma buena.
5. Exportar en MP4.
