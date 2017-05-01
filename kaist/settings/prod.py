from .common import *

import pymysql
pymysql.install_as_MySQLdb()

DEBUG = True  # FIXME: 배포 연습 시에는 켜두시는 것이 오류 확인이 훨씬 쉽습니다.

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += ['storages']

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.mysql'),
        'HOST': os.environ.get('DB_HOST', ''),
        'NAME': os.environ.get('DB_NAME', ''),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'PORT': os.environ.get('DB_PORT', 3306),
    },
}

STATICFILES_STORAGE = 'kaist.storages.StaticAzureStorage'  # FIXME: 프로젝트 내, storages 지정
DEFAULT_FILE_STORAGE = 'kaist.storages.MediaAzureStorage'  # FIXME: 프로젝트 내, storages 지정

# 설정 / 액세스 키
AZURE_ACCOUNT_NAME = os.environ.get('AZURE_ACCOUNT_NAME', '')
AZURE_ACCOUNT_KEY = os.environ.get('AZURE_ACCOUNT_KEY', '')
AZURE_CONTAINER = os.environ.get('AZURE_CONTAINER', '')              # static 파일 저장/서빙용 컨테이너
AZURE_MEDIA_CONTAINER = os.environ.get('AZURE_MEDIA_CONTAINER', '')  # media 파일 저장/서빙용 커스텀 컨테이너
