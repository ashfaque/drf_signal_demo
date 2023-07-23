'''
# ? Production - App wise Logger
 
from os.path import abspath, basename, dirname, join, normpath
 
DJANGO_ROOT = dirname(dirname(abspath(__file__)))
 
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },  
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(DJANGO_ROOT, 'debug.log'),
            'when': 'D', # this specifies the interval
            'interval': 1, # defaults to 1, only necessary for other values 
            'backupCount': 5, # how many backup file to keep, 5 days
            # 'maxBytes': 100 * 1024 * 1024,  # 100 MB
            'formatter': 'verbose',
        },
        'sscrm':{
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(DJANGO_ROOT, './sscrm/debug_sscrm.log'),
            'when': 'D', # this specifies the interval
            'interval': 1, # defaults to 1, only necessary for other values 
            'backupCount': 5, # how many backup file to keep, 5 days
            # 'maxBytes': 100 * 1024 * 1024,  # 100 MB
            'formatter': 'verbose',
        },
        'hrms':{
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(DJANGO_ROOT, './hrms/debug_hrms.log'),
            'when': 'D', # this specifies the interval
            'interval': 1, # defaults to 1, only necessary for other values 
            'backupCount': 5, # how many backup file to keep, 5 days
            # 'maxBytes': 100 * 1024 * 1024,  # 100 MB
            'formatter': 'verbose',
        },
 
    },  
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        '': {
            'handlers': ['file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'sscrm': {
            'handlers': ['sscrm'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'hrms': {
            'handlers': ['hrms'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
    },  
}
'''



'''
# ? Staging - Day wise Logger
 
from os.path import abspath, basename, dirname, join, normpath
 
DJANGO_ROOT = dirname(dirname(abspath(__file__)))
 
# Per-day wise logging :-
# -------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(DJANGO_ROOT, 'debug.log'),
            'when': 'D', # this specifies the interval
            'interval': 1, # defaults to 1, only necessary for other values
            'backupCount': 1, # how many backup file to keep, 5 days
            'formatter': 'verbose',
        },
 
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        '': {
            'handlers': ['file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        }
    },
}
'''



'''
# ? SCRM - Size wise Logger
 
from os.path import abspath, basename, dirname, join, normpath
 
DJANGO_ROOT = dirname(dirname(abspath(__file__)))
 
# Logger updated by Ashfaque Alam, July 22, 2023.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(DJANGO_ROOT, 'debug.log'),
            'maxBytes': 100 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'info_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(DJANGO_ROOT, 'info.log'),
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 2,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'django.db.backends': {
            'handlers': ['info_file'],
            'level': 'INFO',
            'propagate': False,
        },
        '': {
            'handlers': ['file', 'info_file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        }
    },
}
'''
