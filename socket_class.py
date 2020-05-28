# -*- encoding: utf-8 -*-
'''
@Time    :   2020/05/28
@Author  :   Voyage/YH21219
'''
from IPy import IP
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread


class NetForward(object):

    def __init__(self, listen_port, remote_ipaddr, remote_port, listen_addr="0.0.0.0"):
        #  listen_addr 本机监听地址 0.0.0.0 代表接收所有的流量
        #  listen_port 本机监听端口
        #  remote_ipaddr  远程ip地址
        #  remote_port 远程端口
        self.listen_addr = listen_addr
        self.listen_port = listen_port
        self.remote_ipaddr = remote_ipaddr
        self.remote_port = remote_port

    def init_check(self):
        try:
            IP(self.listen_addr)._ipversion
            IP(self.remote_ipaddr)._ipversion
        except:
            exit()
        if not isinstance(self.listen_port, int) or not isinstance(self.remote_port, int):
            print("端口必须为整数")
            exit()
        assert self.listen_port > 1 and self.listen_port <= 65535, "端口数必须在2-65535之间"
        assert self.remote_port > 1 and self.remote_port <= 65535, "端口数必须在2-65535之间"

    def socket_server(self):        # 本机监听socket
        local_server = socket(AF_INET, SOCK_STREAM)
        local_server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        try:
            local_server.bind((self.listen_addr, self.listen_port))
        except Exception as e:
            print(e)
            return
        return local_server

    def socket_client(self):    # 本机客户端连接远程socket
        remote_conn = socket(AF_INET, SOCK_STREAM)
        try:
            remote_conn.connect((self.remote_ipaddr, self.remote_port))
        except Exception as e:
            print(e)
            return
        return remote_conn

    def deal_netflow(self, local_conn, remote_conn):
        if not local_conn or not remote_conn:
            return
        while True:
            try:
                data = local_conn.recv(4096)
            except Exception as e:
                print(e)
                break
            if not data:
                break
            try:
                remote_conn.sendall(data)
            except Exception as e:
                print(e)
                break
        local_conn.close()
        remote_conn.close()

    def tcp_request_deal(self, local_conn):     # 流量请求处理
        remote_conn = self.socket_client()
        if not remote_conn:
            return
        Thread(target=self.deal_netflow, args=(
            local_conn, remote_conn)).start()
        Thread(target=self.deal_netflow, args=(
            remote_conn, local_conn)).start()

    def listen(self):
        self.init_check()
        local_server = self.socket_server()
        if not local_server:
            return
        local_server.listen(30)
        print("local listen port:{0} remoteip:{1} remoteport:{2}".format(
            self.listen_port, self.remote_ipaddr, self.remote_port))
        while True:
            local_conn, local_addr = local_server.accept()
            Thread(target=self.tcp_request_deal, args=(local_conn,)).start()


if __name__ == "__main__":
    s = NetForward(12345, "************", 23456, "0.0.0.0")
    # 本机监听端口，远程ip地址，远程接收端口，本机监听地址
    s.listen()

