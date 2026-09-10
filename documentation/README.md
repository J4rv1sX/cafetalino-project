# Proyecto Cafetalino en LaTeX

Fuente del informe del Trabajo de Innovación (UNIR). Contiene los siete
capítulos del cuerpo, la bibliografía y los cinco anexos.

## Estructura

```
main.tex                         → documento maestro (datos del trabajo y orden de los archivos)
preambulo.tex                    → paquetes, márgenes, estilos de título, encabezado, bibliografía
portada.tex                      → portada institucional UNIR
capitulos/01-introduccion.tex
capitulos/02-objetivos.tex
capitulos/03-desarrollo-conceptual.tex
capitulos/04-metodologia.tex
capitulos/05-implementacion.tex
capitulos/06-validacion.tex
capitulos/07-conclusiones.tex
anexos/a-entrevista-gerente.tex
anexos/b-entrevista-operador.tex
anexos/c-encuesta-clientes.tex
anexos/d-diagramas-de-los-prototipos.tex
anexos/e-capturas-de-jira.tex
anexos/f-backlog-inicial.tex
bibliografia/referencias.bib     → las 32 referencias del documento
imagenes/                        → logo, figuras del .docx y gráficos de la encuesta
```

## Cómo compilar (compilación local)

Compilar en tu máquina con **LuaLaTeX** (requiere MiKTeX o TeX Live 2023+):

```bash
cd documentation
latexmk -lualatex -interaction=nonstopmode main.tex
```

O desde VS Code: abre `main.tex` y pulsa "Build LaTeX project" 
(configurado por defecto en `.vscode/settings.json` para usar latexmk + LuaLaTeX).

**Requisitos:**
- **Motor:** LuaLaTeX (necesario para `fontspec` y acceso a fuentes del sistema)
- **Fuentes:** Calibri y Calibri Light instaladas (vienen con Microsoft Office)
- **Paquete:** biblatex-apa (para estilo APA 7; MiKTeX lo instala automáticamente)

Todo lo que genera LaTeX está en `.gitignore`, `main.pdf` incluido: el PDF es
salida local, no se versiona.

## Formato que reproduce la plantilla

| Elemento | En `plantilla.docx` | En LaTeX |
|---|---|---|
| Página | A4, márgenes 2,5 / 2,5 / 3 / 2 cm | `geometry`, iguales |
| Interlineado | 1,5, texto justificado | `\onehalfspacing` |
| Cuerpo | Calibri 12 pt | Calibri 12 pt real (vía `fontspec` + LuaLaTeX) |
| Títulos | Calibri Light numerados, azul `#0098CD` (18/14/12 pt) | Calibri Light real (vía `fontspec`) + `titlesec` + color `unirazul` |
| Capítulos | cada uno en hoja nueva | `\sectionbreak` → `\clearpage` |
| Encabezado / pie | autor + título / número de página | `fancyhdr` |
| Tablas | título arriba, «Fuente:» debajo | `\captionof{table}` + `\fuente{}` |
| Figuras | título debajo, «Fuente:» al final | `\caption` tras `\includegraphics` + `\fuente{}` |
| Rótulos | «Tabla 1.» / «Figura 1.» | `captionsetup{labelsep=period}` |
| Citas | texto plano "(Autor, año)" | `\citep{}` / `\citet{}` con `.bib` |

## Decisiones tomadas en la conversión desde el .docx

- **Gráficos de la encuesta.** Los cinco gráficos estaban incrustados como
  objetos de gráfico de Word, no como imágenes. Se extrajeron sus datos de los
  XML internos y se regeneraron con `imagenes/regenerar-graficos.py` en la
  paleta azul de UNIR; edita el script, no los PNG.
- **Cuestionario del Anexo C.** En Word eran rejillas de casillas de
  verificación; en LaTeX se convirtieron en listas de opciones con casilla
  (`$\square$`), que se leen mejor.
- **Tablas de resultados del Anexo C.** Rehechas como `tabular` compacto,
  porque el `multicolumn` de pandoc se salía del margen.
- **Tablas de 5 o más columnas.** Cuerpo en `\small` y columnas numéricas
  ensanchadas para que quepan cabeceras como "Nivel de dificultad (SP)".
- **Numeración de tablas.** `longtable` reserva un número de tabla al abrirse
  aunque el título se ponga fuera con `\captionof`, y la numeración saltaba de
  dos en dos. El preámbulo guarda y restaura el contador alrededor de cada
  `longtable`.
