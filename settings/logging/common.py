# -*- coding: utf-8 -*-
"""
    common
    ~~~~~~~~~~~~~~~
  

"""

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console_formatter': {
            'format': '[%(asctime)s]-[%(levelname)s:%(name)s]-'
                      '[%(filename)s:%(lineno)d]: %(message)s',
            'datefmt': "%d-%m-%y %H:%M:%S",
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console_formatter',
        },
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    }
}