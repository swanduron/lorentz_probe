import paramiko
import subprocess
import config
import configparser
import os
import json
import time
import threading


def ssh_worker(working_json):
    server_list = working_json.keys()
    server_list.remove('default')
    for each_server in server_list:
        server_info_obj = working_json[each_server]


def ping_probe(working_json):
    ping_list = working_json['default']['ping_list']
    for ip_index in range(len(ping_list)):
        each_ip = working_json['default']['ping_list'][ip_index]
        ping_command = config.PING_CMD_TEMPLATE.format({'ip':each_ip})
        echo = subprocess.Popen(ping_command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ping_res = echo.stdout.read().decode()
        if 'time=' in ping_res:
            working_json['default']['ping_timestamp'][ip_index] = int(time.time())

def get_config_file(renew_flag=False):
    if renew_flag:
        config_ini = configparser.ConfigParser()
        config_ini['DEFAULT'] = {'Shutdown_interval':'1800', 'ping_list':'1.1.1.1,2.2.2.2'}
        config_ini['server1'] = {'ServerIP':'11.11.11.11', 'Username':'admin', 'Password':'admin'}
        with open(config.INI_FILE_PATH, mode='w') as ini_file_obj:
            config_ini.write(ini_file_obj)
        print('New server information file [server_info.ini] has been generated.')
    else:
        working_json = {}
        try:
            config_ini = configparser.ConfigParser()
            config_ini.read(config.INI_FILE_PATH)
            server_list = config_ini.sections()
            for each_server in server_list:
                each_server = each_server.lower()
                working_json[each_server] = {}
                working_json[each_server]['ip'] = config_ini[each_server]['ServerIP']
                working_json[each_server]['username'] = config_ini[each_server]['Username']
                working_json[each_server]['password'] = config_ini[each_server]['Password']
            working_json['default'] = {}
            working_json['default']['ping_list'] = [i.strip() for i in config_ini['DEFAULT']['Ping_target'].split(',')]
            working_json['default']['ping_timestamp'] = [int(time.time()) for i in range(len(working_json['default']['ping_list']))]
            working_json['default']['shutdown_interval'] = int(config_ini['DEFAULT']['Shutdown_interval'])
            with open(config.JSON_FILE_PATH, mode='w') as json_file_obj:
                json.dump(working_json, json_file_obj, indent=2)
            return working_json
        except Exception as e:
            print(e)