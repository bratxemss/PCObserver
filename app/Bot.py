import time
import telebot
from Tokkens import data_checker, user_pc_data, pc_application_status_observer, switch_changer
from telebot import types

bot = telebot.TeleBot('5913552994:AAELCsRPH9uw3jKgdG_8wVSdIOQOCvga7qs')
generated_applications = []


@bot.message_handler(commands=["help"])
def helper(message):
    bot.send_message(message.chat.id,
                     text="Hello, {0.first_name}! I am the test bot 'P.C.Observer'. "
                          "My job is to turn on and off the applications on your computer if u want to start "
                          "or just print /start".format(message.from_user))


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Начать настройку")
    markup.add(btn1)
    bot.send_message(message.chat.id,
                     text="Hello, {0.first_name}! I am the test bot 'P.C.Observer'. "
                          "My job is to turn on and off the "
                          "applications on your computer".format(message.from_user), reply_markup=markup)


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == "👋 Начать настройку":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("🫡 Создать Токен")
        markup.add(btn1)
        bot.send_message(message.chat.id,
                         text="Для начала тебе нужно создать свой токен.".format(
                             message.from_user), reply_markup=markup)
    if message.text == "🫡 Создать Токен":
        user_id = message.from_user.id
        bot.send_message(message.chat.id,
                         text=data_checker(user_id).format(
                             message.from_user))
        if "Our system detected that you have a connected PC id ->" in data_checker(user_id):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("🔍 get all applications")
            btn2 = types.KeyboardButton("🔍 get all favorite applications ⭐️")
            markup.add(btn1, btn2)
            bot.send_message(message.chat.id,
                             text="⚠⚠Make sure that our application is running and configured on your computer. "
                                  "If all is done, press 🔍 connect_data. "
                                  "You need to add at least "
                                  "one application⚠⚠".format(message.from_user), reply_markup=markup)

    if (message.text == "🔍 get all applications") or (message.text == "🔍 get all favorite applications ⭐️"):
        try:
            user_id = message.from_user.id
            result = user_pc_data(user_id)
            markup = types.InlineKeyboardMarkup()
        except: # noqa
            return
        if pc_application_status_observer(user_id) == 2 and result:  # online
            bot.send_message(message.chat.id, text="Your application is successfully launched and "
                                                   "configured on your computer")
            try:
                for application, data in result.items():

                    if message.text == "🔍 get all applications":
                        generated_applications.append(application)
                        if data['Favorite'] == "No":
                            button = types.InlineKeyboardButton(text=application, callback_data=application)
                        else:
                            button = types.InlineKeyboardButton(text=f"{application}⭐️", callback_data=application)
                        markup.add(button)
                    elif message.text == "🔍 get all favorite applications ⭐️":
                        if data["Favorite"] == "Yes":
                            generated_applications.append(application)
                            button = types.InlineKeyboardButton(text=f"{application}⭐️", callback_data=application)
                            markup.add(button)
                    # Send the message with the inline keyboard
                bot.send_message(message.chat.id, "That is you apps", reply_markup=markup, disable_notification=True)
                bot.send_message(message.chat.id, text="🟢🟢All applications that can be sent have been sent!🟢🟢")

            except telebot.apihelper.ApiTelegramException as e:
                if e.error_code == 429:  # слишком много запросов
                    time.sleep(1)
                elif e.error_code == 400:  # слишком длинное сообщение
                    pass
                else:
                    raise e
                bot.send_message(message.chat.id, text="🔴🔴Unexpected error, "
                                                       "for some reason the bot cannot send "
                                                       "you a list of your apps🔴🔴")
        elif pc_application_status_observer(user_id) == 1:  # offline
            bot.send_message(message.chat.id,
                             text="⚠⚠Please run and configure the application⚠⚠")
        elif pc_application_status_observer(user_id) == 0 and result is False:
            bot.send_message(message.chat.id,
                             text="🔴🔴The application has never been run on your computer, "
                                  "if it is not installed, please install at this link ->🔴🔴")
        else:
            bot.send_message(message.chat.id,
                             text="🔴🔴Unexpected error, start setting process again🔴🔴")


@bot.callback_query_handler(func=lambda call: call.data in generated_applications)
def display_application_info(call):
    application = call.data
    user_id = call.from_user.id
    result = user_pc_data(user_id)
    size = result[application]['size']
    memory = result[application]['memory']
    status = result[application]['Status']
    favorite = result[application]['Favorite']
    markup = types.InlineKeyboardMarkup()
    # Create the turn off button

    if status == "running":
        turn_off_button = types.InlineKeyboardButton("🛑Turn Off", callback_data=f"turn_off_{application}")
        turn_on_button = types.InlineKeyboardButton("✅Turn On❌", callback_data=f"Disabled_button")
    else:
        turn_off_button = types.InlineKeyboardButton("🛑Turn Off❌", callback_data=f"Disabled_button")
        turn_on_button = types.InlineKeyboardButton("✅Turn On", callback_data=f"turn_on_{application}")

    @bot.callback_query_handler(func=lambda c: c.data.startswith("turn_on_"))
    def turn_on_application(c):
        app_name = c.data.replace("turn_on_", "")
        switch_changer(user_id, app_name)
        bot.send_message(c.message.chat.id, text=f"Application {app_name} is starting up!")

    @bot.callback_query_handler(func=lambda c: c.data.startswith("turn_off_"))
    def turn_off_application(c):
        app_name = c.data.replace("turn_off_", "")
        switch_changer(user_id, app_name)
        bot.send_message(c.message.chat.id, text=f"Application {app_name} is turning off!")

    @bot.callback_query_handler(func=lambda c: c.data == "Disabled_button")
    def disabled_button(c):
        bot.send_message(c.message.chat.id, text="Impossible Function")

    markup.add(turn_on_button, turn_off_button)
    bot.send_message(call.message.chat.id,
                     f"Application: {application}\nSize: {size}\nMemory: {memory}\nStatus: "
                     f"{status}\nFavorite:{favorite}", reply_markup=markup)


bot.polling(none_stop=True, interval=0)
