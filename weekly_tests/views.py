from django.shortcuts import render
from django.db.models import Avg, Count
from .models import WeeklyTest, WeeklyTestResult
from users.models import CustomUser


def weekly_leaderboard(request):
    """Отображение доски почета еженедельных тестов"""
    
    # Получаем все тесты, отсортированные по дате (новые сначала)
    all_tests = WeeklyTest.objects.all().order_by('-week_start')
    
    # Последний тест
    current_test = all_tests.first() if all_tests else None
    
    # Предыдущие тесты (кроме последнего)
    previous_tests = list(all_tests[1:]) if all_tests.count() > 1 else []
    
    def get_leaderboard_for_test(test):
        """Получить лидерборд для конкретного теста"""
        if not test:
            return []
        
        # Получаем результаты с группировкой по студентам
        results = WeeklyTestResult.objects.filter(
            weekly_test=test,
            score__isnull=False
        ).select_related('student', 'subject')
        
        # Группируем по студентам
        students_data = {}
        
        for result in results:
            student_id = result.student.id
            
            if student_id not in students_data:
                students_data[student_id] = {
                    'student': result.student,
                    'subjects': [],
                    'total_score': 0,
                    'subject_count': 0
                }
            
            students_data[student_id]['subjects'].append({
                'subject': result.subject.name,
                'score': result.score
            })
            students_data[student_id]['total_score'] += result.score
            students_data[student_id]['subject_count'] += 1
        
        # Формируем лидерборд
        leaderboard = []
        for student_id, data in students_data.items():
            if data['subject_count'] > 0:
                average_score = data['total_score'] / data['subject_count']
                leaderboard.append({
                    'student': data['student'],
                    'average_score': round(average_score, 2),
                    'subjects': data['subjects'],
                    'total_tests': data['subject_count']
                })
        
        # Сортируем по среднему баллу (по убыванию)
        leaderboard.sort(key=lambda x: x['average_score'], reverse=True)
        
        # Добавляем позиции
        for i, item in enumerate(leaderboard, 1):
            item['position'] = i
            
        half = len(leaderboard) // 2
        if len(leaderboard) % 2 == 1:
            half += 1

        for item in leaderboard:
            if item['position'] <= half:
                item['column'] = 'left'
            else:
                item['column'] = 'right'
                
        return leaderboard
    
    # Получаем лидерборды
    current_leaderboard = get_leaderboard_for_test(current_test)
    previous_leaderboards = []
    
    for test in previous_tests:
        leaderboard = get_leaderboard_for_test(test)
        previous_leaderboards.append({
            'test': test,
            'leaderboard': leaderboard
        })
    
    context = {
        'current_test': current_test,
        'current_leaderboard': current_leaderboard,
        'previous_leaderboards': previous_leaderboards
    }
    
    return render(request, 'leaderboard.html', context)