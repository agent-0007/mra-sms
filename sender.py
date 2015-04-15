#!/usr/bin/env python
# coding=utf-8

import socket, string, sys
from struct import *
'''
Конфигурационные данные
'''
LOGIN    = '' # e-mail
PASSWORD = '' # пароль
NUMBER   = '' # номер телефона
TEXT     = "" # текст сообщения
'''
The End of config
'''
PROTO_VERSION         = 0x10008        # версия протокола
CS_MAGIC              = 0xDEADBEEF     # тип магическая хрень (начало заголовка пакета)
MRIM_CS_HELLO         = 0x1001         # приветсвуем сервер
MRIM_CS_HELLO_ACK     = 0x1002         # получаем ответный привет
MRIM_CS_LOGIN2        = 0x1038         # пытаемся залогиниться
MRIM_CS_LOGIN_ACK     = 0x1004         # ответ в случае успешной авторизации
MRIM_CS_SMS           = 0x1039         # шлём СМСку
MRIM_CS_SMS_ACK       = 0x33A          # читаем статус СМСки
MRIM_CS_STATUS_ONLINE = 0x00000001     # логинимся со статусом On-line

# получаем адрес куда будет конектиться
def get_host_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('mrim.mail.ru', 2042))
    s.send("GET / HTTP 1.1\r\n\r\n")
    data = s.recv(128)
    s.close()
    return data
# ф-ция по созданию пакета приветствия
def packet_make(msg, seq=1, mydata=''):
    formt = '<5L'
    dlen = len(mydata)
    my_header = pack(formt, CS_MAGIC, PROTO_VERSION, seq, msg, dlen) + pack('<L', 0)*6
    return my_header
   
# ф-ция авторизации
def mrim_login(login=LOGIN, password=PASSWORD, client='pymra 0.1beta'):
    formt = '<5L'
    mydata = pack('<L', len(login)) + login + pack('<L', len(password)) + password + pack('<L', MRIM_CS_STATUS_ONLINE) + pack('<L', len(client)) + client + pack('<L', 0)*5
    dlen = len(mydata)
    my_header_login = pack(formt, CS_MAGIC, PROTO_VERSION, 2, MRIM_CS_LOGIN2, dlen) + pack('<L', 0)*6 + mydata
    return my_header_login

# ф-ция отправки SMS   
def sms_send(number=NUMBER, text=TEXT):
    formt = '<5L'
    mydata = pack('<L', 0) + pack('<L', len(number)) + number + pack('<L', len(text)) + text
    dlen = len(mydata)
    my_header_sms = pack(formt, CS_MAGIC, PROTO_VERSION, 3, MRIM_CS_SMS, dlen) + pack('<L', 0)*6 + mydata
    return my_header_sms

def main():    
    host_port = get_host_port().split(':') 
    my_header = packet_make(MRIM_CS_HELLO, 1)
    my_header_login = mrim_login()
    my_header_sms = sms_send() 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host_port[0], int(host_port[1])))   
    s.send(my_header)
    data = s.recv(48)
    resp = unpack('12L', data)
    if resp[3] == MRIM_CS_HELLO_ACK:
        print "[+] Подключились!"
    else:
        print "[!] Не подключились!"
        sys.exit(0)
    s.send(my_header_login)
    data_l = s.recv(48)
    resp_l = unpack('12L', data_l)
    if resp_l[3] == MRIM_CS_LOGIN_ACK:
        print "[+] Залогинились!"
    else:
        print "[!] Проверьте логин и пароль!"
        sys.exit(0)
    s.send(my_header_sms)
    data_s = s.recv(48)
    resp_s = unpack('12L', data_s) 
    if resp_s[3] == MRIM_CS_SMS_ACK:
        print "[+] SMS отправили!"
    else:
        print "[!] SMS не отправили :("
        sys.exit(0)
    s.close()
   
if __name__ == "__main__":
    main()
