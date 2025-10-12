import random
import re
import sympy as sp


def clean_expression(expression_str):
    expression_str = re.sub(r'1\*', '', expression_str)
    expression_str = re.sub(r'\*', '', expression_str)
    return expression_str


def insert_multiplication_operator(expression):
    expression = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', expression)
    return expression


def generate_expression_tasks():
    """Генератор заданий для выражений (ровно как в старом коде)"""
    expressions = []

    for _ in range(6):
        m = random.randint(1, 4)
        var1 = random.randint(2, 15)
        var2 = random.randint(2, 15)
        var3 = random.randint(2, 15)
        fvar1 = round(random.uniform(0, 5), 1)
        fvar2 = round(random.uniform(0, 5), 1)
        fvar3 = round(random.uniform(0, 5), 1)

        sign1 = random.choice(['+', '-'])
        sign2 = random.choice(['+', '-'])
        sign3 = random.choice(['+', '-'])
        sign4 = random.choice(['', '-'])

        if _ == 0:
            expression = f"{var1}*({sign4}{m}*m+{var2}){sign2}{var3}"
        elif _ == 1:
            expression = f"{var1}{sign1}{var2}*({sign4}c{sign3}{var3})"
        elif _ == 2:
            expression = f"m{sign1}{var1}*({var2}{sign2}m){sign3}{var3}"
        elif _ == 3:
            expression = f"({fvar1}{sign1}x){sign2}({fvar2}{sign3}x)"
        elif _ == 4:
            expression = f"y{sign1}({fvar1}{sign2}y){sign3}{fvar2}"
        else:
            expression = f"({fvar1}{sign1}{m}*m){sign2}(-m{sign3}{fvar2})"

        expressions.append(expression)

    # Для фронта формируем удобный JSON формат
    formatted_tasks = [clean_expression(e) for e in expressions]
    return expressions, formatted_tasks


def check_expression_answers(expressions, answers):
    """Проверяет введённые ответы (символьное сравнение)"""
    results = []
    for i in range(len(expressions)):
        try:
            left = sp.simplify(expressions[i])
            right = sp.sympify(insert_multiplication_operator(answers[i]))
            results.append(left == right or str(left) == str(right))
        except Exception:
            results.append(False)
    return results