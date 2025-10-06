# fractions_game/calculators/__init__.py

"""
Модуль калькуляторов для тренажеров математики

Содержит генераторы заданий и проверщики ответов для:
- Дробей (легкий уровень)
- Процентов
- Пропорций
"""

from .fractions_calculator import (
    generate_easy_fractions,
    check_fractions_answers,
    calculate_fraction_operation
)

from .percent_calculator import (
    generate_percent_tasks,
    check_percent_answers,
    format_percent_answer
)

from .proportion_calculator import (
    generate_proportion_tasks,
    check_proportion_answers
)

__all__ = [
    'generate_easy_fractions',
    'check_fractions_answers',
    'calculate_fraction_operation',
    'generate_percent_tasks',
    'check_percent_answers',
    'format_percent_answer',
    'generate_proportion_tasks',
    'check_proportion_answers',
]