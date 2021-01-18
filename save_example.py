#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#TODO: Добавить обработчик исключений
#TODO: сервисы вывести в константы, или в фаил конфигурации
#TODO: Убрать явные привязки к оборудованиям, сервисам
#TODO: Добавить возможность замены пароля. Допустим по опциям командной строки или переменной в скрипте/файле конфигурации
#TODO: привести к PEP8
#TODO: Сделать пакетом, что бы подтягивал зависимости

__author__ = "Vyacheslav Sazanov <slava.sazanov@gmail.com>"
__license__ = "GNU Lesser General Public License (LGPL)"

"""
!!!!!Для работы без gui необходимо установить альтернативный keyring-backend. Как пример "sudo pip3 install keyrings.alt"
При первом запуске для каждого пользователя запрашивается пароль который сохраняется в keyring системы
при последующих запусках, если пароль существует, то операции выполняются автоматически."""

import configparser
import datetime
from time import sleep
import paramiko
import keyring
from getpass import getpass

#TODO: Добавить удаление, изменение паролей.
class Password:
    """Класс для хранения паролей в keyring
    Если пароль для пользователя и сервиса отсутствует в системе, то необходимо его ввеси
    """

    def __init__(self, service_name: str, user: str):
        """
        При создании экзепляра класса, проверяет что пароль для сервиса и пользователя существует.
        Иначе выдает запрос на ввод пароля.
        :param service_name: str
            Имя сервиса для сохранения паролей
        :param user: str
            Имя пользователя для сохранения паролей
        """
        self._user = user
        self._service_name = service_name
        self._password = ''
        if keyring.get_password(service_name, user):
            pass
        else:
            self._password = getpass(
                prompt='Enter password for service {0} and user {1}:'.format(self._service_name, self._user))
            self._set_password()

    def _set_password(self):
        """
        Записывает пароль в keyring
        :return:
        """
        keyring.set_password(self._service_name, self._user, self._password)

    def get_password(self) -> str:
        """
        :return: str
            Возвращает пароль из keyring.
        """
        self._password = keyring.get_password(self._service_name, self._user)
        return self._password


class OPTIONS:
    def __init__(self, section: str):
        """
        :param section: str
            Секция для чтения опций.
        """
        self.config_file = 'settings.ini'
        self.section = section

    def get_config(self) -> dict:
        """
        Парсит конфигурационный фаил возвращает опции подключения к ssh
        :return: dict
            Возвращает словать в виде опция : значение
        """
        config = configparser.ConfigParser()
        config.read(self.config_file)
        ssh_config_dict = {}
        for key, value in config[self.section].items():
            ssh_config_dict[key] = value
        return ssh_config_dict


class Backup:

    def __init__(self, ssh_config_dict: dict, ftp_config_dict: dict):
        """
        :param ssh_config_dict:
            Параметры подключения к ssh
        :param ftp_config_dict:
            Параметры подключения к ftp
        """
        self.ssh_config_dict = ssh_config_dict
        self.ftp_config_dict = ftp_config_dict

    def config_backup(self):
        """
        Выполняет резервное копирование
        :return:
        """
        cur_data = str(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M"))
        cli_backup = 'copy /noconfirm run ftp://' + self.ftp_config_dict['user'] + ':' + self.ftp_config_dict[
            'password'] + '@' + self.ftp_config_dict['host'] + '/Backup_network_devices/12_cisco-asa/' + cur_data + '\n'
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(hostname=self.ssh_config_dict['host'],
                               username=self.ssh_config_dict['user'],
                               password=self.ssh_config_dict['password'],
                               look_for_keys=False,
                               allow_agent=False)
        except KeyError:
            print('Неправильные параметры в конфигурационном файле. Невозможно подключиться по ssh')

        else:
            with ssh_client.invoke_shell() as asa_ssh:
                print(asa_ssh.recv(60000).decode('utf-8'))
                asa_ssh.send('enable\n')
                sleep(2)
                print(asa_ssh.recv(60000).decode('utf-8'))
                asa_ssh.send(self.ssh_config_dict['enable'] + '\n')
                sleep(3)
                print(asa_ssh.recv(60000).decode('utf-8'))
                asa_ssh.send(cli_backup)
                print(asa_ssh.recv(60000).decode('utf-8'))


if __name__ == '__main__':
    #Получение конфигурации для подключения к ASA
    ssh_config_dict = OPTIONS('ASA').get_config()
    #Получение пароля для ssh
    ssh_config_dict['password'] = Password('asa_ssh_pass', ssh_config_dict['user']).get_password()
    #Получение enable пароля
    ssh_config_dict['enable'] = Password('asa_en_pass', ssh_config_dict['user']).get_password()
    #Получение конфигурации ftp
    ftp_config_dict = OPTIONS('FTP').get_config()
    #Получение пароля ftp
    ftp_config_dict['password'] = Password('ftp_pass', ftp_config_dict['user']).get_password()
    #Создание экземпляра класса Бекап
    backup = Backup(ssh_config_dict, ftp_config_dict)
    #Запуск резервного копирования
    backup.config_backup()
