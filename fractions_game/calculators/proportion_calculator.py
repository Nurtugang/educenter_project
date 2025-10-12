import random
import re
from fractions import Fraction

def solve_simple_proportion(a, b, c, d=None):
    """
    Решает пропорцию вида a : b = c : x или a : b = x : d
    Возвращает значение x
    """
    if d is None:
        if a == 0:
            return None
        return (b * c) / a
    else:
        if b == 0:
            return None
        return (a * d) / b

def generate_proportion_tasks():
    """Генерирует 8 заданий с пропорциями"""
    tasks = []
    
    task_types = ['simple_1', 'simple_2', 'simple_3', 'medium_1', 'medium_2', 'complex_1', 'complex_2', 'complex_3']
    
    for task_type in task_types:
        
        if task_type == 'simple_1':
            b = random.randint(2, 10)
            c = random.randint(2, 15)
            d = random.randint(2, 15)
            
            x = (b * c) / d
            if x != int(x):
                d = random.choice([i for i in range(2, 16) if (b * c) % i == 0])
                x = (b * c) // d
            else:
                x = int(x)
            
            task_text = f"x : {b} = {c} : {d}"
            answer = x
            
        elif task_type == 'simple_2':
            a = random.randint(2, 12)
            c = random.randint(2, 15)
            d = random.randint(2, 20)
            
            x = (a * d) / c
            if x != int(x):
                c = random.choice([i for i in range(2, 16) if (a * d) % i == 0])
                x = (a * d) // c
            else:
                x = int(x)
            
            task_text = f"{a} : x = {c} : {d}"
            answer = x
            
        elif task_type == 'simple_3':
            a = random.choice([1.5, 2.5, 3.5, 4.5, 0.5])
            c = random.randint(2, 8)
            d = random.randint(4, 16)
            
            x = (a * d) / c
            if abs(x - round(x, 1)) < 0.01:
                x = round(x, 1)
            
            task_text = f"{a} : x = {c} : {d}"
            answer = x
            
        elif task_type == 'medium_1':
            workers_templates = [
                "рабочих выполняют работу",
                "человека за {days1} дней пропололи участок клубники, за какое время выполнят эту работу {workers2} человек",
                "рабочих строят дом"
            ]
            
            template = random.choice(workers_templates)
            
            workers1 = random.randint(3, 12)
            days1 = random.randint(2, 8)
            days2 = random.randint(1, days1 - 1)
            
            workers2 = (workers1 * days1) / days2
            if workers2 != int(workers2):
                days2 = random.choice([i for i in range(1, days1) if (workers1 * days1) % i == 0])
                workers2 = (workers1 * days1) // days2
            else:
                workers2 = int(workers2)
            
            if "клубники" in template:
                task_text = f"{workers1} {template.format(days1=days1, workers2=workers2)}?"
                answer = days2
            else:
                task_text = f"{workers1} {template} за {days1} дня. За сколько дней выполнят работу {workers2} {template.split()[0]}?"
                answer = days2
            
        elif task_type == 'medium_2':
            scale_templates = [
                "На карте {cm1} см соответствует {km1} км. Сколько километров соответствует {cm2} см",
                "Для изготовления {n1} одинаковых приборов требуется {kg1} кг металла. Сколько килограммов металла потребуется для изготовления {n2} таких приборов"
            ]
            
            template = random.choice(scale_templates)
            
            if "карте" in template:
                map_cm1 = random.randint(1, 5)
                real_km1 = random.randint(3, 15)
                map_cm2 = random.randint(map_cm1 + 1, 15)
                
                real_km2 = (map_cm2 * real_km1) / map_cm1
                if real_km2 != int(real_km2):
                    if real_km2 * 2 == int(real_km2 * 2):
                        real_km2 = real_km2
                    else:
                        map_cm2 = map_cm1 * random.randint(2, 5)
                        real_km2 = (map_cm2 * real_km1) // map_cm1
                
                task_text = template.format(cm1=map_cm1, km1=real_km1, cm2=map_cm2) + "?"
                answer = real_km2
            else:
                n1 = random.randint(5, 15)
                kg1 = round(random.uniform(10, 25), 1)
                n2 = random.randint(n1 - 4, n1 - 1)
                
                kg2 = (n2 * kg1) / n1
                kg2 = round(kg2, 1)
                
                task_text = template.format(n1=n1, kg1=kg1, n2=n2) + "?"
                answer = kg2
            
        elif task_type == 'complex_1':
            a = random.randint(1, 5)
            b = random.randint(2, 8)
            c = random.randint(2, 10)
            
            # Подбираем x чтобы (x+a) делилось на нужное
            x = random.randint(2, 12)
            
            # (x+a) : b = c : d
            # d = (b * c) / (x + a)
            d = (b * c) / (x + a)
            
            # Проверяем что d целое
            if d != int(d):
                # Подбираем x так чтобы (x+a) было делителем b*c
                product = b * c
                possible_x = []
                for test_x in range(1, 20):
                    if product % (test_x + a) == 0:
                        possible_x.append(test_x)
                
                if possible_x:
                    x = random.choice(possible_x)
                    d = product // (x + a)
                else:
                    # Fallback к простой пропорции
                    b_val = random.randint(2, 8)
                    c_val = random.randint(2, 10)
                    d_val = random.randint(2, 15)
                    x = (b_val * c_val) / d_val
                    if x == int(x):
                        x = int(x)
                    task_text = f"x : {b_val} = {c_val} : {d_val}"
                    answer = x
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
            
        elif task_type == 'complex_2':
            # (3x - a) / b = (3x - c) / d
            coef = random.choice([2, 3, 4])
            a = random.randint(5, 20)
            b = random.choice([4, 6, 8, 12])
            c = round(random.uniform(2, 8), 1)
            d = random.choice([2, 4, 8])
            
            # Решаем: d(3x - a) = b(3x - c)
            # d*3x - d*a = b*3x - b*c
            # d*3x - b*3x = d*a - b*c
            # 3x(d - b) = d*a - b*c
            # x = (d*a - b*c) / (3*(d - b))
            
            if d == b:
                d = b + 2
            
            x = (d * a - b * c) / (coef * (d - b))
            
            if x <= 0 or abs(x - round(x, 1)) > 0.05:
                x = random.randint(3, 8)
                a = random.randint(5, 15)
                c = (d * a - coef * x * (d - b)) / b
                c = round(c, 1)
            else:
                x = round(x, 1)
            
            task_text = f"({coef}x - {a}) / {b} = ({coef}x - {c}) / {d}"
            answer = x
            
        elif task_type == 'complex_3':
            # (a + bx) : c = dx : e
            a = random.randint(1, 5)
            b = random.randint(3, 12)
            c = random.randint(2, 8)
            d = random.randint(1, 6)
            
            # Решаем: e(a + bx) = c * dx
            # e*a + e*bx = c*dx
            # e*bx - c*dx = -e*a
            # x(e*b - c*d) = -e*a
            # x = -e*a / (e*b - c*d)
            
            e = random.randint(2, 5)
            
            if e * b == c * d:
                e = e + 1
            
            x = (e * a) / (c * d - e * b)
            
            if x <= 0 or abs(x - round(x, 1)) > 0.05:
                x = random.randint(1, 5)
                e = (c * d * x) / (a + b * x)
                if e != int(e) or e <= 0:
                    e = 2
                    a = int((c * d * x / e) - b * x)
                else:
                    e = int(e)
            else:
                x = round(x, 1)
            
            task_text = f"({a} + {b}x) : {c} = {d}x : {e}"
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
        user_answer = user_answer.strip().replace(',', '.')
        
        # Проверка на дробь (например 7/16)
        if '/' in user_answer:
            parts = user_answer.split('/')
            if len(parts) == 2:
                numerator = float(parts[0])
                denominator = float(parts[1])
                if denominator != 0:
                    user_value = numerator / denominator
                else:
                    return False
            else:
                return False
        else:
            user_value = float(user_answer)
        
        # Приводим correct_answer к float для корректного сравнения
        correct_answer = float(correct_answer)
        
        # Устанавливаем толерантность в зависимости от типа задачи
        if task_type in ['simple_3', 'complex_2', 'complex_3']:
            tolerance = 0.2
        elif 'medium' in task_type:
            tolerance = 0.5
        else:
            tolerance = 0.05  # Увеличил с 0.01 до 0.05 для надежности
        
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