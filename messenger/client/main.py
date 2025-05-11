import grpc
import threading
import time
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import messenger_pb2
import messenger_pb2_grpc

class MessengerClient:
    def __init__(self, username: str):
        self.username = username
        self.channel = grpc.insecure_channel('localhost:5001')
        self.stub = messenger_pb2_grpc.MessengerStub(self.channel)
        self.receive_thread = None
        self.is_running = True

    def send_message(self, to: str, content: str):
        message = messenger_pb2.Message(
            sender=self.username,
            to=to,
            content=content,
            timestamp=int(time.time())
        )
        try:
            print(f"Отправка сообщения: {message}")
            self.stub.SendMessage(message)
            print(f"[{datetime.fromtimestamp(message.timestamp)}] Вы -> {to}: {content}")
        except grpc.RpcError as e:
            print(f"Ошибка при отправке сообщения: {e}")

    def receive_messages(self):
        request = messenger_pb2.User(username=self.username)
        try:
            print(f"Начинаю получать сообщения для пользователя {self.username}")
            for message in self.stub.ReceiveMessages(request):
                timestamp = datetime.fromtimestamp(message.timestamp)
                print(f"[{timestamp}] {message.sender} -> Вы: {message.content}")
        except grpc.RpcError as e:
            print(f"Ошибка при получении сообщений: {e}")
            self.is_running = False

    def start(self):
        print(f"Добро пожаловать, {self.username}!")
        print("Для выхода введите 'exit'")
        print("Для отправки сообщения используйте формат: 'to:username message'")

        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        while self.is_running:
            try:
                user_input = input("> ").strip()
                if user_input.lower() == 'exit':
                    self.is_running = False
                    break

                if user_input.startswith('to:'):
                    parts = user_input[3:].strip().split(' ', 1)
                    if len(parts) == 2:
                        to, content = parts
                        if to and content:
                            self.send_message(to, content)
                        else:
                            print("Неверный формат. Используйте: 'to:username message'")
                    else:
                        print("Неверный формат. Используйте: 'to:username message'")
                else:
                    print("Неверный формат. Используйте: 'to:username message'")

            except KeyboardInterrupt:
                self.is_running = False
                break
            except Exception as e:
                print(f"Ошибка: {e}")

        self.channel.close()

def main():
    username = input("Введите ваш никнейм: ").strip()
    if not username:
        print("Никнейм не может быть пустым")
        return

    client = MessengerClient(username)
    client.start()

if __name__ == '__main__':
    main() 