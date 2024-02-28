import socket
import threading
import json
import logging
from queue import Queue


# 群聊 - 服务端
class ServerBot:
    """
        host -> 地址
        port -> 端口
    """
    def __init__(self, host='127.0.0.1', port=8888):
        # 创建一个socket对象
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置地址和端口
        self.host = host
        self.port = port
        # 保存所有连接到服务器的客户端对象
        self.clients = {}
        # 保存所有连接到服务器的客户端地址
        self.addresses = {}
        # 用于存放等待处理的客户端对象
        self.queue = Queue()
        # 设置日志输出格式
        logging.basicConfig(level=logging.INFO)

    def start(self):
        # 绑定地址和端口
        self.socket.bind((self.host, self.port))
        # 监听连接请求
        self.socket.listen(10)
        # 输出服务器启动信息
        logging.info("Server started and listening on {}:{}".format(self.host, self.port))
        # 创建一个线程来处理接受新连接的请求
        accept_thread = threading.Thread(target=self.accept_incoming_connections)
        accept_thread.start()
        # 等待线程结束
        accept_thread.join()
        # 关闭socket
        self.socket.close()

    def accept_incoming_connections(self):
        # 循环接受新连接
        while True:
            # 接受新连接
            client, client_address = self.socket.accept()
            # 输出连接信息
            logging.info("{} has connected.".format(client_address))
            # 将客户端对象添加到队列中
            self.queue.put(client)
            # 创建一个线程来处理客户端请求
            threading.Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):
        try:
            # 循环处理客户端请求
            while True:
                # 接受客户端发送的消息
                msg = client.recv(1024).decode("utf8")
                # 如果消息不为空，则将消息广播给所有客户端
                if msg != "":
                    logging.info("Received message: {}".format(msg))
                    self.broadcast(msg, client)
                # 如果消息为空，则表示客户端已经断开连接
                else:
                    raise Exception("Client disconnected")
        # 捕获处理客户端请求时的异常
        except Exception as e:
            logging.error("Error handling client: {}".format(e))
            # 关闭客户端连接
            client.close()
            # 将客户端对象从队列中移除
            self.remove_client(client)

    def broadcast(self, msg, sender):
        # 遍历队列中的所有客户端对象
        for client in self.queue.queue:
            # 如果客户端不是消息发送者，则将消息发送给该客户端
            if client != sender:
                try:
                    client.send(msg.encode("utf8"))
                # 捕获发送消息时的异常
                except Exception as e:
                    logging.error("Error broadcasting to {}: {}".format(client, e))
                    # 关闭客户端连接
                    client.close()
                    # 将客户端对象从队列中移除
                    self.remove_client(client)

    def remove_client(self, client):
        # 将客户端对象从队列中移除
        if client in self.queue.queue:
            self.queue.queue.remove(client)
