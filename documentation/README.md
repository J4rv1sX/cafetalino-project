# Proyecto Cafetalino en LaTeX

Conversión completa de `Proyecto_Cafetalino_-_V02.docx`: los cuatro capítulos
redactados, la bibliografía y los tres anexos.

## Estructura

```
main.tex                         → documento maestro (datos del trabajo y orden de los archivos)
preambulo.tex                    → paquetes, márgenes, estilos de título, bibliografía
portada.tex                      → portada institucional UNIR
capitulos/01-introduccion.tex
capitulos/02-objetivos.tex
capitulos/03-desarrollo-conceptual.tex
capitulos/04-metodologia.tex
anexos/a-entrevista-gerente.tex
anexos/b-entrevista-operador.tex
anexos/c-encuesta-clientes.tex
bibliografia/referencias.bib     → las 27 referencias del documento
imagenes/                        → logo, figuras del .docx y gráficos de la encuesta
vista-previa.pdf                 → PDF compilado de prueba (60 páginas)
```

## Cómo compilar en Overleaf

1. Sube el .zip completo (*New Project → Upload Project*).
2. En *Menu → Settings*: **Compiler pdfLaTeX**, **TeX Live 2023 o superior**.
3. Pulsa *Recompile* dos veces (la secuencia es pdflatex → biber → pdflatex → pdflatex).

El preámbulo trae `\overleaftrue`, que activa `biblatex` con estilo **APA 7**
(biber). Para compilar en una instalación local sin `biblatex-apa`, cambia esa
línea a `\overleaffalse` y el proyecto usa `natbib` + `apalike`.

## Correspondencia con el .docx

| Elemento | En el .docx | En LaTeX |
|---|---|---|
| Página | A4, márgenes 2,5 / 2,5 / 3 / 2 cm | `geometry`, iguales |
| Interlineado | 1,5, texto justificado | `\onehalfspacing` |
| Cuerpo | Calibri 12 pt | `carlito` 12 pt (libre, misma métrica) |
| Títulos | numerados, azul `#0098CD` | `titlesec` + color `unirazul` |
| Citas | texto plano "(Autor, año)" | `\citep{}` con `.bib` |
| Tablas y figuras | pies numerados a mano | numeración automática + índices |

## Decisiones tomadas en la conversión

- **Gráficos de la encuesta.** Los cinco gráficos del capítulo 3 estaban
  incrustados como objetos de gráfico de Word, no como imágenes. Se extrajeron
  sus datos de los XML internos del .docx y se regeneraron
  (`imagenes/grafico1-5.png`) con los mismos valores, en la paleta azul de UNIR.
- **Cuestionario del Anexo C.** En Word eran rejillas de casillas de
  verificación; en LaTeX se convirtieron en listas de opciones con casilla
  (`$\square$`), que se leen mejor.
- **Tablas de resultados del Anexo C.** Rehechas como `tabular` compacto,
  porque el `multicolumn` de pandoc se salía del margen.
- **Tablas de 5 o más columnas.** Cuerpo en `\small` y columnas numéricas
  ensanchadas para que quepan cabeceras como "Nivel de dificultad (SP)".
- **Referencias no citadas.** Kovalyk (2022), Atlassian (2026) y Drumond (2026)
  aparecen en la lista del documento original pero no se citan en el texto. Se
  incluyeron con `\nocite` en `main.tex` para reproducir la bibliografía tal
  cual; conviene revisarlo.
- **Erratas corregidas**: "Inicio" → "Inició", "Samart vending" → "Smart
  Vending", "esta limitado" → "está limitado", `N˚` → `N.º`.

## Nota sobre el PDF de muestra

`vista-previa.pdf` se compiló en un entorno sin `babel-spanish` ni `biblatex`,
así que la bibliografía aparece titulada "References" en estilo `apalike` y los
pies dicen "Tabla 1:" en vez de "Tabla 1.". En Overleaf saldrá en español y en
APA 7. Todo lo demás es lo que verás.

## Qué queda pendiente

- Los capítulos 5, 6 y 7 (Implementación, Validación y Conclusiones), que en el
  .docx todavía no estaban redactados. En `main.tex` hay líneas `\input`
  comentadas listas para añadirlos.
- Tres párrafos se salen del margen entre 3 y 20 pt (palabras largas sin punto
  de corte). En Overleaf, con la partición de palabras en español activa,
  probablemente desaparezcan solos.
- Las referencias cruzadas a los anexos siguen escritas como texto ("Anexo A").
  Las etiquetas `\label{}` ya existen si quieres cambiarlas por `\ref{}`.
