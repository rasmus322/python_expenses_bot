import matplotlib
import matplotlib.pyplot as pyplot
import io
from datetime import date

matplotlib.use("Agg")

CATEGORY_COLORS = {
    "Продукты": "#2ECC71",
    "Кафе": "#E67E22",
    "Транспорт": "#3498DB",
    "Жильё": "#95A5A6",
    "Постоянные расходы": "#7F8C8D",
    "Развлечения": "#9B59B6",
    "Хобби": "#1ABC9C",
    "Техника": "#34495E",
    "Здоровье": "#27AE60",
    "Красота": "#FF69B4",
    "Одежда": "#E91E63",
    "Путешествия": "#00BCD4",
    "Вредные привычки": "#E74C3C",
    "Дом и быт": "#8D6E63",
    "Прочее": "#BDC3C7"
}

DEFAULT_COLOR = "#95A5A6" 

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
    colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#C2C2F0', '#FFB3E6', '#FFD700']

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