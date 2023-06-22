import time
import telebot
from Tokkens import DataChecker,USER_PC_DATA,PC_Application_status_observer,Switch_changer
from telebot import types

bot = telebot.TeleBot('5913552994:AAELCsRPH9uw3jKgdG_8wVSdIOQOCvga7qs')
generated_applications = []

@bot.message_handler(commands=["help"])
def help(messege):
    bot.send_message(messege.chat.id,
                     text="Hello, {0.first_name}! I am the test bot 'P.C.Observer'. My job is to turn on and off the applications on your computer if u want to start or just print /start".format(
                         messege.from_user))
@bot.message_handler(commands=["start"])
def start(messege):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Начать настройку")
    markup.add(btn1)
    bot.send_message(messege.chat.id,
                     text="Hello, {0.first_name}! I am the test bot 'P.C.Observer'. My job is to turn on and off the applications on your computer".format(
                         messege.from_user), reply_markup=markup)
@bot.message_handler(content_types=['text'])
def start(messege):
    if(messege.text == "👋 Начать настройку"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("🫡 Создать Токен")
        markup.add(btn1)
        bot.send_message(messege.chat.id,
                         text="Для начала тебе нужно создать свой токен.".format(
                             messege.from_user), reply_markup=markup)
    if (messege.text == "🫡 Создать Токен"):
        user_id = messege.from_user.id
        bot.send_message(messege.chat.id,
                         text=DataChecker(user_id).format(
                             messege.from_user))
        if "Our system detected that you have a connected PC id ->" in DataChecker(user_id):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("🔍 get all applications")
            btn2 = types.KeyboardButton("🔍 get all favorite applications ⭐️")
            markup.add(btn1,btn2)
            bot.send_message(messege.chat.id,
                             text="⚠⚠Make sure that our application is running and configured on your computer. If all is done, press 🔍 connect_data. You need to add at least one application⚠⚠".format(
                                 messege.from_user), reply_markup=markup)

    if (messege.text == "🔍 get all applications") or (messege.text == "🔍 get all favorite applications ⭐️"):
        try:
            user_id = messege.from_user.id
            result = USER_PC_DATA(user_id)
            markup = types.InlineKeyboardMarkup()

        except:
            return
        if PC_Application_status_observer(user_id) == 2 and result:#online
            bot.send_message(messege.chat.id, text= "Your application is successfully launched and configured on your computer")
            try:
                for application, data in result.items():

                    if (messege.text == "🔍 get all applications"):
                        generated_applications.append(application)
                        if data['Favorite'] == "No":
                            button = types.InlineKeyboardButton(text=application, callback_data=application)
                        else:
                            button = types.InlineKeyboardButton(text=f"{application}⭐️", callback_data=application)
                        markup.add(button)
                    elif(messege.text == "🔍 get all favorite applications ⭐️"):
                        if data["Favorite"] == "Yes":
                            generated_applications.append(application)
                            button = types.InlineKeyboardButton(text=f"{application}⭐️", callback_data=application)
                            markup.add(button)
                    # Send the message with the inline keyboard
                bot.send_message(messege.chat.id, "That is you apps", reply_markup=markup, disable_notification=True)
                bot.send_message(messege.chat.id, text="🟢🟢All applications that can be sent have been sent!🟢🟢")

            except telebot.apihelper.ApiTelegramException as e:
                if e.error_code == 429:# слишком много запросов
                    time.sleep(1)
                elif e.error_code == 400:# слишком длинное сообщение
                    pass
                else:
                    raise e
                bot.send_message(messege.chat.id, text= "🔴🔴Unexpected error, for some reason the bot cannot send you a list of your apps🔴🔴")
        elif PC_Application_status_observer(user_id) == 1: # offline
            bot.send_message(messege.chat.id,
                             text="⚠⚠Please run and configure the application⚠⚠")
        elif PC_Application_status_observer(user_id) == 0 and result == False:
            bot.send_message(messege.chat.id,
                             text="🔴🔴The application has never been run on your computer, if it is not installed, please install at this link ->🔴🔴")
        else:
            bot.send_message(messege.chat.id,
                             text="🔴🔴Unexpected error, start setting process again🔴🔴")


@bot.callback_query_handler(func=lambda call: call.data in generated_applications)
def display_application_info(call):
    # Get the application name from the callback data
    application = call.data
    # Get the user id from the callback query
    user_id = call.from_user.id

    # Get the application data for the user
    result = USER_PC_DATA(user_id)

    # Get the size, memory, and status for the application
    size = result[application]['size']
    memory = result[application]['memory']
    status = result[application]['Status']
    Favorite = result[application]['Favorite']
    # Create the markup object
    markup = types.InlineKeyboardMarkup()
    # Create the turn off button

    if status == "running":
        turn_off_button = types.InlineKeyboardButton("🛑Turn Off", callback_data=f"turn_off_{application}")
        turn_on_button = types.InlineKeyboardButton("✅Turn On❌", callback_data=f"Disabled_button")
    else:
        turn_off_button = types.InlineKeyboardButton("🛑Turn Off❌", callback_data= "Disabled_button")
        turn_on_button = types.InlineKeyboardButton("✅Turn On", callback_data=f"turn_on_{application}")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("turn_on_"))
    def turn_on_application(call):
        app_name = call.data.replace("turn_on_", "")
        Switch_changer(user_id, app_name)
        bot.send_message(call.message.chat.id, text=f"Application {app_name} is starting up!")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("turn_off_"))
    def turn_off_application(call):
        app_name = call.data.replace("turn_off_", "")
        # if app_name.endswith(".exe") is False and app_name.endswith(".lnk") is False:
        #     bot.send_message(call.message.chat.id, text="Unfortunately, I can't close files like this, if you want to be able to do that, replace it with the .exe permission file")

        Switch_changer(user_id, app_name)
        bot.send_message(call.message.chat.id, text=f"Application {app_name} is turning off!")

    @bot.callback_query_handler(func=lambda call: call.data == "Disabled_button")
    def disabled_button(call):
        bot.send_message(call.message.chat.id, text="Impossible Function")

    markup.add(turn_on_button, turn_off_button)
    # Send the message with the inline keyboard
    bot.send_message(call.message.chat.id, f"Application: {application}\nSize: {size}\nMemory: {memory}\nStatus: {status}\nFavorite:{Favorite}", reply_markup=markup)


bot.polling(none_stop=True, interval=0)

