Video: https://drive.google.com/file/d/1ajCNkkvu8qhX0yVGXyFuYhufgSIRFGMr/view?usp=sharing

# gRPC Messenger

Простой мессенджер на основе gRPC с поддержкой двусторонней потоковой передачи сообщений c консольным и веб интерфейсом на React.

## Установка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Сгенерируйте код из proto-файла:
```bash
python -m grpc_tools.protoc -I./proto -I./venv/lib/python3.11/site-packages --python_out=. --grpc_python_out=. ./proto/messenger.proto
```

## Запуск

### Консольный клиент

1. Запустите сервер:
```bash
python server/main.py
```

2. В другом терминале запустите клиент:
```bash
python client/main.py
```

### Веб-интерфейс

1. Запустите сервер (если еще не запущен):
```bash
python server/main.py
```

2. В другом терминале запустите веб-интерфейс:
```bash
cd web
python run.py
```

3. Откройте браузер и перейдите по адресу http://localhost:8000
