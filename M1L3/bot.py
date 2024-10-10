import telebot # библиотека telebot
from config import token # импорт токена
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from collections import defaultdict
import time



bot = telebot.TeleBot(token) 
MESSAGE_LIMIT = 5  
TIME_LIMIT = 10
user_messages = defaultdict(list)

def anti_spam(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    current_time = time.time()

    # Добавляем время отправки сообщения
    user_messages[user_id].append(current_time)

    # Оставляем только сообщения, отправленные за последние TIME_LIMIT секунд
    user_messages[user_id] = [t for t in user_messages[user_id] if current_time - t < TIME_LIMIT]

    # Проверяем, если количество сообщений за последние TIME_LIMIT секунд превышает лимит
    if len(user_messages[user_id]) > MESSAGE_LIMIT:
        # Если лимит превышен, удаляем сообщение и блокируем пользователя на 1 минуту
        update.message.reply_text("Вы отправляете сообщения слишком быстро! Пожалуйста, подождите.")
        context.bot.restrict_chat_member(update.effective_chat.id, user_id, can_send_messages=False, until_date=int(current_time) + 60)
    else:
        # Обработка обычного сообщения (если лимит не превышен)
        update.message.reply_text("Ваше сообщение было принято.")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я бот для управления чатом.")

@bot.message_handler(content_types=['new_chat_members'])
def make_some(message):
    bot.send_message(message.chat.id, 'I accepted a new user!')
    bot.approve_chat_join_request(message.chat.id, message.from_user.id)



@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.reply_to_message: #проверка на то, что эта команда была вызвана в ответ на сообщение 
        chat_id = message.chat.id # сохранение id чата
         # сохранение id и статуса пользователя, отправившего сообщение
        user_id = message.reply_to_message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status 
         # проверка пользователя
        if user_status == 'administrator' or user_status == 'creator':
            bot.reply_to(message, "Невозможно забанить администратора.")
        else:
            bot.ban_chat_member(chat_id, user_id) # пользователь с user_id будет забанен в чате с chat_id
            bot.reply_to(message, f"Пользователь @{message.reply_to_message.from_user.username} был забанен.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите забанить.")

bot.infinity_polling(none_stop=True)
