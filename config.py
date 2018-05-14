import os

PING_CMD_TEMPLATE = 'ping {ip} -c 3'
INI_FILE_PATH = os.path.join(os.path.abspath(os.curdir), 'server_info.ini')
JSON_FILE_PATH = os.path.join(os.path.abspath(os.curdir), 'server_info.json')
LOGGING_FILE_PATH = os.path.join(os.path.abspath(os.curdir), 'probe_log.json')