import socket
import threading


# 群聊 - 客户端
class ClientBot:
    """
        host -> 地址
        port -> 端口
    """
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = input("Enter your username: ")

    def receive_message(self):
        while True:
            try:
                message = self.socket.recv(1024).decode("utf-8")
                if message:
                    print(message)
                else:
                    print("Disconnected from server")
                    self.socket.close()
                    break
            except Exception as e:
                print("Error receiving message:", e)
                self.socket.close()
                break

    def send_message(self):
        join_message = f"[{self.username}] joined the chat"
        self.socket.send(self.username.encode("utf-8"))  # Send username as the first message
        self.socket.send(join_message.encode("utf-8"))  # Send join notification
        while True:
            message = input("")
            message = f"[{self.username}] {message}"  # Prefix message with username
            try:
                self.socket.send(message.encode("utf-8"))
            except Exception as e:
                print("Error sending message:", e)
                self.socket.close()
                break

    def start(self):
        try:
            self.socket.connect((self.host, self.port))
            print("Connected to server.")
            threading.Thread(target=self.receive_message).start()
            self.send_message()
        except Exception as e:
            print("Connection error:", e)
            self.socket.close()

if __name__ == "__main__":
    client = Client()
    client.run()