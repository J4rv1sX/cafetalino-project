# Proyecto Cafetalino en LaTeX

Fuente del informe del Trabajo de Innovación (UNIR). Contiene los cuatro
capítulos redactados hasta la segunda entrega, la bibliografía y los cinco
anexos.

## Estructura

```
main.tex                         → documento maestro (datos del trabajo y orden de los archivos)
preambulo.tex                    → paquetes, márgenes, estilos de título, encabezado, bibliografía
portada.tex                      → portada institucional UNIR
capitulos/01-introduccion.tex
capitulos/02-objetivos.tex
capitulos/03-desarrollo-conceptual.tex
capitulos/04-metodologia.tex
anexos/a-entrevista-gerente.tex
anexos/b-entrevista-operador.tex
anexos/c-encuesta-clientes.tex
anexos/d-diagramas-de-los-prototipos.tex
anexos/e-capturas-de-jira.tex
bibliografia/referencias.bib     → las 27 referencias del documento
imagenes/                        → logo, figuras del .docx y gráficos de la encuesta
```

## Cómo compilar en Overleaf

1. Sube el .zip completo (*New Project → Upload Project*).
2. En *Menu → Settings*: **Compiler pdfLaTeX**, **TeX Live 2023 o superior**.
3. Pulsa *Recompile* dos veces (la secuencia es pdflatex → biber → pdflatex → pdflatex).

El preámbulo trae `\overleaftrue`, que activa `biblatex` con estilo **APA 7**
(biber). Para compilar en una instalación local sin `biblatex-apa`, cambia esa
línea a `\overleaffalse` y el proyecto usa `natbib` + `apalike`.

Todo lo que genera LaTeX está en `.gitignore`, `main.pdf` incluido: el PDF es
salida local, no se versiona.

## Formato que reproduce la plantilla

| Elemento | En `plantilla.docx` | En LaTeX |
|---|---|---|
| Página | A4, márgenes 2,5 / 2,5 / 3 / 2 cm | `geometry`, iguales |
| Interlineado | 1,5, texto justificado | `\onehalfspacing` |
| Cuerpo | Calibri 12 pt | `carlito` 12 pt (libre, misma métrica) |
| Títulos | numerados, azul `#0098CD` | `titlesec` + color `unirazul` |
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

- Los capítulos 5, 6 y 7 (Implementación, Validación y Conclusiones). En
  `main.tex` hay líneas `\input` comentadas listas para añadirlos.
- **Extensión.** `docs/instrucciones.md` fija un máximo de 30 páginas sin contar
  portada, índices ni anexos. Los capítulos 1–4 ocupan hoy 35, así que hay que
  recortar antes de la entrega final, que además sumará tres capítulos más.
- Dos párrafos se salen del margen unos 7 pt por la palabra "Mantenimiento" en
  celdas estrechas de tabla.
