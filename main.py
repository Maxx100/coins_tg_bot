import telebot
from telebot import types

bot = telebot.TeleBot("")

"""menu = types.InlineKeyboardMarkup(row_width=3)
menu.add(
    types.InlineKeyboardButton(text='Hi!', callback_data='b1'),
    types.InlineKeyboardButton(text='Hello!', callback_data='b2')
)"""

users = {}  # name: balance; acc; id
const_send = [1, 0, [], "send"]
wait_send = {}
checking = False
# status; count; names | 0 - none; 1 - waiting count; 2 - waiting names; 3 - sending; 4 - type (send/grant)
# -630143142


def data_import():
    with open("data.txt", "r") as f:
        for i in f.readlines():
            temp = i.split()
            users[temp[0]] = [int(temp[1]), temp[2], int(temp[3])]


def data_export():
    with open("data.txt", "w") as f:
        for i in users:
            f.write("{} {} {} {}\n".format(i, str(users[i][0]), users[i][1], str(users[i][2])))


def back_button(text, chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Back")
    markup.add(item)
    bot.send_message(chat_id, text, reply_markup=markup)


def send_points(my_name, chat_id, names, value, mode):
    temp = []
    for n in names:
        if n[0] == "@":
            name = n[1:]
        else:
            name = n
        if name not in users:
            users[name] = [0, "user", 0]
        if users[my_name][0] < int(value) and mode == "send":
            bot.send_message(chat_id, "Too much. You haven't this points")
        else:
            if mode == "send":
                users[my_name][0] -= int(value)
                if users[name][2] != 0:
                    bot.send_message(users[name][2], "@{} sent to you {}Ⓟ".format(my_name, str(value)))
            else:
                if users[name][2] != 0:
                    bot.send_message(users[name][2], "@{} granted to you {}Ⓟ".format(my_name, str(value)))
            users[name][0] += int(value)
            temp.append("@" + name)
            data_export()
    if temp:
        if mode == "send":
            bot.send_message(-630143142, "@{} sent {}Ⓟ to {}".format(my_name, str(value), ", ".join(temp)))
        else:
            bot.send_message(-630143142, "@{} granted {}Ⓟ to {}".format(my_name, str(value), ", ".join(temp)))


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Hello!')
    if message.from_user.username == "None":
        bot.send_message(message.chat.id, 'You haven`t name yet. Check it in settings of TG!')
    else:
        if message.from_user.username not in users:
            print("New user:", message.chat.id, message.from_user.username)
            users[message.from_user.username] = [0, "user", message.chat.id]
            data_export()
        elif message.from_user.username in users and users[message.from_user.username][2] == 0:
            users[message.from_user.username][2] = message.chat.id
            data_export()
        main(message)


@bot.message_handler(commands=['back'])
def main(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Balance")
    markup.add(item1)
    item2 = types.KeyboardButton("Send points")
    markup.add(item2)
    item3 = types.KeyboardButton("My name")
    markup.add(item3)
    if users[message.from_user.username][1] == "admin":
        item4 = types.KeyboardButton("Admin's commands")
        markup.add(item4)
    bot.send_message(message.chat.id, 'Choose your option', reply_markup=markup)


@bot.message_handler(commands=['admin'])
def admin(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Grants")
    markup.add(item1)
    item2 = types.KeyboardButton("Show user's balance")
    markup.add(item2)
    item3 = types.KeyboardButton("Back")
    markup.add(item3)
    bot.send_message(message.chat.id, 'Choose your option, admin', reply_markup=markup)


@bot.message_handler(content_types='text')
def message_reply(message):
    global wait_send, checking
    if message.text == "Balance":
        info = "Your balance: {}Ⓟ".format(str(users[message.from_user.username][0]))
        bot.send_message(message.chat.id, info)
    elif message.text == "My name":
        info = "Your name: @{}".format(str(message.from_user.username))
        bot.send_message(message.chat.id, info)
    elif message.text == "Send points":
        back_button("Input names and count", message.chat.id)
        wait_send[message.from_user.username] = const_send + []
    elif message.text == "Admin's commands":
        admin(message)
    elif message.text == "Back":
        main(message)
        if message.from_user.username in wait_send:
            del wait_send[message.from_user.username]
    elif users[message.from_user.username][1] == "admin" and "Grant" in message.text:
        back_button("Input names and count", message.chat.id)
        wait_send[message.from_user.username] = const_send + []
        wait_send[message.from_user.username][0] = 1
        wait_send[message.from_user.username][3] = "grant"
    elif users[message.from_user.username][1] == "admin" and "Show user's balance" == message.text:
        back_button("Input name", message.chat.id)
        checking = True
    elif message.from_user.username in wait_send and wait_send[message.from_user.username][0]:
        if wait_send[message.from_user.username][0] == 1:
            try:
                wait_send[message.from_user.username][1] = int(message.text.split()[-1])
                wait_send[message.from_user.username][2] = message.text.split()[:-1]
                if wait_send[message.from_user.username][1] < 1:
                    raise TypeError
                wait_send[message.from_user.username][0] = 3
                if len(wait_send[message.from_user.username][2]) * wait_send[message.from_user.username][1] \
                        > users[message.from_user.username][0] and wait_send[message.from_user.username][3] == "send":
                    bot.send_message(message.chat.id, "Too much. You have only"
                                                      "{}Ⓟ".format(str(users[message.from_user.username][0])))
                else:
                    send_points(message.from_user.username, message.chat.id,
                                wait_send[message.from_user.username][2],
                                wait_send[message.from_user.username][1], wait_send[message.from_user.username][3])
                    bot.send_message(message.chat.id, "✅")
                main(message)
                if message.from_user.username in wait_send:
                    del wait_send[message.from_user.username]
            except TypeError:
                back_button("Incorrect count", message.chat.id)
            except ValueError:
                back_button("Incorrect count", message.chat.id)
    elif checking:
        name = message.text
        if name[0] == "@":
            name = name[1:]
        if name in users:
            bot.send_message(message.chat.id, "@{} have {}Ⓟ".format(message.text, str(users[name][0])))
            checking = False
            main(message)
        else:
            bot.send_message(message.chat.id, "Incorrect name")
    else:
        bot.send_message(message.chat.id, message.text)


data_import()
bot.infinity_polling()
