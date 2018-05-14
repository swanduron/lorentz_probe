import paramiko
import subprocess
import config
import configparser
import json
import time
import threading
import re
import logging
from logging import handlers


def ssh_link(ip, username, password):
    try:
        ssh_shooter = paramiko.SSHClient()
        ssh_shooter.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_shooter.connect(ip, 22, username, password, timeout=5)
        stdin, stdout, stderr = ssh_shooter.exec_command('vim-cmd vmsvc/getallvms')
        vm_vmid_list = []
        vms_res_list = stdout.readlines()
        vms_res_list = [i.decode() for i in vms_res_list]
        for each_line in vms_res_list:
            if re.match('\d', each_line):
                vm_vmid_list.append(each_line.split()[0])
        for each_vm in vm_vmid_list:
            stdin, stdout, stderr = ssh_shooter.exec_command('vim-cmd vmsvc/power.shutdown %s' % each_vm)
        time.sleep(30)
        for each_vm in vm_vmid_list:
            stdin, stdout, stderr = ssh_shooter.exec_command('vim-cmd vmsvc/power.off %s' % each_vm)
    except Exception as e:
        print(e)


def ssh_worker(working_json):
    server_list = list(working_json.keys())
    server_list.remove('default')
    for each_server in server_list:
        server_info_obj = working_json[each_server]
        ip = server_info_obj['ip']
        username = server_info_obj['username']
        password = server_info_obj['password']
        print('push command to host [%s]' % ip)
        threading.Thread(target=ssh_link, args=(ip, username, password)).start()



def ping_probe(working_json):
    ping_list = working_json['default']['ping_list']
    print('Do ping test at >>:', ping_list)
    for ip_index in range(len(ping_list)):
        each_ip = working_json['default']['ping_list'][ip_index]
        ping_command = config.PING_CMD_TEMPLATE.format(ip=each_ip)
        echo = subprocess.Popen(ping_command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ping_res = echo.stdout.read().decode()
        print('ping_res >>:', ping_res)
        if 'time=' in ping_res:
            working_json['default']['ping_timestamp'][ip_index] = int(time.time())


def get_config_file(renew_flag=False, load_flag=True):
    if renew_flag:
        config_ini = configparser.ConfigParser()
        config_ini['DEFAULT'] = {'Shutdown_interval':'1800', 'ping_list':'1.1.1.1,2.2.2.2'}
        config_ini['server1'] = {'ServerIP':'11.11.11.11', 'Username':'admin', 'Password':'admin'}
        with open(config.INI_FILE_PATH, mode='w') as ini_file_obj:
            config_ini.write(ini_file_obj)
        print('New server information file [server_info.ini] has been generated.')
    if load_flag:
        working_json = {}
        try:
            config_ini = configparser.ConfigParser()
            config_ini.read(config.INI_FILE_PATH)
            server_list = config_ini.sections()
            for each_server in server_list:
                each_server = each_server.lower()
                working_json[each_server] = {}
                working_json[each_server]['ip'] = config_ini[each_server]['serverip']
                working_json[each_server]['username'] = config_ini[each_server]['username']
                working_json[each_server]['password'] = config_ini[each_server]['password']
            working_json['default'] = {}
            working_json['default']['ping_list'] = [i.strip() for i in config_ini['DEFAULT']['ping_list'].split(',')]
            working_json['default']['ping_timestamp'] = [int(time.time()) for i in range(len(working_json['default']['ping_list']))]
            working_json['default']['shutdown_interval'] = int(config_ini['DEFAULT']['Shutdown_interval'])
            with open(config.JSON_FILE_PATH, mode='w') as json_file_obj:
                json.dump(working_json, json_file_obj, indent=2)
            return working_json
        except Exception as e:
            print('Exception is [%s]' % e)



def check_ping_status(working_json):
    current_timestamp = int(time.time())
    ping_timestamp = working_json['default']['ping_timestamp']
    time_check_res = [i for i in filter(lambda x:abs(x - current_timestamp) < working_json['default']['shutdown_interval'],
                                        ping_timestamp)]
    print('All status is>>:',current_timestamp, ping_timestamp)
    if not time_check_res:
        ssh_worker(working_json)