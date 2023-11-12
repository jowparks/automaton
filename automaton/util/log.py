import logging
import os
import sys

api_logger = logging.getLogger('automaton.api')
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
numeric_level = getattr(logging, log_level, None)

if not isinstance(numeric_level, int):
    raise ValueError(f'Invalid log level: {log_level}')

api_logger.setLevel(numeric_level)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
api_logger.addHandler(handler)