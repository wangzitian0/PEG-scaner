"""
Django settings for CMS project.

Uses libs/config for shared configuration (SSOT).
"""

import sys
from pathlib import Path
from datetime import timedelta

# Add libs to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import shared settings (SSOT)
from libs.config import settings as app_settings

# =============================================================================
# Core
# =============================================================================
SECRET_KEY = app_settings.django_secret_key
DEBUG = app_settings.debug
ALLOWED_HOSTS = app_settings.django_allowed_hosts

# =============================================================================
# Application definition
# =============================================================================
INSTALLED_APPS = [
    # Django Unfold admin (must be before django.contrib.admin)
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'django_fsm',
    'django_neomodel',
    
    # Local apps
    'graph',
    'pipeline',
    'cms_content',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cms.wsgi.application'

# =============================================================================
# Database (PostgreSQL via SSOT)
# =============================================================================
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=app_settings.database_url,
        conn_max_age=600,
    )
}

# =============================================================================
# Neo4j Configuration (via SSOT)
# =============================================================================
NEOMODEL_NEO4J_BOLT_URL = app_settings.neo4j_bolt_url
NEOMODEL_SIGNALS = True
NEOMODEL_FORCE_TIMEZONE = False

# Expose to other modules
NEO4J_FAKE = app_settings.neo4j_fake
DB_TABLE_PREFIX = app_settings.db_table_prefix

# =============================================================================
# REST Framework + JWT (using simplejwt instead of custom)
# =============================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'SIGNING_KEY': app_settings.jwt_secret_key,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# =============================================================================
# Password validation
# =============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =============================================================================
# Internationalization
# =============================================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =============================================================================
# Static files
# =============================================================================
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# =============================================================================
# Default primary key field type
# =============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# Django Unfold Admin
# =============================================================================
UNFOLD = {
    "SITE_TITLE": "PEG Scanner CMS",
    "SITE_HEADER": "PEG Scanner",
    "SITE_SYMBOL": "monitoring",
    "SHOW_HISTORY": True,
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "navigation": [
            {
                "title": "Dashboard",
                "items": [{"title": "Home", "icon": "home", "link": "/admin/"}],
            },
            {
                "title": "Pipeline",
                "items": [
                    {"title": "Data Batches", "icon": "inventory_2", "link": "/admin/pipeline/databatchproxy/"},
                    {"title": "Crawler Tasks", "icon": "schedule", "link": "/admin/pipeline/crawlertaskproxy/"},
                ],
            },
            {
                "title": "Graph Data",
                "items": [
                    {"title": "Companies", "icon": "business", "link": "/admin/graph/companyproxy/"},
                    {"title": "Quotes", "icon": "candlestick_chart", "link": "/admin/graph/dailyquoteproxy/"},
                ],
            },
            {
                "title": "System",
                "items": [
                    {"title": "Users", "icon": "person", "link": "/admin/auth/user/"},
                ],
            },
        ],
    },
}
