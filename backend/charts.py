import matplotlib
matplotlib.use('Agg')  # Без GUI
import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta
from crud import get_user_tasks, get_statistics
from database import Status, Priority

# Настройка для русского языка
plt.rcParams['font.family'] = 'DejaVu Sans'


def create_statistics_chart(telegram_id: int) -> io.BytesIO:
    """
    Создать дашборд со статистикой пользователя
    Возвращает BytesIO объект с PNG изображением
    """
    stats = get_statistics(telegram_id)
    tasks = get_user_tasks(telegram_id)
    
    # Создаём фигуру с несколькими графиками
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('📊 Статистика задач', fontsize=18, fontweight='bold')
    
    # ===== ГРАФИК 1: Круговая диаграмма статусов =====
    statuses = ['Выполнено', 'В процессе']
    counts = [stats['completed'], stats['pending']]
    colors = ['#4CAF50', '#FFC107']
    
    axes[0, 0].pie(
        counts,
        labels=statuses,
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        textprops={'fontsize': 11}
    )
    axes[0, 0].set_title('Статус задач', fontsize=13, fontweight='bold')
    
    # ===== ГРАФИК 2: Приоритеты =====
    high = len([t for t in tasks if t.get('priority') == Priority.HIGH.value])
    medium = len([t for t in tasks if t.get('priority') == Priority.MEDIUM.value])
    low = len([t for t in tasks if t.get('priority') == Priority.LOW.value])
    
    priorities = ['Высокий', 'Средний', 'Низкий']
    priority_counts = [high, medium, low]
    priority_colors = ['#F44336', '#FF9800', '#4CAF50']
    
    axes[0, 1].barh(priorities, priority_counts, color=priority_colors)
    axes[0, 1].set_title('Задачи по приоритету', fontsize=13, fontweight='bold')
    axes[0, 1].set_xlabel('Количество')
    
    # Добавляем значения на столбцы
    for i, v in enumerate(priority_counts):
        axes[0, 1].text(v + 0.1, i, str(v), va='center')
    
    # ===== ГРАФИК 3: Динамика по дням =====
    dates = []
    completed_per_day = []
    
    for i in range(6, -1, -1):  # Последние 7 дней
        date = datetime.now() - timedelta(days=i)
        dates.append(date.strftime('%d.%m'))
        
        count = len([
            t for t in tasks
            if t.get('completed_at') and 
            t['completed_at'].date() == date.date() and
            t['status'] == Status.COMPLETED.value
        ])
        completed_per_day.append(count)
    
    axes[1, 0].plot(dates, completed_per_day, marker='o', linewidth=2, 
                    color='#2196F3', markersize=8)
    axes[1, 0].fill_between(dates, completed_per_day, alpha=0.3, color='#2196F3')
    axes[1, 0].set_title('Выполнено задач за неделю', fontsize=13, fontweight='bold')
    axes[1, 0].set_xlabel('Дата')
    axes[1, 0].set_ylabel('Задач')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Добавляем значения на точки
    for i, v in enumerate(completed_per_day):
        if v > 0:
            axes[1, 0].text(i, v + 0.2, str(v), ha='center', fontsize=9)
    
    # ===== ГРАФИК 4: Категории (если есть) =====
    categories = {}
    for task in tasks:
        cat = task.get('category', 'Без категории') or 'Без категории'
        categories[cat] = categories.get(cat, 0) + 1
    
    if len(categories) > 0:
        cat_names = list(categories.keys())[:5]  # Топ 5
        cat_counts = [categories[name] for name in cat_names]
        
        axes[1, 1].bar(range(len(cat_names)), cat_counts, color='#9C27B0')
        axes[1, 1].set_xticks(range(len(cat_names)))
        axes[1, 1].set_xticklabels(cat_names, rotation=45, ha='right')
        axes[1, 1].set_title('Топ категории', fontsize=13, fontweight='bold')
        axes[1, 1].set_ylabel('Количество')
        
        # Значения на столбцах
        for i, v in enumerate(cat_counts):
            axes[1, 1].text(i, v + 0.1, str(v), ha='center')
    else:
        # Если нет категорий - показываем статистику
        axes[1, 1].text(
            0.5, 0.5,
            f"Всего задач: {stats['total']}\n"
            f"Выполнено: {stats['completed']}\n"
            f"В процессе: {stats['pending']}\n"
            f"Процент: {stats['completion_rate']}%",
            ha='center', va='center',
            fontsize=14,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )
        axes[1, 1].axis('off')
        axes[1, 1].set_title('Общая статистика', fontsize=13, fontweight='bold')
    
    # Компоновка
    plt.tight_layout()
    
    # Сохранение в буфер
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    
    return buffer


def create_simple_pie_chart(telegram_id: int) -> io.BytesIO:
    """
    Простая круговая диаграмма для быстрой статистики
    """
    stats = get_statistics(telegram_id)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    labels = ['Выполнено', 'В процессе']
    sizes = [stats['completed'], stats['pending']]
    colors = ['#4CAF50', '#FFC107']
    explode = (0.1, 0)  # Выделяем первый сегмент
    
    ax.pie(
        sizes,
        explode=explode,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        shadow=True,
        startangle=90,
        textprops={'fontsize': 12}
    )
    
    ax.set_title(
        f'Статистика задач\nВсего: {stats["total"]} | Процент выполнения: {stats["completion_rate"]}%',
        fontsize=14,
        fontweight='bold'
    )
    
    # Сохранение
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    
    return buffer
