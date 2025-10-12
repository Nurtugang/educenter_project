import json
import pathlib
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http.response import FileResponse, Http404, JsonResponse


# Импорты калькуляторов
from .calculators.equations_calculator import generate_equations, format_equation, solve
from .calculators.expressions_calculator import generate_expression_tasks, check_expression_answers

from .calculators.fractions_calculator import generate_easy_fractions, check_fractions_answers
from .calculators.percent_calculator import generate_percent_tasks, check_percent_answers, format_percent_answer
from .calculators.proportion_calculator import generate_proportion_tasks, check_proportion_answers

from .calculators.decimal_fractions_calculator import generate_decimal_fractions, check_decimal_fractions
from .calculators.complex_fractions_calculator import (
    generate_complex_fractions,
    check_complex_fractions,
)

@login_required
def trainers_index(request):
    return render(request, 'trainers.html')


# ============ ПРЕДСТАВЛЕНИЯ ДЛЯ ТРЕНАЖЕРОВ ============

@login_required
def fractions_easy(request):
    """Тренажер легких дробей"""
    return render(request, 'fractions_easy.html')

@login_required
def percentages(request):
    """Тренажер процентов"""
    return render(request, 'percentages.html')

@login_required
def proportions(request):
    """Тренажер пропорций"""
    return render(request, 'proportions.html')

@login_required
def expressions(request):
    """Тренажер выражений"""
    return render(request, 'expressions.html')

@login_required
def equations(request):
    """Тренажер уравнений"""
    return render(request, 'equations.html')

@login_required
def fractions_decimal(request):
    """Тренажёр десятичных дробей"""
    return render(request, 'fractions_decimal.html')

@login_required
def fractions_complex(request):
    return render(request, 'fractions_complex.html')

# ============ ГЕНЕРАТОРЫ ЗАДАНИЙ ============

@login_required
def fractions_generator(request):
    """Генератор заданий для дробей"""
    try:
        tasks = generate_easy_fractions()
        
        # Форматируем задания для фронтенда
        formatted_tasks = []
        answers_data = []
        
        for task in tasks:
            formatted_tasks.append(task['task'])
            answers_data.append({
                'answer_num': task['answer_num'],
                'answer_den': task['answer_den'],
                'answer_text': task['answer']
            })
        
        return JsonResponse({
            'success': True,
            'formatted_tasks': formatted_tasks,
            'tasks_data': answers_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def percent_generator(request):
    """Генератор заданий для процентов"""
    try:
        tasks = generate_percent_tasks()
        
        formatted_tasks = []
        answers_data = []
        
        for task in tasks:
            formatted_tasks.append(task['task'])
            answers_data.append({
                'answer': task['answer'],
                'type': task['type'],
                'formatted_answer': format_percent_answer(task['answer'], task['type'])
            })
        
        return JsonResponse({
            'success': True,
            'formatted_tasks': formatted_tasks,
            'tasks_data': answers_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def proportion_generator(request):
    """Генератор заданий для пропорций"""
    try:
        tasks = generate_proportion_tasks()
        
        formatted_tasks = []
        answers_data = []
        
        for task in tasks:
            formatted_tasks.append(task['task'])
            answers_data.append({
                'answer': task['answer'],
                'type': task['type']
            })
        
        return JsonResponse({
            'success': True,
            'formatted_tasks': formatted_tasks,
            'tasks_data': answers_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def expressions_generator(request):
    """Генератор заданий для выражений"""
    try:
        expressions, cleaned_expressions = generate_expression_tasks()
        return JsonResponse({
            'success': True,
            'expressions': expressions,
            'cleaned_expressions': cleaned_expressions
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def equations_generator(request):
    equations = generate_equations()
    formatted_equations = [format_equation(eq) for eq in equations]
    return JsonResponse({'formatted_equations': formatted_equations, 'equations':equations})

@login_required
def decfractions_generator(request):
    try:
        tasks = generate_decimal_fractions()
        return JsonResponse({'success': True, 'formatted_tasks': [t['task'] for t in tasks], 'tasks_data': tasks})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
@login_required
def complexfractions_generator(request):
    try:
        tasks = generate_complex_fractions()
        return JsonResponse({
            "success": True,
            "formatted_tasks": [t["task"] for t in tasks],
            "tasks_data": tasks
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

# ============ ПРОВЕРЩИКИ ОТВЕТОВ ============

@csrf_exempt
@login_required
def fractions_checker(request):
    """Проверка ответов для дробей"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tasks_data = data.get('tasks_data', [])
            user_answers = data.get('answers', [])
            
            results = check_fractions_answers(tasks_data, user_answers)
            
            return JsonResponse({
                'success': True,
                'results': results,
                'correct_count': sum(results),
                'total_count': len(results)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

@csrf_exempt
@login_required
def percent_checker(request):
    """Проверка ответов для процентов"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tasks_data = data.get('tasks_data', [])
            user_answers = data.get('answers', [])
            
            results = check_percent_answers(tasks_data, user_answers)
            
            return JsonResponse({
                'success': True,
                'results': results,
                'correct_count': sum(results),
                'total_count': len(results)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

@csrf_exempt
@login_required
def proportion_checker(request):
    """Проверка ответов для пропорций"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tasks_data = data.get('tasks_data', [])
            user_answers = data.get('answers', [])
            
            results = check_proportion_answers(tasks_data, user_answers)
            
            return JsonResponse({
                'success': True,
                'results': results,
                'correct_count': sum(results),
                'total_count': len(results)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

@csrf_exempt
@login_required
def expressions_checker(request):
    """Проверка ответов выражений"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            expressions = data.get('expressions', [])
            answers = data.get('answers', [])
            results = check_expression_answers(expressions, answers)
            return JsonResponse({
                'success': True,
                'results': results,
                'correct_count': sum(results),
                'total_count': len(results)
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

@csrf_exempt
@login_required
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

@csrf_exempt
@login_required
def decfractions_checker(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            results = check_decimal_fractions(data.get('tasks_data', []), data.get('answers', []))
            return JsonResponse({'success': True, 'results': results})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

@csrf_exempt
@login_required
def complexfractions_checker(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            results = check_complex_fractions(
                data.get("tasks_data", []),
                data.get("answers", [])
            )
            return JsonResponse({"success": True, "results": results})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Method not allowed"})

# ============ ПРЕДСТАВЛЕНИЯ И ФАЙЛЫ GODOT ============

@login_required
def godot_index(request):
    """Главная страница Godot-игры"""
    return render(request, 'fractions.html')


def godot_file(request, path: str) -> FileResponse:
    """Отдаёт игровые файлы Godot из static/godot"""
    file_path = pathlib.Path(settings.STATIC_ROOT) / 'godot' / path

    if not file_path.exists():
        raise Http404(f"File not found: {path}")

    response = FileResponse(open(file_path, 'rb'))
    response['Cache-Control'] = 'public, max-age=31536000, immutable'
    response['Content-Disposition'] = f'inline; filename="{file_path.name}"'
    return response