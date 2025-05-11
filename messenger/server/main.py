import grpc
import time
from concurrent import futures
from typing import Dict, List, Set
import threading
import queue
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import messenger_pb2
import messenger_pb2_grpc

class MessengerServicer(messenger_pb2_grpc.MessengerServicer):
    def __init__(self):
        self.message_queues: Dict[str, queue.Queue] = {}
        self.active_users: Set[str] = set()
        self.lock = threading.Lock()

    def SendMessage(self, request, context):
        print(f"Получено сообщение от {request.sender} для {request.to}: {request.content}")
        
        if request.sender not in self.active_users:
            print(f"Ошибка: отправитель {request.sender} не активен")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Отправитель {request.sender} не активен")
            return messenger_pb2.Empty()

        with self.lock:
            if request.to not in self.message_queues:
                self.message_queues[request.to] = queue.Queue()
            self.message_queues[request.to].put(request)
            print(f"Сообщение добавлено в очередь для {request.to}")

        return messenger_pb2.Empty()

    def ReceiveMessages(self, request, context):
        username = request.username
        print(f"Новое подключение от пользователя {username}")
        
        with self.lock:
            self.active_users.add(username)
            if username not in self.message_queues:
                self.message_queues[username] = queue.Queue()
            print(f"Активные пользователи: {self.active_users}")

        try:
            while context.is_active():
                try:
                    message = self.message_queues[username].get(timeout=1)
                    print(f"Отправка сообщения от {message.sender} для {username}")
                    yield message
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Ошибка при отправке сообщения: {e}")
                    break

        finally:
            with self.lock:
                if username in self.active_users:
                    self.active_users.remove(username)
                    print(f"Пользователь {username} отключился. Осталось пользователей: {len(self.active_users)}")
                if username in self.message_queues:
                    del self.message_queues[username]

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    messenger_pb2_grpc.add_MessengerServicer_to_server(
        MessengerServicer(), server
    )
    server.add_insecure_port('[::]:5001')
    server.start()
    print("Сервер запущен на порту 5001")
    server.wait_for_termination()

if __name__ == '__main__':
    serve() 