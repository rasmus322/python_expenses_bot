import matplotlib
import matplotlib.pyplot as pyplot
import io
from datetime import date
from constants import CATEGORY_COLORS, DEFAULT_COLOR

matplotlib.use("Agg")

def get_chart_title(min_date: date, max_date: date) -> str:
    if min_date == max_date:
        return f"График расходов за { min_date.strftime('%d.%m.%Y') }"
    return f"График расходов за { min_date.strftime('%d.%m.%Y') } - { max_date.strftime('%d.%m.%Y') }"

def create_pie_chart(stats: dict, min_date: date, max_date: date) -> io.BytesIO:
    categories = list(stats.keys())
    amounts = list(stats.values())
    colors = [CATEGORY_COLORS.get(category, DEFAULT_COLOR) for category in categories]

    pyplot.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif']
    pyplot.rcParams['axes.unicode_minus'] = False

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

    ax.set_title(get_chart_title(min_date, max_date), fontsize=16, fontweight='bold', pad=20)

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

def create_bar_chart(stats: dict, min_date: date, max_date: date) -> io.BytesIO:
    categories = list(stats.keys())
    amounts = list(stats.values())
    colors = [CATEGORY_COLORS.get(category, DEFAULT_COLOR) for category in categories]

    pyplot.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif']
    pyplot.rcParams['axes.unicode_minus'] = False
    
    fig, ax = pyplot.subplots(figsize=(10,6))
    
    bars = ax.bar(
        categories,
        amounts,
        color=colors[:len(categories)],
        edgecolor='white',
        linewidth=1.5
    )

    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.0f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha='center',
            va='bottom',
            fontsize=11,
            fontweight='bold'
        )

    ax.set_title(get_chart_title(min_date, max_date), fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel("Сумма", fontsize=12)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    pyplot.xticks(rotation=45, ha='right', fontsize=11)

    buf = io.BytesIO()
    pyplot.savefig(buf, format='png', bbox_inches='tight', dpi=120)
    buf.seek(0)

    pyplot.close(fig)

    return buf