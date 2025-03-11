import telebot

bot = telebot.TeleBot('8086994241:AAG8NYaP-2dxDJMyKFnqutIMCs-nUIxaLys')


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет!\n(здесь будет инфа о боте)")


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "(здесь будет руководство по боту)")


bot.polling(none_stop=True)