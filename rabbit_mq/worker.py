import pika
import json
import jwt
from datetime import datetime, timedelta, timezone
from config import RABBITMQ_URL, BASE_URL, SECRET_KEY
from email_sender import send_email

def create_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = timedelta(minutes=1)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def process_message(ch, method, properties, body):
    try:
        data = json.loads(body)
        email_type = data.get('type')
        email_data = data.get('data', {})
        if email_type == 'registration':
            token = create_token({'email': email_data['to'], 'action': 'set_password'})
            set_password_url = f"{BASE_URL}/set-password?token={token}"
            send_email(
                to_email=email_data['to'],
                subject='Завершите регистрацию',
                html_content=f"""
                <h1>Добро пожаловать!</h1>
                <p>Для завершения регистрации, пожалуйста, установите пароль.</p>
                <p>Перейдите по ссылке для установки пароля:</p>
                <p><a href="{set_password_url}">Установить пароль</a></p>
                <p>Ссылка действительна 1 минуту.</p>
                """
            )
        elif email_type == 'password_recovery':
            token = create_token({'email': email_data['to'], 'action': 'recover_password'})
            set_password_url = f"{BASE_URL}/set-password?token={token}"
            send_email(
                to_email=email_data['to'],
                subject='Восстановление пароля',
                html_content=f"""
                <h1>Восстановление пароля</h1>
                <p>Для восстановления пароля перейдите по ссылке:</p>
                <p><a href=\"{set_password_url}\">Восстановить пароль</a></p>
                <p>Ссылка действительна 1 минуту.</p>
                """
            )
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"Обработано сообщение типа: {email_type}")
    except Exception as e:
        print(f"Ошибка при обработке сообщения: {str(e)}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue='email_queue', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue='email_queue',
        on_message_callback=process_message
    )
    print('Воркер запущен и ожидает сообщения...')
    channel.start_consuming()

if __name__ == '__main__':
    main() 