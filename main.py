import os
import re
import ffmpeg
import telebot
from config import *
from gtts import gTTS


bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "This bot can pronounce message text." + '\n' +
                     "Just send him a message with the text what you want to voice. "
                     "Bot recognizes both Russian, English languages. If message is short - you'll get a "
                     "`voice message`. Otherwise - `.mp3` file.", parse_mode='Markdown')


@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text
    user_id = message.from_user.id
    check_language = bool(re.search('[а-яА-Я]', text))  # check the letter text for russian letters
    if check_language:  # if russian letters was detected - launch russian voice acting
        text_voice(text, 'ru', user_id)
    else:
        text_voice(text, 'en', user_id)  # if not detected - english voice


def text_voice(text, language, user_id):  # function that reads text
    output = gTTS(text=text, lang=language, slow=False)
    output.save('audio.mp3')
    size = os.stat('audio.mp3').st_size
    if int(size) >= 550000:  # if the size is too big the file does not work as a voice message
        send_audio(user_id)  # so we send it as mp3 audio file
    else:
        send_voice(user_id)  # or, if size in normal range - send it as voice message


def send_voice(user_id):
    stream = ffmpeg.input("audio.mp3")
    stream = ffmpeg.output(stream, "audio.opus")  # formatting mp3 file to opus format, because Telegram can send
    ffmpeg.run(stream)  # voice message only in opus format
    audio = open('audio.opus', 'rb')
    bot.send_voice(user_id, audio, duration=True)
    audio.close()
    os.remove('audio.opus')  # delete all unnecessary files
    os.remove('audio.mp3')


def send_audio(user_id):  # simple audio file sending using TelegramBotAPI
    audio = open('audio.mp3', 'rb')
    bot.send_audio(user_id, audio)
    audio.close()
    os.remove('audio.mp3')  # delete all unnecessary files


if __name__ == '__main__':
    bot.polling(True)
