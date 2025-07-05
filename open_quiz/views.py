from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse, HttpResponseForbidden
import json
from django.utils import timezone
from datetime import timedelta


def open_quizer_choose(request):
    qs = OpenQuizSubject.objects.all()
    
    # Если пользователь авторизован, проверяем наличие незавершенных тестов
    ongoing_tests = []
    if request.user.is_authenticated:
        ongoing_tests = OpenTestProgress.objects.filter(
            user=request.user,
            is_completed=False
        ).select_related('quiz_subject')
    
    context = {
        'qs': qs,
        'ongoing_tests': ongoing_tests
    }
    return render(request, 'open_quizer_choose.html', context)


@login_required
def open_quizer_page(request):
    is_student = request.user.groups.filter(name__in=['Студент']).exists()
    
    open_quizer_id = str(request.GET.get('open_quizer_id'))
    open_quiz_subject = OpenQuizSubject.objects.get(id=open_quizer_id)
    
    # Проверяем, есть ли незавершенный тест для этого предмета
    progress = OpenTestProgress.objects.filter(
        user=request.user,
        quiz_subject_id=open_quizer_id,
        is_completed=False
    ).first()
    
    # Если прогресс существует, перенаправляем на страницу с незавершенным тестом
    if progress:
        return redirect(reverse('continue_test', args=[progress.id]))
    
    # Выбираем вопросы согласно логике
    if open_quizer_id == '2':  # если это тест РФМШ 2025
        qs1 = OpenQuestion.objects.filter(quiz_subject__id=open_quizer_id, weight=3).order_by('?')[:5]
        qs2 = OpenQuestion.objects.filter(quiz_subject__id=open_quizer_id, weight=5).order_by('?')[:5]
        qs3 = OpenQuestion.objects.filter(quiz_subject__id=open_quizer_id, weight=7).order_by('?')[:5]
        questions = list(qs1) + list(qs2) + list(qs3)
    else:
        questions = list(OpenQuestion.objects.filter(quiz_subject__id=open_quizer_id).order_by('?')[:20])
    
    context = {
        'is_student': is_student,
        'quiz': open_quiz_subject,
        'quiz_id': open_quizer_id,
        'questions': questions,
        'is_new_test': True,  # Флаг для шаблона, чтобы понять, что это новый тест
    }
    return render(request, 'open_quizer_page.html', context)


@login_required
def continue_test(request, progress_id):
    # Получаем прогресс теста
    progress = get_object_or_404(OpenTestProgress, id=progress_id)
    
    # Проверяем, что пользователь имеет доступ к этому прогрессу
    if progress.user != request.user:
        return HttpResponseForbidden("У вас нет доступа к этому тесту")
    
    # Проверяем, что тест не завершен
    if progress.is_completed:
        return redirect(reverse('open_quizer_results', args=[progress.quiz_subject.id]))
    
    # Загружаем вопросы из сохраненного прогресса
    question_ids = progress.get_question_ids()
    
    # Отладочная информация
    print(f"Question IDs from progress: {question_ids}")
    
    # Проверяем, что у нас есть ID вопросов
    if not question_ids:
        # Если список пустой, возможно это старый прогресс или произошла ошибка
        # В этом случае создаем новый набор вопросов
        if progress.quiz_subject.id == 2:  # Если это тест РФМШ 2025
            qs1 = OpenQuestion.objects.filter(quiz_subject_id=progress.quiz_subject.id, weight=3).order_by('?')[:5]
            qs2 = OpenQuestion.objects.filter(quiz_subject_id=progress.quiz_subject.id, weight=5).order_by('?')[:5]
            qs3 = OpenQuestion.objects.filter(quiz_subject_id=progress.quiz_subject.id, weight=7).order_by('?')[:5]
            questions = list(qs1) + list(qs2) + list(qs3)
        else:
            questions = list(OpenQuestion.objects.filter(quiz_subject_id=progress.quiz_subject.id).order_by('?')[:20])
            
        # Сохраняем новые ID вопросов в прогресс
        question_ids = [q.id for q in questions]
        progress.set_question_ids(question_ids)
        progress.save()
    else:
        # Загружаем вопросы по сохраненным ID
        questions = list(OpenQuestion.objects.filter(id__in=question_ids))
        
        # Сортируем вопросы в том же порядке, что и в сохраненных ID
        questions_dict = {q.id: q for q in questions}
        ordered_questions = []
        for qid in question_ids:
            if qid in questions_dict:
                ordered_questions.append(questions_dict[qid])
        
        questions = ordered_questions
    
    # Получаем временные ответы
    temp_answers = progress.get_temp_answers()
    
    # Отладочная информация
    print(f"Found {len(questions)} questions for progress {progress_id}")
    print(f"Current question index: {progress.current_question_index}")
    print(f"Remaining seconds: {progress.remaining_seconds}")
    
    context = {
        'is_student': request.user.groups.filter(name__in=['Студент']).exists(),
        'quiz': progress.quiz_subject,
        'quiz_id': progress.quiz_subject.id,
        'questions': questions,
        'is_new_test': False,  # Флаг для шаблона
        'progress': progress,
        'progress_id': progress.id,  # Добавляем ID прогресса для формы
        'current_question_index': progress.current_question_index,
        'temp_answers': json.dumps(temp_answers),
        'remaining_seconds': progress.remaining_seconds,
    }
    
    return render(request, 'open_quizer_page.html', context)

