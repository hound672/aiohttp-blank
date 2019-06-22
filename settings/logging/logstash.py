# -*- coding: utf-8 -*-
"""
    logstash
    ~~~~~~~~~~~~~~~
  

"""

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'logstash': {
            '()': 'logstash_async.formatter.LogstashFormatter',
            'message_type': 'ggg',
            'fqdn': False,  # Fully qualified domain name. Default value: false.
            'extra_prefix': 'dev'
        },
    },
    'handlers': {
        'logstash': {
            'level': 'DEBUG',
            'class': 'logstash_async.handler.AsynchronousLogstashHandler',
            'formatter': 'logstash',
            'transport': 'logstash_async.transport.TcpTransport',
            'host': '192.168.75.131',
            'port': 5000,
            'database_path': 'logstash.db',
        },
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['logstash'],
        },
    }
}