import os
import sys
import telebot
import requests
from dotenv import load_dotenv
from telebot import types

# Загрузка токенов из .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

if not TELEGRAM_TOKEN or not HUGGINGFACE_API_KEY:
    print("❌ Ошибка: Убедитесь, что в .env указаны TELEGRAM_TOKEN и HUGGINGFACE_API_KEY")
    sys.exit(1)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

MAX_TG_MESSAGE_LENGTH = 4096

def get_bot_reply(prompt):
    url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": f"[INST] {prompt} [/INST]",
        "parameters": {"max_new_tokens": 1024}
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        full_text = result[0]["generated_text"].replace(f"[INST] {prompt} [/INST]", "").strip()
        return full_text
    except Exception as e:
        print("Ошибка от HuggingFace:", e)
        return "Произошла ошибка при получении ответа. Попробуй позже."

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    bot.send_chat_action(message.chat.id, "typing")

    if message.text.lower() in ["/start", "привет", "здравствуй", "hello"]:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        btn1 = types.KeyboardButton("💬 Задать вопрос")
        btn2 = types.KeyboardButton("📌 О боте")
        btn3 = types.KeyboardButton("❌ Закрыть меню")
        markup.add(btn1, btn2)
        markup.add(btn3)

        welcome = "👋 Привет! Я здесь, чтобы поддержать тебя. Чем могу помочь?"
        bot.send_message(message.chat.id, welcome, reply_markup=markup)
    elif message.text.lower() in ["❌ закрыть меню"]:
        hide_markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Меню скрыто. Просто напиши мне, когда захочешь пообщаться!", reply_markup=hide_markup)
    elif message.text.lower() in ["📌 о боте"]:
        bot.send_message(message.chat.id, "🤖 Я — бесплатный бот для поддержки и общения. Напиши что-нибудь, и я постараюсь помочь!")
    else:
        reply = get_bot_reply(message.text)
        for i in range(0, len(reply), MAX_TG_MESSAGE_LENGTH):
            bot.send_message(message.chat.id, reply[i:i+MAX_TG_MESSAGE_LENGTH])

if __name__ == "__main__":
    print("🤖 Простой бесплатный бот запущен. Готов к диалогу!")
    bot.polling()
