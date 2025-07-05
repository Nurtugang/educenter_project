from django.apps import AppConfig


class EduprocessesConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'eduprocesses'
	verbose_name = '1.Учебный процесс'
	def ready(self):
		import eduprocesses.signals
