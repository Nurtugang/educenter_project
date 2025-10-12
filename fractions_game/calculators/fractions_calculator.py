import random
import math
from fractions import Fraction

def gcd(a, b):
    """Находит наибольший общий делитель"""
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    """Находит наименьшее общее кратное"""
    return abs(a * b) // gcd(a, b)

def simplify_fraction(num, den):
    """Упрощает дробь до несократимой формы"""
    if den == 0:
        raise ValueError("Знаменатель не может быть нулем")
    
    common_divisor = gcd(abs(num), abs(den))
    num //= common_divisor
    den //= common_divisor
    
    # Если знаменатель отрицательный, переносим знак в числитель
    if den < 0:
        num = -num
        den = -den
        
    return num, den

def add_fractions(num1, den1, num2, den2):
    """Складывает две дроби"""
    common_den = lcm(den1, den2)
    new_num1 = num1 * (common_den // den1)
    new_num2 = num2 * (common_den // den2)
    result_num = new_num1 + new_num2
    return simplify_fraction(result_num, common_den)

def subtract_fractions(num1, den1, num2, den2):
    """Вычитает вторую дробь из первой"""
    common_den = lcm(den1, den2)
    new_num1 = num1 * (common_den // den1)
    new_num2 = num2 * (common_den // den2)
    result_num = new_num1 - new_num2
    return simplify_fraction(result_num, common_den)

def multiply_fractions(num1, den1, num2, den2):
    """Умножает две дроби"""
    result_num = num1 * num2
    result_den = den1 * den2
    return simplify_fraction(result_num, result_den)

def divide_fractions(num1, den1, num2, den2):
    """Делит первую дробь на вторую"""
    if num2 == 0:
        raise ValueError("Деление на ноль")
    result_num = num1 * den2
    result_den = den1 * num2
    return simplify_fraction(result_num, result_den)

def calculate_fraction_operation(num1, den1, num2, den2, operation):
    """Выполняет операцию над двумя дробями"""
    operations = {
        '+': add_fractions,
        '-': subtract_fractions,
        '*': multiply_fractions,
        '/': divide_fractions
    }
    
    if operation not in operations:
        raise ValueError(f"Неподдерживаемая операция: {operation}")
    
    return operations[operation](num1, den1, num2, den2)

def generate_easy_fractions():
    """Генерирует 6 легких заданий с дробями"""
    tasks = []
    operations = ['+', '-', '*', '/']
    
    for i in range(6):
        operation = random.choice(operations)
        
        # Генерируем дроби с небольшими числителями и знаменателями
        if operation in ['+', '-']:
            # Для сложения и вычитания делаем знаменатели не очень большими
            den1 = random.randint(2, 8)
            den2 = random.randint(2, 8)
            num1 = random.randint(1, den1 - 1)  # Правильные дроби
            num2 = random.randint(1, den2 - 1)
        elif operation == '*':
            # Для умножения можем использовать любые дроби
            den1 = random.randint(2, 10)
            den2 = random.randint(2, 10)
            num1 = random.randint(1, 12)
            num2 = random.randint(1, 12)
        else:  # operation == '/'
            # Для деления убеждаемся, что результат будет разумным
            den1 = random.randint(2, 8)
            den2 = random.randint(2, 8)
            num1 = random.randint(1, 15)
            num2 = random.randint(1, 15)
        
        # Вычисляем правильный ответ
        try:
            answer_num, answer_den = calculate_fraction_operation(num1, den1, num2, den2, operation)
            
            # Формируем задание
            display_operation = '÷' if operation == '/' else operation
            task_text = f"{num1}/{den1} {display_operation} {num2}/{den2}"
            
            # Ответ в виде дроби (если знаменатель = 1, то целое число)
            if answer_den == 1:
                answer_text = str(answer_num)
            else:
                answer_text = f"{answer_num}/{answer_den}"
            
            tasks.append({
                'task': task_text,
                'answer': answer_text,
                'answer_num': answer_num,
                'answer_den': answer_den
            })
            
        except (ValueError, ZeroDivisionError):
            # Если возникла ошибка, пропускаем это задание
            continue
    
    # Если получилось меньше 6 заданий, дополняем
    while len(tasks) < 6:
        tasks.extend(generate_easy_fractions()[:6-len(tasks)])
    
    return tasks[:6]

def check_fraction_answer(user_answer, correct_num, correct_den):
    """Проверяет ответ пользователя"""
    try:
        user_answer = user_answer.strip()
        
        # Проверяем разные форматы ввода
        if '/' in user_answer:
            # Ответ в виде дроби
            parts = user_answer.split('/')
            if len(parts) != 2:
                return False
            
            user_num = int(parts[0])
            user_den = int(parts[1])
            
            # Приводим к несократимой форме
            user_num, user_den = simplify_fraction(user_num, user_den)
            
        else:
            # Ответ в виде целого числа или десятичной дроби
            if '.' in user_answer:
                # Десятичная дробь
                decimal_value = float(user_answer)
                correct_decimal = correct_num / correct_den
                return abs(decimal_value - correct_decimal) < 0.001
            else:
                # Целое число
                user_num = int(user_answer)
                user_den = 1
        
        # Сравниваем упрощенные дроби
        return user_num == correct_num and user_den == correct_den
        
    except (ValueError, ZeroDivisionError):
        return False

def check_fractions_answers(tasks, user_answers):
    """Проверяет массив ответов пользователя"""
    results = []
    
    for i, task in enumerate(tasks):
        if i < len(user_answers):
            user_answer = user_answers[i]
            is_correct = check_fraction_answer(
                user_answer, 
                task['answer_num'], 
                task['answer_den']
            )
            results.append(is_correct)
        else:
            results.append(False)
    
    return results