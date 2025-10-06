import random

def generate_percent_tasks():
    """Генерирует 6 заданий с процентами"""
    tasks = []
    task_types = ['find_percent', 'find_number', 'find_percentage', 'increase', 'decrease', 'simple_percent']
    
    for i in range(6):
        task_type = random.choice(task_types)
        
        if task_type == 'find_percent':
            # Найти процент от числа: 25% от 80 = ?
            percent = random.choice([5, 10, 15, 20, 25, 30, 40, 50, 60, 75, 80, 90])
            number = random.randint(10, 200)
            # Подбираем так, чтобы результат был целым
            if number % (100 / percent) != 0:
                number = int((100 / percent)) * random.randint(1, 5)
            
            answer = (percent * number) / 100
            task_text = f"{percent}% от {number}"
            
        elif task_type == 'find_number':
            # Найти число по проценту: 15% от числа равно 30. Найти число
            percent = random.choice([10, 15, 20, 25, 30, 40, 50])
            part = random.randint(10, 100)
            number = (part * 100) / percent
            
            # Проверяем, что число целое
            if number != int(number):
                continue
                
            answer = int(number)
            task_text = f"{percent}% от числа равно {part}. Найти число"
            
        elif task_type == 'find_percentage':
            # Найти процентное отношение: 30 составляет сколько % от 120?
            part = random.randint(5, 50)
            whole = random.randint(part + 10, 200)
            
            # Подбираем так, чтобы процент был красивым
            percentage = (part * 100) / whole
            if percentage != int(percentage):
                # Подгоняем числа
                percentage = random.choice([10, 15, 20, 25, 30, 40, 50, 60, 75])
                whole = random.randint(20, 100)
                part = int((percentage * whole) / 100)
            
            answer = percentage
            task_text = f"{part} составляет сколько % от {whole}?"
            
        elif task_type == 'increase':
            # Увеличение на процент: 100 увеличить на 15% = ?
            number = random.randint(10, 200)
            percent = random.choice([10, 15, 20, 25, 30, 50])
            answer = number + (number * percent) / 100
            task_text = f"{number} увеличить на {percent}%"
            
        elif task_type == 'decrease':
            # Уменьшение на процент: 200 уменьшить на 25% = ?
            number = random.randint(20, 200)
            percent = random.choice([10, 15, 20, 25, 30, 40])
            answer = number - (number * percent) / 100
            task_text = f"{number} уменьшить на {percent}%"
            
        elif task_type == 'simple_percent':
            # Простое преобразование: Сколько это 0.75 в процентах?
            decimal_values = [0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.9]
            decimal = random.choice(decimal_values)
            answer = decimal * 100
            task_text = f"Переведите в проценты: {decimal}"
        
        # Проверяем, что ответ разумный
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
        user_answer = user_answer.strip()
        
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