"""
!!!!!Для работы без gui необходимо установить альтернативный keyring-backend. 
Как пример "sudo pip3 install keyrings.alt"
При первом запуске для каждого пользователя запрашивается пароль который сохраняется в keyring системы
при последующих запусках, если пароль существует, то операции выполняются автоматически."""

__author__ = "Vyacheslav Sazanov <slava.sazanov@gmail.com>"
__license__ = "GNU Lesser General Public License (LGPL)"

__all__ = ['save_example']
