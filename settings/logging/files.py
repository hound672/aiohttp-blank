import settings

LOGS_DIR = settings.BASE_DIR.joinpath('logs')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'main_formatter': {
            'format': '[%(asctime)s]-[%(levelname)s:%(name)s]-'
                      '[%(filename)s:%(lineno)d]: %(message)s',
            'datefmt': "%d-%m-%y %H:%M:%S",
        },
        'console_formatter': {
            'format': '***** [%(levelname)s:%(name)s]-'
                      '[%(filename)s:%(lineno)d]: %(message)s',
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'console_formatter',
        },
        'needles': {
            'level': 'DEBUG',
            'class': 'utils.logger.TimedRotatingFileHandlerEx',
            'formatter': 'main_formatter',
            'filename': LOGS_DIR.joinpath('needles.log')
        },
        'intermediate': {
            'level': 'DEBUG',
            'class': 'utils.logger.TimedRotatingFileHandlerEx',
            'formatter': 'main_formatter',
            'filename': LOGS_DIR.joinpath('intermediate.log')
        },
        'finish': {
            'level': 'DEBUG',
            'class': 'utils.logger.TimedRotatingFileHandlerEx',
            'formatter': 'main_formatter',
            'filename': LOGS_DIR.joinpath('finish.log')
        },
        'ppod': {
            'level': 'DEBUG',
            'class': 'utils.logger.TimedRotatingFileHandlerEx',
            'formatter': 'main_formatter',
            'filename': LOGS_DIR.joinpath('ppod.log')
        },
        'py_warnings': {
            'level': 'WARNING',
            'class': 'utils.logger.TimedRotatingFileHandlerEx',
            'formatter': 'main_formatter',
            'filename': LOGS_DIR.joinpath('py_warnings.log')
        },
    },
    'loggers': {
        'py.warnings': {
            'handlers': ['py_warnings'],
        },
        'apps.needles': {
            'level': 'DEBUG',
            'handlers': ['needles'],
            'propagate': False
        },
        'apps.intermediate': {
            'level': 'DEBUG',
            'handlers': ['intermediate'],
            'propagate': False
        },
        'apps.finish': {
            'level': 'DEBUG',
            'handlers': ['finish'],
            'propagate': False
        },
        'apps.ppod': {
            'level': 'DEBUG',
            'handlers': ['ppod'],
            'propagate': False
        },
        '': {
            'level': 'INFO',
            'handlers': ['console', 'py_warnings'],
        },
    }
}
