import telebot
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telebot import types

# Ваш токен, полученный от BotFather
API_TOKEN = '7337273145:AAER3jUxmD-8L_ZQtneWm1hQsjpRCd2AQGA'
bot = telebot.TeleBot(API_TOKEN)

# Данные для отправки письма
YANDEX_EMAIL = 'artemkbnv@yandex.ru'  # Замените на ваш Yandex email
YANDEX_PASSWORD = 'zrzdfbponlyxleei'  # Замените на ваш пароль
RECIPIENT_EMAIL = 'deofso.production@yandex.ru'  # Адрес, на который будут отправляться заявки

# Словарь для хранения данных пользователя
user_data = {}

# Функция для старта диалога
@bot.message_handler(commands=['start'])
def start_dialog(message):
    user_id = message.chat.id
    user_data[user_id] = {}  # Сбрасываем данные пользователя
    bot.send_message(user_id, "🖐Здравствуйте! \nМеня зовут Deofso Production bot, я здесь, чтобы помочь Вам \nДавайте знакомиться🙂🙂🙂")
    bot.send_message(user_id, "Пожалуйста, напишите Ваше имя")

# Обработчик для получения полного имени
@bot.message_handler(func=lambda message: message.chat.id in user_data and 'full_name' not in user_data[message.chat.id])
def get_full_name(message):
    user_id = message.chat.id
    user_data[user_id]['full_name'] = message.text
    bot.send_message(user_id, "Спасибо! \nНапишите свой номер телефона, чтобы мы смогли с Вами связаться для уточнения подробностей.📲")

# Обработчик для получения номера телефона
@bot.message_handler(func=lambda message: message.chat.id in user_data and 'phone_number' not in user_data[message.chat.id])
def get_phone_number(message):
    user_id = message.chat.id
    user_data[user_id]['phone_number'] = message.text
    bot.send_message(user_id, "Прекрасно! \nТеперь расскажите, какой тип услуги или продукта Вас интересует?\n(можно несколько)")

# Обработчик для получения типа услуги или продукта
@bot.message_handler(func=lambda message: message.chat.id in user_data and 'service_type' not in user_data[message.chat.id])
def get_service_type(message):
    user_id = message.chat.id
    user_data[user_id]['service_type'] = message.text
    bot.send_message(user_id, "Отлично! \nКакой бюджет Вы готовы выделить на этот проект(ы)?💰")

# Обработчик для получения бюджета
@bot.message_handler(func=lambda message: message.chat.id in user_data and 'budget' not in user_data[message.chat.id])
def get_budget(message):
    user_id = message.chat.id
    user_data[user_id]['budget'] = message.text
    bot.send_message(user_id, "Замечательно! \nИ последнее, в какие сроки Вы хотели бы реализовать этот проект?🕓")

# Обработчик для получения сроков реализации
@bot.message_handler(func=lambda message: message.chat.id in user_data and 'deadline' not in user_data[message.chat.id])
def get_deadline(message):
    user_id = message.chat.id
    user_data[user_id]['deadline'] = message.text
    bot.send_message(user_id, "Спасибо за Вашу информацию! \nМы свяжемся с Вами в ближайшее время, чтобы обсудить детали Вашего проекта😉")
    send_email(user_data[user_id])  # Отправляем данные на почту

    # Создаем клавиатуру с кнопками "Сначала" и "Выйти"
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Сначала', 'Выйти')
    bot.send_message(user_id, "Хотите начать сначала или выйти?", reply_markup=markup)

# Обработчик для кнопок "Сначала" и "Выйти"
@bot.message_handler(func=lambda message: message.text in ['Сначала', 'Выйти'])
def handle_buttons(message):
    user_id = message.chat.id

    if message.text == 'Сначала':
        user_data.pop(user_id, None)  # Удаляем историю диалога пользователя
        bot.send_message(user_id, "Начинаем сначала. Пожалуйста, напишите Ваше имя.")
        start_dialog(message)  # Запускаем диалог сначала

    elif message.text == 'Выйти':
        user_data.pop(user_id, None)  # Удаляем историю диалога пользователя
        bot.send_message(user_id, "✅Спасибо за заявку! Хорошего дня😉")
        bot.send_message(user_id, "Для начала нового диалога введите /start", reply_markup=types.ReplyKeyboardRemove())

# Функция для отправки данных на почту
def send_email(data):
    msg = MIMEMultipart()
    msg['From'] = YANDEX_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = 'Новая заявка с Telegram бота'

    body = (
        f"Полное имя: {data.get('full_name')}\n"
        f"Номер телефона: {data.get('phone_number')}\n"
        f"Тип услуги/продукта: {data.get('service_type')}\n"
        f"Бюджет: {data.get('budget')}\n"
        f"Сроки реализации: {data.get('deadline')}\n"
    )
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.yandex.ru', 587)
        server.starttls()
        server.login(YANDEX_EMAIL, YANDEX_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")

# Запуск бота
bot.polling(none_stop=True)