@login_required
def save_test_progress(request, quiz_id):
    """
    AJAX-представление для сохранения прогресса теста
    """
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Только POST-запросы"}, status=400)
    
    try:
        data = json.loads(request.body)
        remaining_seconds = data.get('remaining_seconds', 0)
        current_question_index = data.get('current_question_index', 0)
        temp_answers = data.get('temp_answers', {})
        question_ids = data.get('question_ids', [])
        
        # Отладочная информация
        print(f"Saving progress for quiz {quiz_id}")
        print(f"Question IDs: {question_ids}")
        print(f"Current question index: {current_question_index}")
        print(f"Remaining seconds: {remaining_seconds}")
        
        # Находим или создаем запись прогресса
        progress, created = OpenTestProgress.objects.get_or_create(
            user=request.user,
            quiz_subject_id=quiz_id,
            is_completed=False,
            defaults={
                'remaining_seconds': remaining_seconds,
                'current_question_index': current_question_index,
            }
        )
        
        # Обновляем существующую запись
        if not created:
            progress.remaining_seconds = remaining_seconds
            progress.current_question_index = current_question_index
            
        # Сохраняем временные ответы
        progress.set_temp_answers(temp_answers)
        
        # Сохраняем список ID вопросов только при первом создании или если список пуст
        if (created or not progress.get_question_ids()) and question_ids:
            print(f"Setting question IDs: {question_ids}")
            progress.set_question_ids(question_ids)
            
        progress.save()
        
        return JsonResponse({
            "status": "success", 
            "progress_id": progress.id
        })
    except Exception as e:
        import traceback
        print(f"Error saving progress: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
@login_required
def cancel_test(request, progress_id):
    """
    Отменить тест и удалить запись о прогрессе
    """
    progress = get_object_or_404(OpenTestProgress, id=progress_id)
    
    # Проверяем, принадлежит ли прогресс текущему пользователю
    if progress.user != request.user:
        return HttpResponseForbidden("У вас нет доступа к этому тесту")
    
    quiz_id = progress.quiz_subject.id
    progress.delete()
    
    return redirect(reverse('open_quizer_choose'))


def open_testing_handle(request, open_quiz_id):
    if request.method == 'POST':
        answers = []
        user_answer = OpenUserAnswer.objects.filter(
            user=request.user, 
            question__quiz_subject__id=open_quiz_id
        ).order_by('-id').first()
        last_attempt_id = user_answer.attempt_number if user_answer else 0

        with transaction.atomic():
            for key, value in request.POST.items():  # key-value:айди вопроса-ответ пользователя 
                if key.startswith('question_'):
                    question_id = key.split('_')[1]
                    question = OpenQuestion.objects.get(id=question_id)
                    answers.append(OpenUserAnswer(
                        user=request.user, 
                        question=question, 
                        answer_text=value, 
                        attempt_number=last_attempt_id + 1
                    ))

            OpenUserAnswer.objects.bulk_create(answers)
            
            # Отмечаем прогресс как завершенный
            progress = OpenTestProgress.objects.filter(
                user=request.user,
                quiz_subject_id=open_quiz_id,
                is_completed=False
            ).first()
            
            if progress:
                progress.is_completed = True
                progress.save()

        return redirect(reverse('open_quizer_results', args=[open_quiz_id]))
    else:
        return redirect('quizer_choose')


@login_required
def open_quizer_results(request, quiz_id):
    user_attempts = OpenUserAnswer.objects.filter(
        user=request.user, 
        question__quiz_subject_id=quiz_id
    ).values_list('attempt_number', flat=True).distinct().order_by('-attempt_number')

    results = []

    for attempt_number in user_attempts:
        # Получаем все ответы пользователя для данной попытки
        user_answers = OpenUserAnswer.objects.filter(
            user=request.user, 
            question__quiz_subject_id=quiz_id,
            attempt_number=attempt_number
        ).select_related("question")

        # Get the questions the user answered in this attempt
        answered_question_ids = user_answers.values_list('question_id', flat=True)
        answered_questions = OpenQuestion.objects.filter(id__in=answered_question_ids)
        
        total_questions = user_answers.count()
        correct_answers = 0

        maximum_points = answered_questions.aggregate(Sum('weight'))['weight__sum'] or 0

        total_points = 0
        detailed_answers = []

        for answer in user_answers:
            user_answer = answer.answer_text.strip().lower()
            correct_answer = answer.question.correct_answer.strip().lower()
            is_correct = False
            try:
                user_float = float(user_answer)
                correct_float = float(correct_answer)
                is_correct = user_float == correct_float
            except ValueError:
                is_correct = user_answer == correct_answer
                
            if is_correct:
                correct_answers += 1
                total_points += int(answer.question.weight)

            detailed_answers.append({
                "question_text": answer.question.text,
                "question_weight": answer.question.weight,
                "question_image": answer.question.image.url if answer.question.image else None,
                "user_answer": answer.answer_text,
                "correct_answer": answer.question.correct_answer,
                "is_correct": is_correct,
            })

        results.append({
            "attempt_number": attempt_number,
            "score": correct_answers,
            "total": total_questions,
            'maximum_points': maximum_points,
            'total_points': total_points,
            "answers": detailed_answers
        })

    quiz_subject = OpenQuizSubject.objects.get(id=quiz_id)
    context = {
        "quiz_subject": quiz_subject,
        "results": results,
    }
    
    return render(request, "open_quizer_results.html", context)