import random

def generate_decimal_fractions():
    """Генератор заданий для десятичных дробей (с усложнёнными задачами на сложение и вычитание)"""
    tasks = []
    task_types = [
        'addition', 'subtraction', 'multiplication',
        'division', 'addition_hard', 'subtraction_hard'
    ]
    
    for task_type in task_types:
        if task_type == 'addition':
            # Простое сложение десятичных дробей
            a = round(random.uniform(0.1, 9.9), 1)
            b = round(random.uniform(0.1, 9.9), 1)
            answer = round(a + b, 2)
            task_text = f"{a} + {b}"

        elif task_type == 'subtraction':
            # Простое вычитание десятичных дробей
            a = round(random.uniform(1.0, 9.9), 1)
            b = round(random.uniform(0.1, a - 0.1), 1)
            answer = round(a - b, 2)
            task_text = f"{a} − {b}"

        elif task_type == 'multiplication':
            # Умножение десятичных дробей
            a = round(random.uniform(0.2, 4.5), 1)
            b = round(random.uniform(0.2, 4.5), 1)
            answer = round(a * b, 3)
            task_text = f"{a} × {b}"

        elif task_type == 'division':
            # Деление десятичных дробей
            a = round(random.uniform(1.0, 9.9), 2)
            b = round(random.uniform(0.2, 4.5), 2)
            answer = round(a / b, 3)
            task_text = f"{a} ÷ {b}"

        elif task_type == 'addition_hard':
            # Усложнённое сложение — больше знаков после запятой
            a = round(random.uniform(10.1, 999.9), random.choice([2, 3]))
            b = round(random.uniform(10.1, 999.9), random.choice([2, 3]))
            answer = round(a + b, 4)
            task_text = f"{str(a).replace('.', ',')} + {str(b).replace('.', ',')}"

        elif task_type == 'subtraction_hard':
            # Усложнённое вычитание — мелкие разности и больше знаков
            a = round(random.uniform(100.0, 999.99), random.choice([2, 3]))
            b = round(random.uniform(a - 5.0, a - 0.01), random.choice([2, 3]))
            answer = round(a - b, 4)
            task_text = f"{str(a).replace('.', ',')} − {str(b).replace('.', ',')}"

        tasks.append({
            'task': task_text,
            'answer': answer,
            'type': task_type
        })
    
    return tasks


def check_decimal_fraction(user_answer, correct_answer, task_type):
    """Проверка одного ответа для десятичных дробей"""
    try:
        user_answer = user_answer.strip().replace(',', '.')
        user_value = float(user_answer)
        correct_value = float(correct_answer)
        tolerance = 0.01
        return abs(user_value - correct_value) <= tolerance
    except Exception:
        return False


def check_decimal_fractions(tasks, user_answers):
    """Проверка массива ответов пользователя для десятичных дробей"""
    results = []
    for i, task in enumerate(tasks):
        if i < len(user_answers):
            user_answer = user_answers[i]
            result = check_decimal_fraction(user_answer, task['answer'], task['type'])
            results.append(result)
        else:
            results.append(False)
    return results