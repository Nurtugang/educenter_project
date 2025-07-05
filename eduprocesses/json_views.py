import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from users.models import CustomUser
from eduprocesses.models import Lesson, StudentAttendance

@csrf_exempt
def add_coins(request):
	student_id = request.POST.get('student_id', '')
	student = CustomUser.objects.get(id=student_id)
	lesson_id = request.POST.get('lesson_id', '')
	value = request.POST.get('value', '')
	student_attendance = StudentAttendance.objects.get(student=student, lesson_id=lesson_id)
	if value.strip() == '':
		student_attendance.coins = 0
	else:
		student_attendance.coins = int(value)
	student_attendance.save()
	
	return JsonResponse({"success":"Updated"})


@csrf_exempt
def add_mark(request):
	student_id = request.POST.get('student_id', '')
	student = CustomUser.objects.get(id=student_id)
	lesson_id = request.POST.get('lesson_id', '')
	value = request.POST.get('value', '')
	student_attendance = StudentAttendance.objects.get(student=student, lesson_id=lesson_id)
	if value:
		student_attendance.mark = int(value)
		student_attendance.attendance_status = 'PR'
		student_attendance.save()
	return JsonResponse({"success":"Updated"})

@csrf_exempt
def add_comment(request):
	student_id = request.POST.get('student_id', '')
	student = CustomUser.objects.get(id=student_id)
	lesson_id = request.POST.get('lesson_id', '')
	value = request.POST.get('value', '')
	student_attendance = StudentAttendance.objects.get(student=student, lesson_id=lesson_id)
	student_attendance.comment = value
	student_attendance.save()
	return JsonResponse({"success":"Updated"})

@csrf_exempt
def add_abs(request):
	student_id = request.POST.get('student_id', '')
	student = CustomUser.objects.get(id=student_id)
	lesson_id = request.POST.get('lesson_id', '')
	abs = request.POST.get('abs', '')
	student_attendance = StudentAttendance.objects.get(student=student, lesson_id=lesson_id)
	if abs:
		student_attendance.attendance_status = abs
		if abs != 'PR':
			student_attendance.mark = None
		student_attendance.save()
	return JsonResponse({"success":"Updated"})


@csrf_exempt
def add_homework_view(request, lesson_id):
	if request.method == 'POST':
		try:
			data = json.loads(request.body)
			lesson = Lesson.objects.get(pk=lesson_id)
			lesson.homework = data.get('homework', '')
			lesson.save()
			return JsonResponse({'success': True})
		except Lesson.DoesNotExist:
			return JsonResponse({'success': False, 'error': 'Lesson not found'})
		except Exception as e:
			return JsonResponse({'success': False, 'error': str(e)})

	return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def add_max_grade_view(request, lesson_id):
	if request.method == 'POST':
		try:
			data = json.loads(request.body)
			lesson = Lesson.objects.get(pk=lesson_id)
			lesson.max_grade = data.get('max_grade', '')
			lesson.save()
			return JsonResponse({'success': True})
		except Lesson.DoesNotExist:
			return JsonResponse({'success': False, 'error': 'Lesson not found'})
		except Exception as e:
			return JsonResponse({'success': False, 'error': str(e)})

	return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def add_homework_status(request):
    """AJAX функция для отметки выполнения домашнего задания"""
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    student_id = request.POST.get('student_id', '')
    lesson_id = request.POST.get('lesson_id', '')
    homework_status = request.POST.get('homework_status', '')
    
    # Отладочный вывод
    print(f"Received homework_status: '{homework_status}' (type: {type(homework_status)})")
    
    if not student_id or not lesson_id:
        return JsonResponse({"error": "Missing required parameters"}, status=400)
    
    try:
        student = CustomUser.objects.get(id=student_id)
        student_attendance = StudentAttendance.objects.get(student=student, lesson_id=lesson_id)
        
        if homework_status == 'true':
            student_attendance.homework_completed = True
            print("Setting homework_completed to True")
        elif homework_status == 'false':
            student_attendance.homework_completed = False
            print("Setting homework_completed to False")
        elif homework_status == 'clear':
            student_attendance.homework_completed = None
            print("Setting homework_completed to None")
        else:
            print(f"Unknown homework_status: '{homework_status}'")
            return JsonResponse({"error": "Invalid homework status"}, status=400)
        
        student_attendance.save()
        print(f"Saved homework_completed: {student_attendance.homework_completed}")
        
        return JsonResponse({
            "success": "Updated",
            "homework_completed": student_attendance.homework_completed,
            "student_id": student_id,
            "lesson_id": lesson_id
        })
        
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "Student not found"}, status=404)
        
    except StudentAttendance.DoesNotExist:
        return JsonResponse({"error": "Student attendance not found"}, status=404)
        
    except Exception as e:
        return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)