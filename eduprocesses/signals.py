from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import StudentAttendance, Lesson, StudyGroup

@receiver(post_save, sender=Lesson)
def create_student_attendance(sender, instance, created, **kwargs):
	if created:
		students = instance.study_group.students.all()
		student_attendance_list = [
			StudentAttendance(lesson=instance, student=student)
			for student in students
		]  
		StudentAttendance.objects.bulk_create(student_attendance_list)

@receiver(m2m_changed, sender=StudyGroup.students.through)
def update_student_attendance(sender, instance, action, model, pk_set, **kwargs):
    if action == 'post_add':
        for lesson in instance.lesson_set.all():
            existing_attendance_students = StudentAttendance.objects.filter(lesson=lesson).values_list('student', flat=True)
            students = instance.students.filter(pk__in=pk_set).exclude(id__in=existing_attendance_students)

            student_attendance_list = [
                StudentAttendance(lesson=lesson, student=student)
                for student in students
            ]
            StudentAttendance.objects.bulk_create(student_attendance_list)
    elif action == 'post_remove':
        return