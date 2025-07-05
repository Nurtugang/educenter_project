from django.shortcuts import render
from django.http.response import FileResponse, Http404, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import pathlib
import json
import random
import sympy as sp
import re
from .eq import generate_equations, format_equation, solve

@login_required
def equations(request):
    return render(request, 'equations.html')

def equations_generator(request):
    equations = generate_equations()
    formatted_equations = [format_equation(eq) for eq in equations]
    return JsonResponse({'formatted_equations': formatted_equations, 'equations':equations})

@csrf_exempt
def equations_checker(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            equations = data.get('equations', [])
            answers = data.get('answers', [])
            results = []
            
            for i in range(len(equations)):
                solution = solve(equations[i])
                try:
                    if int(answers[i]) == int(solution):
                        results.append(True)
                    else:
                        results.append(False)
                except Exception:
                    results.append(False)

            return JsonResponse({'success': True, 'results': results})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def clean_expression(expression_str):
    # Удаление умножения на 1*
    expression_str = re.sub(r'1\*', '', expression_str)
    # Удаление знаков умножения перед открывающей скобкой
    expression_str = re.sub(r'\*', '', expression_str)
    return expression_str

def insert_multiplication_operator(expression):
    # Используем регулярное выражение для вставки '*' перед переменной, если необходимо
    expression = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', expression)
    return expression

def generate_expressions():
    expressions = []

    for _ in range(6):
        # Генерация случайных коэффициентов и чисел
        m = random.randint(1, 4)
        var1 = random.randint(2, 15)
        var2 = random.randint(2, 15)
        var3 = random.randint(2, 15)
        fvar1 = round(random.uniform(0, 5), 1)
        fvar2 = round(random.uniform(0, 5), 1)
        fvar3 = round(random.uniform(0, 5), 1)

        # Генерация случайных знаков
        sign1 = random.choice(['+', '-'])
        sign2 = random.choice(['+', '-'])
        sign3 = random.choice(['+', '-'])
        sign4 = random.choice(['', '-'])

        # Формирование выражения
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
        elif _ == 5:
            expression = f"({fvar1}{sign1}{m}*m){sign2}(-m{sign3}{fvar2})"
        expressions.append(expression)

    return expressions

@login_required
def play_game(request):
    return render(request, 'fractions.html')

@login_required
def expressions(request):
    return render(request, 'expressions.html')


def get_file_game(request, path: str) -> FileResponse:
    file = pathlib.Path(settings.STATIC_ROOT) / 'fractions_game' / path
    if not file.exists():
        raise Http404()
    response = FileResponse(open(file, 'rb'))
    response['Cache-Control'] = 'public, max-age=31536000, immutable'
    response['Content-Disposition'] = f'inline; filename="{file}"'
    return response
    # return FileResponse(open(file, 'rb'))


def expressions_generator(request):
    expressions = generate_expressions()
    cleaned_expressions = [clean_expression(expr) for expr in expressions]
    return JsonResponse({'expressions': expressions, 'cleaned_expressions':cleaned_expressions})

@csrf_exempt
def expressions_checker(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            expressions = data.get('expressions', [])
            answers = data.get('answers', [])
            results = []
            for i in range(len(expressions)):
                try:
                    if sp.simplify(expressions[i]) == sp.sympify(insert_multiplication_operator(answers[i])) or sp.simplify(expressions[i]).__str__() == sp.sympify(insert_multiplication_operator(answers[i])).__str__():
                        results.append(True)
                    else:
                        results.append(False)
                except Exception:
                    results.append(False)
            # Возвращаем результат в виде JsonResponse (просто для примера)
            result = {'success': True, 'results': results}
            return JsonResponse(result)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)