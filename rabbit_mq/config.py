import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Application settings
SECRET_KEY = os.getenv("SECRET_KEY", "test-secret-key")
BASE_URL = os.getenv("BASE_URL", "http://localhost:5001")

# RabbitMQ settings
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")

# SMTP settings for Gmail
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "kolyvanov1455@gmail.com"  # Ваш Gmail адрес
SMTP_PASSWORD = "ifbu bejh ztlp iqrt"  # Пароль приложения для RabbitMQ Auth 