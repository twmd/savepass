#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#TODO: Добавить аннотации
#TODO: Добавить обработчик исключений
#TODO: сервисы вывести в константы, или в фаил конфигурации
#TODO: Убрать явные привязки к оборудованиям, сервисам
#TODO: Добавить возможность замены пароля. Допустим по опциям командной строки или переменной в скрипте/файле конфигурации
#TODO: привести к PEP8
"""При первом запуске для каждого пользователя запрашивается пароль который сохраняется в keyring системы
при последующих запусках, если пароль существует, то операции выполняются автоматически."""

import configparser
import datetime
from time import sleep
import paramiko
import keyring
from getpass import getpass


class Password:
    """Класс для хранения паролей в keyring
    Если пароль для пользователя и системы отсутствует в системе, то необходимо его ввеси
    """

    def __init__(self, service_name, user):
        self.user = user
        self.service_name = service_name
        self.password = ''
        if keyring.get_password(service_name, user):
            pass
        else:
            self.password = getpass(
                prompt='Enter password for service {0} and user {1}:'.format(self.service_name, self.user))
            keyring.set_password(service_name, user, self.password)

    def get_password(self):
        self.password = keyring.get_password(self.service_name, self.user)
        return self.password


class OPTIONS:
    def __init__(self, section):
        self.config_file = 'settings.ini'
        self.section = section

    def get_config(self):
        """Парсит конфигурационный фаил возвращает опции подключения к ssh"""
        config = configparser.ConfigParser()
        config.read(self.config_file)
        ssh_config_dict = {}
        for key, value in config[self.section].items():
            ssh_config_dict[key] = value
        return ssh_config_dict


class ASA_BACKUP:

    def __init__(self, ssh_config_dict, ftp_config_dict):
        self.ssh_config_dict = ssh_config_dict
        self.ftp_config_dict = ftp_config_dict

    def asa_backup(self):
        cur_data = str(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M"))
        cli_backup = 'copy /noconfirm run ftp://' + self.ftp_config_dict['user'] + ':' + self.ftp_config_dict[
            'password'] + '@' + self.ftp_config_dict['host'] + '/Backup_network_devices/12_cisco-asa/' + cur_data + '\n'
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=self.ssh_config_dict['host'],
                           username=self.ssh_config_dict['user'],
                           password=self.ssh_config_dict['password'],
                           look_for_keys=False,
                           allow_agent=False)
        with ssh_client.invoke_shell() as asa_ssh:
            asa_ssh.send('enable\n')
            sleep(2)
            asa_ssh.send(self.ssh_config_dict['enable'] + '\n')
            sleep(3)
            asa_ssh.send(cli_backup)


if __name__ == '__main__':
    ssh_config_dict = OPTIONS('ASA').get_config()
    ssh_config_dict['password'] = Password('asa_ssh_pass', ssh_config_dict['user']).get_password()
    ssh_config_dict['enable'] = Password('asa_en_pass', ssh_config_dict['user']).get_password()
    ftp_config_dict = OPTIONS('FTP').get_config()
    ftp_config_dict['password'] = Password('ftp_pass', ftp_config_dict['user']).get_password()
    backup = ASA_BACKUP(ssh_config_dict, ftp_config_dict)
    backup.asa_backup()
