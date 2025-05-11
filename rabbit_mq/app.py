from flask import Flask, request, jsonify, render_template_string
import pika
import json
import jwt
from datetime import datetime, timedelta
from config import RABBITMQ_URL, SECRET_KEY
import logging
from email_sender import send_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Срок действия токена истек")
    except jwt.InvalidTokenError:
        raise Exception("Недействительный токен")


def get_rabbitmq_channel():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue='email_queue', durable=True)
    return channel, connection


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    try:
        channel, connection = get_rabbitmq_channel()
        message = {
            'type': 'registration',
            'data': {
                'to': email
            }
        }
        logger.info(f"Отправка сообщения в очередь: {message}")
        channel.basic_publish(
            exchange='',
            routing_key='email_queue',
            body=json.dumps(message)
        )
        connection.close()
        logger.info("Сообщение успешно отправлено в очередь")
        return jsonify({'message': 'Registration email will be sent'}), 200
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/set-password', methods=['GET', 'POST'])
def set_password():
    if request.method == 'GET':
        token = request.args.get('token')
        if not token:
            return "Token is required", 400
        try:
            payload = verify_token(token)
            # HTML-форма для установки пароля
            return render_template_string('''
                <h2>Установка пароля для {{ email }}</h2>
                <form method="post">
                    <input type="hidden" name="token" value="{{ token }}">
                    <input type="password" name="password" placeholder="Введите новый пароль" required>
                    <button type="submit">Установить пароль</button>
                </form>
            ''', email=payload['email'], token=token)
        except Exception as e:
            return f"Ошибка: {str(e)}", 400

    elif request.method == 'POST':
        token = request.form.get('token')
        password = request.form.get('password')
        if not token or not password:
            return "Token and password are required", 400
        try:
            payload = verify_token(token)
            #TODO save to db

            send_email(
                to_email=payload['email'],
                subject='Ваша регистрация успешно завершена',
                html_content=f"""
                    <h1>Поздравляем!</h1>
                    <p>Вы успешно завершили регистрацию на сайте.</p>
                """
            )

            return "Пароль успешно установлен!"
        except Exception as e:
            return f"Ошибка: {str(e)}", 400

@app.route('/recover-password', methods=['POST'])
def recover_password():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    try:
        channel, connection = get_rabbitmq_channel()
        message = {
            'type': 'password_recovery',
            'data': {
                'to': email,
                'recovery_link': "http://example.com/recover?token=123"
            }
        }
        logger.info(f"Отправка сообщения в очередь: {message}")
        channel.basic_publish(
            exchange='',
            routing_key='email_queue',
            body=json.dumps(message)
        )
        connection.close()
        logger.info("Сообщение успешно отправлено в очередь")
        return jsonify({'message': 'Password recovery email will be sent'}), 200
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 