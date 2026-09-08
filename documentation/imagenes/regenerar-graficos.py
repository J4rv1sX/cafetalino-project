"""Regenera los 5 gráficos incrustados en el .docx (charts1-5.xml) como PNG."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

OUT = 'proyecto-latex/imagenes'
os.makedirs(OUT, exist_ok=True)

AZUL = ['#0098CD', '#0B6E93', '#66C6E6', '#1B3B54', '#A9DCF0', '#4FA3C7', '#D6EEF8']

pies = [
    ('grafico1', ['No responde', 'Menos de 1 vez/mes', '1 vez/mes', '2 veces/mes',
                  '1 vez/semana', '2 veces/semana', 'Más de 2 veces/semana'],
     [0.39, 0.79, 1.18, 8.27, 28.74, 37.40, 23.23]),
    ('grafico2', ['No responde', 'Muy malo', 'Malo', 'Regular', 'Bueno', 'Muy bueno'],
     [0.79, 0.39, 9.06, 5.91, 46.06, 37.80]),
    ('grafico3', ['No responde', 'No recibió el producto',
                  'Calidad del producto no esperada', 'Nunca me ocurrió'],
     [0.79, 6.30, 2.76, 90.16]),
]

for name, labels, vals in pies:
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200)
    wedges, _, autotexts = ax.pie(
        vals, colors=[AZUL[i % len(AZUL)] for i in range(len(vals))],
        autopct=lambda p: f'{p:.1f}%' if p >= 2 else '',
        startangle=90, counterclock=False,
        wedgeprops={'edgecolor': 'white', 'linewidth': 1.2},
        textprops={'fontsize': 8, 'weight': 'bold'})
    # texto oscuro sobre porciones claras, blanco sobre las oscuras
    for w, t in zip(wedges, autotexts):
        r, g, b = matplotlib.colors.to_rgb(w.get_facecolor())
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        t.set_color('#123044' if lum > 0.6 else 'white')
    ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(1.0, 0.5),
              fontsize=8, frameon=False)
    ax.set_aspect('equal')
    fig.tight_layout()
    fig.savefig(f'{OUT}/{name}.png', bbox_inches='tight', transparent=False,
                facecolor='white')
    plt.close(fig)

bars = [
    ('grafico4', ['No responde', 'Decepción', 'Frustración', 'Impotencia',
                  'Pérdida/Robo', 'Desconfianza', 'Confianza'],
     [0.0, 91.30, 78.26, 26.09, 4.35, 43.48, 56.52]),
    ('grafico5', ['No responde', 'Disculpa', 'Reembolso', 'Compensación'],
     [4.26, 100.0, 100.0, 64.71]),
]

for name, labels, vals in bars:
    fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=200)
    b = ax.bar(labels, vals, color='#0098CD', width=0.6)
    ax.bar_label(b, fmt='%.1f%%', fontsize=8, padding=2)
    ax.set_ylim(0, 112)
    ax.set_ylabel('% de clientes afectados', fontsize=9)
    ax.tick_params(axis='x', labelsize=8, rotation=20)
    ax.tick_params(axis='y', labelsize=8)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.grid(axis='y', color='#DDDDDD', linewidth=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(f'{OUT}/{name}.png', facecolor='white')
    plt.close(fig)

print('gráficos generados')
