'''
@Author: Voyage
@Date: 2020-05-11 20:59:33
@LastEditTime: 2020-05-11 21:22:08
@Description: flow repeater main class
@FilePath: \flow_repeater\socket_class.py
'''
import gevent
from gevent import socket, monkey
monkey.patch_all()


class FlowRepeater(object):

    def __init__(self, local_listen_addr, local_listen_port, target_ip, target_port):
        self.local_listen_addr = local_listen_addr
        self.local_listen_port = local_listen_port
        self.target_ip = target_ip
        self.target_port = target_port
    
    def listen(self):
        local_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            local_server.bind((self.local_listen_addr, self.local_listen_port))
        except Exception as e:
            print(e)
        local_server.listen(20)
        while True:
            local_conn, local_addr = local_server.accept()
            gevent.spawn(self.tcp_forward_request, local_conn)
    
    def forward_request(self, local_conn):
        remote_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_conn.connect((self.target_ip, self.target_port))