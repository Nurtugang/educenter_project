import random

def generate_percent_tasks():
    """Генерирует 9 заданий с процентами — строго по порядку"""
    tasks = []
    task_types = [
        'find_percent', 'find_number', 'find_percentage',
        'increase', 'decrease', 'simple_percent',
        'complex_increase_decrease', 'book_reading', 'rectangle_area', 'cucumber_sales'
    ]
    
    # Всегда проходим по всем типам по порядку
    for task_type in task_types:
        if task_type == 'find_percent':
            percent = random.choice([5, 10, 15, 20, 25, 30, 40, 50, 60, 75, 80, 90])
            number = random.randint(10, 200)
            if number % (100 / percent) != 0:
                number = int((100 / percent)) * random.randint(1, 5)
            answer = (percent * number) / 100
            task_text = f"{percent}% от {number}"

        elif task_type == 'find_number':
            percent = random.choice([10, 15, 20, 25, 30, 40, 50])
            part = random.randint(10, 100)
            number = (part * 100) / percent
            if number != int(number):
                number = round(number)
            answer = int(number)
            task_text = f"{percent}% от числа равно {part}. Найти число"

        elif task_type == 'find_percentage':
            part = random.randint(5, 50)
            whole = random.randint(part + 10, 200)
            percentage = (part * 100) / whole
            percentage = round(percentage, 2)
            answer = percentage
            task_text = f"{part} составляет сколько % от {whole}?"

        elif task_type == 'increase':
            number = random.randint(10, 200)
            percent = random.choice([10, 15, 20, 25, 30, 50])
            answer = number + (number * percent) / 100
            task_text = f"{number} увеличить на {percent}%"

        elif task_type == 'decrease':
            number = random.randint(20, 200)
            percent = random.choice([10, 15, 20, 25, 30, 40])
            answer = number - (number * percent) / 100
            task_text = f"{number} уменьшить на {percent}%"

        elif task_type == 'simple_percent':
            decimal_values = [0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.9]
            decimal = random.choice(decimal_values)
            answer = decimal * 100
            task_text = f"Переведите в проценты: {decimal}"

        elif task_type == 'complex_increase_decrease':
            number = random.randint(500, 1500)
            first_percent = 20
            second_percent = 40
            after_increase = number * (1 + first_percent / 100)
            answer = after_increase * (1 - second_percent / 100)
            task_text = (
                f"Число {number} увеличили на {first_percent}%, "
                f"результат уменьшили на {second_percent}%. "
                f"Какое число получилось?"
            )

        elif task_type == 'book_reading':
            first_percent = 60
            second_percent = 60
            read_first = first_percent / 100
            remaining_after_first = 1 - read_first
            read_second = remaining_after_first * (second_percent / 100)
            remaining = 1 - (read_first + read_second)
            answer = round(remaining * 100, 2)
            task_text = (
                f"Арайлым прочитала {first_percent}% книги, потом ещё {second_percent}% остатка. "
                f"Сколько процентов книги осталось прочитать Арайлым?"
            )

        elif task_type == 'rectangle_area':
            length_percent = 20
            width_percent = 60
            answer = 100 - ((1 - length_percent / 100) * (1 - width_percent / 100) * 100)
            answer = round(answer, 2)
            task_text = (
                f"На сколько процентов уменьшится площадь прямоугольника, "
                f"если его длину уменьшить на {length_percent}%, а ширину — на {width_percent}%?"
            )

        elif task_type == 'cucumber_sales':
            total = 850
            first_percent = 10
            second_percent = 20
            first_sold = total * (first_percent / 100)
            remaining = total - first_sold
            second_sold = remaining * (second_percent / 100)
            answer = round(first_sold + second_sold, 2)
            task_text = (
                f"В палатку завезли {total} кг огурцов. "
                f"В первой половине дня продали {first_percent}% огурцов, "
                f"во второй — {second_percent}% от остатка. "
                f"Сколько всего продали огурцов за день?"
            )

        if isinstance(answer, float) and answer.is_integer():
            answer = int(answer)

        tasks.append({
            'task': task_text,
            'answer': answer,
            'type': task_type
        })
    
    return tasks

def check_percent_answer(user_answer, correct_answer, task_type):
    """Проверяет ответ пользователя для процентов"""
    try:
        user_answer = user_answer.strip().replace(',', '.')
        
        # Убираем знак % если он есть
        if user_answer.endswith('%'):
            user_answer = user_answer[:-1]
        
        user_value = float(user_answer)
        
        # Для разных типов задач разная точность
        if task_type in ['find_percentage', 'simple_percent']:
            # Для процентов допускаем небольшую погрешность
            tolerance = 0.1
        else:
            # Для остальных типов более строгая проверка
            tolerance = 0.01
        
        return abs(user_value - correct_answer) <= tolerance
        
    except (ValueError, TypeError):
        return False

def check_percent_answers(tasks, user_answers):
    """Проверяет массив ответов пользователя для процентов"""
    results = []
    
    for i, task in enumerate(tasks):
        if i < len(user_answers):
            user_answer = user_answers[i]
            is_correct = check_percent_answer(
                user_answer, 
                task['answer'], 
                task['type']
            )
            results.append(is_correct)
        else:
            results.append(False)
    
    return results

def format_percent_answer(answer, task_type):
    """Форматирует ответ для отображения"""
    if task_type in ['find_percentage', 'simple_percent']:
        return f"{answer}%"
    else:
        if isinstance(answer, float) and answer.is_integer():
            return str(int(answer))
        else:
            return str(answer)