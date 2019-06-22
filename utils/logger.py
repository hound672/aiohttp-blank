# -*- coding: utf-8 -*-
"""
    core/logging/handlers.py
    ~~~~~~~~~~~~~~~
  
    Расширение штатного обработчика логирования с ротацией логов по времени
"""

from logging.handlers import TimedRotatingFileHandler


class TimedRotatingFileHandlerEx(TimedRotatingFileHandler):
    """
    Расширение базового класса логгирования с возможностью ротации
    """

    def __init__(self, filename):
        super().__init__(filename, when='W0', interval=1, backupCount=10)
