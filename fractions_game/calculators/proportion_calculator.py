import random
import re
from fractions import Fraction

def solve_simple_proportion(a, b, c, d=None):
    """
    Решает пропорцию вида a : b = c : x или a : b = x : d
    Возвращает значение x
    """
    if d is None:
        # a : b = c : x -> x = (b * c) / a
        if a == 0:
            return None
        return (b * c) / a
    else:
        # a : b = x : d -> x = (a * d) / b
        if b == 0:
            return None
        return (a * d) / b

def generate_proportion_tasks():
    """Генерирует 6 заданий с пропорциями"""
    tasks = []
    
    # Типы пропорций: простые, средние, сложные
    task_types = ['simple_1', 'simple_2', 'simple_3', 'medium_1', 'medium_2', 'complex_1']
    
    for task_type in task_types:
        
        if task_type == 'simple_1':
            # Простая пропорция: x : 3 = 4 : 6
            b = random.randint(2, 10)
            c = random.randint(2, 15)
            d = random.randint(2, 15)
            
            # Вычисляем x так, чтобы оно было целым
            x = (b * c) / d
            if x != int(x):
                # Подгоняем числа
                d = random.choice([i for i in range(2, 16) if (b * c) % i == 0])
                x = (b * c) // d
            else:
                x = int(x)
            
            task_text = f"x : {b} = {c} : {d}"
            answer = x
            
        elif task_type == 'simple_2':
            # Простая пропорция: 2 : x = 5 : 15
            a = random.randint(2, 12)
            c = random.randint(2, 15)
            d = random.randint(2, 20)
            
            # Вычисляем x
            x = (a * d) / c
            if x != int(x):
                # Подгоняем числа
                c = random.choice([i for i in range(2, 16) if (a * d) % i == 0])
                x = (a * d) // c
            else:
                x = int(x)
            
            task_text = f"{a} : x = {c} : {d}"
            answer = x
            
        elif task_type == 'simple_3':
            # Пропорция с десятичными: 1.5 : x = 3 : 8
            a = random.choice([1.5, 2.5, 3.5, 4.5, 0.5])
            c = random.randint(2, 8)
            d = random.randint(4, 16)
            
            x = (a * d) / c
            if abs(x - round(x, 1)) < 0.01:
                x = round(x, 1)
            
            task_text = f"{a} : x = {c} : {d}"
            answer = x
            
        elif task_type == 'medium_1':
            # Пропорция из задачи: "5 рабочих за 3 дня. Сколько рабочих за 1 день?"
            workers1 = random.randint(3, 12)
            days1 = random.randint(2, 8)
            days2 = random.randint(1, days1 - 1)
            
            # Обратная пропорциональность: w1 * d1 = w2 * d2
            workers2 = (workers1 * days1) / days2
            if workers2 != int(workers2):
                days2 = random.choice([i for i in range(1, days1) if (workers1 * days1) % i == 0])
                workers2 = (workers1 * days1) // days2
            else:
                workers2 = int(workers2)
            
            task_text = f"{workers1} рабочих выполняют работу за {days1} дня. За сколько дней выполнят работу {workers2} рабочих?"
            answer = days2
            
        elif task_type == 'medium_2':
            # Пропорция с масштабом: "На карте 2 см = 5 км. Сколько км в 7 см?"
            map_cm1 = random.randint(1, 5)
            real_km1 = random.randint(3, 15)
            map_cm2 = random.randint(map_cm1 + 1, 15)
            
            real_km2 = (map_cm2 * real_km1) / map_cm1
            if real_km2 != int(real_km2):
                if real_km2 * 2 == int(real_km2 * 2):
                    real_km2 = real_km2
                else:
                    # Подгоняем числа
                    map_cm2 = map_cm1 * random.randint(2, 5)
                    real_km2 = (map_cm2 * real_km1) // map_cm1
            
            task_text = f"На карте {map_cm1} см соответствует {real_km1} км. Сколько километров соответствует {map_cm2} см?"
            answer = real_km2
            
        elif task_type == 'complex_1':
            # Составная пропорция: (x+2) : 5 = 6 : (x-1)
            # (x+2)(x-1) = 5*6 = 30
            # x² + x - 2 = 30
            # x² + x - 32 = 0
            # Но это слишком сложно, упростим:
            
            # Пропорция: (x+a) : b = c : d, где x - целое
            a = random.randint(1, 5)
            b = random.randint(2, 8)
            c = random.randint(2, 10)
            
            # Выбираем x так, чтобы все было целым
            x = random.randint(1, 10)
            d = (b * c) / (x + a)
            
            if d != int(d):
                # Подбираем другие значения
                x = random.randint(1, 15)
                for test_d in range(1, 20):
                    if (test_d * (x + a)) % (b * c) == 0:
                        d = test_d
                        break
                else:
                    # Возвращаемся к простой пропорции
                    task_text = f"{random.randint(2,8)} : x = {random.randint(2,10)} : {random.randint(2,15)}"
                    answer = random.randint(1, 20)
                    tasks.append({
                        'task': task_text,
                        'answer': answer,
                        'type': task_type
                    })
                    continue
            else:
                d = int(d)
            
            task_text = f"(x + {a}) : {b} = {c} : {d}"
            answer = x
        
        tasks.append({
            'task': task_text,
            'answer': answer,
            'type': task_type
        })
    
    return tasks

def check_proportion_answer(user_answer, correct_answer, task_type):
    """Проверяет ответ пользователя для пропорций"""
    try:
        user_answer = user_answer.strip()
        user_value = float(user_answer)
        
        # Для разных типов задач разная точность
        if task_type in ['simple_3']:
            tolerance = 0.1
        elif 'medium' in task_type:
            tolerance = 0.5
        else:
            tolerance = 0.01
        
        return abs(user_value - correct_answer) <= tolerance
        
    except (ValueError, TypeError):
        return False

def check_proportion_answers(tasks, user_answers):
    """Проверяет массив ответов пользователя для пропорций"""
    results = []
    
    for i, task in enumerate(tasks):
        if i < len(user_answers):
            user_answer = user_answers[i]
            is_correct = check_proportion_answer(
                user_answer, 
                task['answer'], 
                task['type']
            )
            results.append(is_correct)
        else:
            results.append(False)
    
    return results