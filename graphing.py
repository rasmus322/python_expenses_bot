import matplotlib
import matplotlib.pyplot as pyplot
import io

matplotlib.use("Agg")

def create_expenses_pie_chart(stats: dict) -> io.BytesIO:
    if not stats:
        return None

    categories = list(stats.keys())
    amounts = list(stats.values())

    colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#C2C2F0', '#FFB3E6', '#FFD700']

    pyplot.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif']
    pyplot.rcParams['axes.unicode_minus'] = False

    fig, ax = pyplot.subplots(figsize=(8,8))

    wedges, texts, autotexts = ax.pie(
        amounts,
        labels=categories,
        autopct='%1.1f%%',
        colors=colors[:len(categories)],
        startangle=140,
        pctdistance=0.85,
        wedgeprops=dict(width=0.5, edgecolor='w')
    )

    pyplot.setp(autotexts, size=11, weight="bold", color="white")
    pyplot.setp(texts, size=12)

    ax.set_title("График расходов", fontsize=16, fontweight='bold', pad=20)

    buf = io.BytesIO()
    pyplot.savefig(buf, format='png', bbox_inches='tight', dpi=120)
    buf.seek(0)

    pyplot.close(fig)

    return buf