import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import threading
import queue
import time
import pendulum
app = Flask(__name__)
message_queue = queue.Queue()
BOT_TOKEN = '7961369773:AAGY0RkHAmsRVdGAN0GtAHOqXJNijmjHRUs'

telegram_bot = None


def run_telegram_bot():
    global telegram_bot
    telegram_bot = telebot.TeleBot(BOT_TOKEN)
    
    @telegram_bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        chat_id = str(message.chat.id)
        aa = open("id_tg.txt", "r", encoding="utf-8")
        existing_ids = aa.readlines()
        aa.close()        
        keyboard = ReplyKeyboardMarkup()
        btn = KeyboardButton("Посмотреть статистику заходов")
        keyboard.add(btn)
        chat_id_with_newline = chat_id + "\n"
        if chat_id_with_newline not in existing_ids:
            aa = open("id_tg.txt", "a", encoding="utf-8")
            aa.write(chat_id + "\n")
            aa.close()
            print(f"Новый chat_id сохранен: {chat_id}")
            telegram_bot.reply_to(message, "Бот запущен и готов получать сообщения с сайта!",reply_markup=keyboard)
        else:
            telegram_bot.reply_to(message, "Вы уже зарегистрированы! Бот готов получать сообщения с сайта!",reply_markup=keyboard)
    
    def process_queue():
        while True:
            try:
                @telegram_bot.message_handler(func=filterr)
                def start_converstion_nuer(message):
                    aa=open("analiz.txt","r")
                    statik=aa.readlines()
                    print(statik)
                    aa.close()
                    statik_return=""
                    for z in statik:
                        statik_return+=z
                    telegram_bot.send_message(message.chat.id,statik_return)
                message_text = message_queue.get(timeout=1)
                if message_text:
                    aa = open("id_tg.txt", "r", encoding="utf-8")
                    chat_ids = aa.readlines()
                    aa.close()
                    print(f"Отправка {len(chat_ids)} пользователям: {message_text}")
                    
                    for chat_id in chat_ids:
                        try:
                            telegram_bot.send_message(int(chat_id), message_text)
                        except Exception as e:
                            print(f"Ошибка отправки в {chat_id}: {e}")
                
                message_queue.task_done()
            except queue.Empty:
                continue
    
    threading.Thread(target=process_queue, daemon=True).start()
    
    print("Telegram бот запускается...")
    telegram_bot.infinity_polling()
def filterr(message):
    if message.text=="Посмотреть статистику заходов":
        return True
@app.route('/')
def index():
    analitik()
    return render_template("3d_print.html")

@app.route('/tg_attach', methods=["POST"])
def send_message():
    namee = request.form.get("name")
    email = request.form.get("email")
    mesg = request.form.get("mesg")
    message_text = f"Заявка с сайта 3д печати:\nИмя: {namee}\nПочта: {email}\nСообщение: {mesg}"
    message_queue.put(message_text)
    print(f"Сообщение в очереди: {message_text}")
    
    return redirect(url_for('index'))

@app.route('/health')
def health_check():
    try:
        aa = open("id_tg.txt", "r", encoding="utf-8")
        chat_ids_raw = aa.readlines()
        aa.close()
        chat_ids = [chat_id.strip() for chat_id in chat_ids_raw if chat_id.strip()]
        return jsonify({
            'status': 'running',
            'queue_size': message_queue.qsize(),
            'active_chats': len(chat_ids)
        })
    except FileNotFoundError:
        return jsonify({
            'status': 'running',
            'queue_size': message_queue.qsize(),
            'active_chats': 0,
            'file_status': 'not_found'
        })
    
def analitik():
    an=open("analiz.txt", "r", encoding="utf-8")
    histori = an.readlines()
    an.close()
    data_histori=[]
    nz_histori=[]
    for n in histori:
        zxz=n.split()
        data_histori.append(zxz[0])
        nz_histori.append(zxz[1])
    now = pendulum.now('Europe/Moscow')
    data=now.format('YYYY-MM-DD') 
    if data not in data_histori:
        an=open("analiz.txt", "a", encoding="utf-8")
        an.write(data+" "+ "1" + " \n")
        an.close()
    else:
        add=histori[-1].split()
        print(add)
        y=add[1]
        y=int(y)
        y+=1
        y=str(y)
        histori[-1]=add[0]+" "+y+" "+"\n"
        an=open("analiz.txt", "w", encoding="utf-8")
        an.close()
        an=open("analiz.txt", "a", encoding="utf-8")
        for line in histori:
            an.write(line)
if __name__ == '__main__':
    print("Запуск приложения...")
    
    # Создаем файл, если он не существует
    if not os.path.exists("id_tg.txt"):
        open("id_tg.txt", "w", encoding="utf-8").close()
        print("Создан файл id_tg.txt")
    if not os.path.exists("analiz.txt"):
        open("analiz.txt", "w", encoding="utf-8").close()
        print("Создан файл analiz.txt")
    threading.Thread(target=run_telegram_bot, daemon=True).start()
    time.sleep(2)
    
    app.run(host='0.0.0.0', port=5454, debug=False, use_reloader=False)