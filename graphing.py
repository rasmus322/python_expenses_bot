import matplotlib
import matplotlib.pyplot as pyplot
import io
from datetime import date

matplotlib.use("Agg")

def create_expenses_pie_chart(stats: dict, min_date: date, max_date: date) -> io.BytesIO:
    if not stats:
        return None

    categories = list(stats.keys())
    amounts = list(stats.values())
    title = ""

    colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#C2C2F0', '#FFB3E6', '#FFD700']

    pyplot.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif']
    pyplot.rcParams['axes.unicode_minus'] = False

    if min_date == max_date:
        title = f"График расходов за { min_date.strftime('%d.%m.%Y') }"
    else:
        title = f"График расходов за { min_date.strftime('%d.%m.%Y') } - { max_date.strftime('%d.%m.%Y') }"

    fig, ax = pyplot.subplots(figsize=(10,8))

    _, _, autotexts = ax.pie(
        amounts,
        labels=categories,
        autopct='%1.1f%%',
        colors=colors[:len(categories)],
        startangle=140,
        pctdistance=0.85,
        wedgeprops=dict(width=0.5, edgecolor='w')
    )

    pyplot.setp(autotexts, size=11, weight="bold", color="white")

    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)

    ax.legend(
        categories,
        loc='center left',
        bbox_to_anchor=(1, 0.5),
        fontsize=12,
        frameon=True,
        shadow=True
    )

    buf = io.BytesIO()
    pyplot.savefig(buf, format='png', bbox_inches='tight', dpi=120)
    buf.seek(0)

    pyplot.close(fig)

    return buf