import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = os.getenv("DEBUG") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

INTERNAL_IPS = os.getenv("INTERNAL_IPS", "").split(",")

INSTALLED_APPS = [
    'debug_toolbar',
    'rangefilter',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'users.apps.UsersConfig',    
    'eduapp.apps.EduappConfig',
    'eduprocesses.apps.EduprocessesConfig',
    'fractions_game.apps.FractionsGameConfig',
    'check_journal.apps.CheckJournalConfig',
    'quizer.apps.QuizerConfig',
    'open_quiz.apps.OpenQuizConfig',
    'senim_store.apps.SenimStoreConfig',
    'weekly_tests.apps.WeeklyTestsConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'educenter_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'builtins': [
                'eduapp.templatetags.my_filters',
                'eduprocesses.templatetags.custom_filters',
                'open_quiz.templatetags.custom_filters' 
            ],
        },
    },
]

WSGI_APPLICATION = 'educenter_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),   
        'PORT': os.getenv('DB_PORT'),
    }
}

LANGUAGES = (
    ('ru', 'Русский'),
    ('kk', 'Қазақ'),
    ('en', 'English'),
)

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Asia/Almaty'

USE_I18N = True

USE_L10N = True

USE_TZ = True

AUTH_USER_MODEL = 'users.CustomUser'
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'index'
LOGIN_URL = 'login'

STATIC_URL = '/static/'
STATIC_ROOT= os.path.join(BASE_DIR,'staticfiles')

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / 'media'

MEDIA_RESPONSE_HEADERS = {
    'Cache-Control': 'public, max-age=604800',
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_AGE = 1209600
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = None

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]