- **Backlog en el Anexo F.** La tabla de las 20 historias de usuario ocupaba
  cinco páginas enteras del capítulo 4 y se trasladó al Anexo F por extensión,
  no por contenido: los anexos no computan para el límite de páginas. En el
  capítulo 4 quedan el criterio de estimación y la lectura de los resultados,
  dentro de «Artefactos», y la subsección 4.2 desapareció como tal.
- **Erratas corregidas**: "Inicio" → "Inició", "Samart vending" → "Smart
  Vending", "esta limitado" → "está limitado", `N˚` → `N.º`.

## Observaciones del tutor atendidas

`docs/observaciones-primera-entrega.md` recoge la revisión de la Entrega 1.
Estado de cada punto en la versión actual:

| Observación | Estado |
|---|---|
| Contextualizar el sector antes de presentar a Cafetalino | Ya resuelto en la reescritura: la introducción abre con cuatro párrafos de contexto |
| Aplicar un instrumento a clientes finales | Ya resuelto: encuesta a 254 clientes en 15 máquinas, con el muestreo descrito y los resultados en el Anexo C |
| Criterios de éxito cuantitativos | Ya resuelto; se añadió además la columna «Periodo de medición» |
| Reducir 1.2 a un párrafo breve | Reescrita: describe solo los cuatro capítulos existentes |
| Cada capítulo en hoja nueva | Aplicado con `\sectionbreak` |
| Rótulos «Tabla N» / «Figura N» con título y fuente, citados desde el texto | Aplicado: rótulo con punto, título de figura movido debajo de la imagen y las nueve tablas referenciadas con `\ref` |
| Simplificar la tabla del estado del arte | Rehecha con columnas técnicas: modelo, datos, horizonte, evaluación y limitación |
| Explicar datos, horizonte y métricas de los trabajos previos | Ampliados los párrafos de Mehmood, Aguas y Puma |
| Precisar variables, granularidad, horizonte, baselines y calidad del histórico | Nueva subsección 3.6.1, «Datos disponibles y diseño de la evaluación» |
| Bibliografía con correspondencia en ambos sentidos | Eliminadas Kovalyk (2022), Atlassian (2026) y Drumond (2026), que no se citaban; quedan 27 y todas están citadas |
| Numeración duplicada | Corregido el salto del contador de `longtable` |
| Primera persona plural | Queda una sola forma impersonal homogénea en todo el cuerpo |
| Dividir párrafos de más de diez o doce renglones | Divididos los dos que lo superaban en el capítulo 3 |
| Entregar en PDF | Procedimiento de entrega; Overleaf produce el PDF |

**No aplicadas, por corresponder al alcance de la Entrega 1:** «eliminen los
capítulos 4 a 8» y «el documento tiene 44 páginas». La Actividad 3 del programa
exige justamente Scrum y LEAN, es decir el capítulo 4, que se mantiene.

## Qué queda pendiente

- **Extensión.** Sigue siendo el único pendiente estructural: el documento está
  completo. `docs/instrucciones.md` fija un máximo de 30 páginas sin contar
  portada, índices ni anexos —las referencias sí cuentan—, y una primera poda
  bajó el cuerpo computable de **57 a 48 páginas** (cuerpo 1–45 más tres de
  referencias): el backlog se movió al Anexo F (−5) y se comprimió la prosa de
  los capítulos 1, 3 y 4. Reparto actual: cap. 1 → 4 pp., cap. 2 → 1, cap. 3 →
  13, cap. 4 → 8, cap. 5 → 12, cap. 6 → 4, cap. 7 → 3, referencias → 3. Para
  llegar a 30 quedan por decidir recortes de fondo: mover a anexos la
  comparativa de ideas (cap. 3) y las tablas DoR/DoD, el cronograma y el
  presupuesto (caps. 4 y 5), y condensar el capítulo 5, hoy el segundo más
  extenso.
- **Métricas del capítulo 5.** La tabla de desempeño de los modelos omite el
  coeficiente de determinación de los vasos: el valor registrado en
  `backend/docs/CONSUMPTION_MODEL.md` coincide exactamente con el del agua
  embotellada, lo que parece un error de transcripción. Hay que regenerarlo
  (`load_consumption.py` → `train_consumption.py`, en WSL2) y completar la celda.
- **Capturas de la aplicación.** El capítulo 5 ganaría con dos o tres capturas
  de la interfaz y del mapa con la ruta, en un anexo F que no computa para la
  extensión. Requieren levantar el prototipo con la clave de Google Maps.
