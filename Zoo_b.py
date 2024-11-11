import telebot
import re
from telebot import types
from info_answer import TOKEN, totem_zoo
from extensions import InputException
from question import QuestionsAboutAnimals
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def start(message):
    text = ('   Здравствуй путник! Ты здесь, а это значит, ты хочешь узнать свое тотемное животное. В данном тесте '
            'присутствуют обитатели Московского зоопарка, опекуном которых ты можешь стать! \n\nЕсли ты готов, '
            'жми -  "Начать тест". \n\n‼️ Для дополнительной информации можно связаться с сотрудником или зайти на сайт'
            ' Московского зоопарка нажав по кнопке ниже.')
    photo = open("main.jpg", "rb")
    bot.send_message(message.chat.id, text)
    bot.send_photo(message.chat.id, photo=photo)
    button_start(message)

@bot.message_handler(commands=['button'])
def button_start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item1 = types.KeyboardButton("Начать тест")
    item2 = types.KeyboardButton("Связаться с сотрудником зоопарка")
    markup.add(item1)
    markup.add(item2)
    bot.send_message(message.chat.id, 'Ну что, вперед!!!', reply_markup=markup)

@bot.message_handler(func=lambda
        message: message.text.lower() == 'начать тест' or message.text.lower() == 'связаться с сотрудником зоопарка' or message.text.lower() == 'сыграть снова' or message.text.lower() == 'закончить игру' or message.text.lower() == 'перейти на официальный сайт московского зоопарка' or message.text.lower() == 'расскажите мне о программе опеки')
def handle_text(message):
    try:
        if message.text.lower() == 'начать тест' or message.text.lower() == 'сыграть снова':
            ask_question(message)
        elif message.text.lower() == 'связаться с сотрудником зоопарка':
            contact(message)
        elif message.text.lower() == 'перейти на официальный сайт московского зоопарка':
            MoskowZooSite(message)
        elif message.text.lower() == 'расскажите мне о программе опеки':
            guardianship_program(message)
    except InputException as e:
        bot.reply_to(message, f"‼️ Ошибка отправки сообщения: \n{e}")

def contact(message):
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="Связаться с сотрудником зоопарка", url="https://t.me/V_Vladislav_N")
    keyboard.add(url_button)
    bot.send_message(message.chat.id, " ⬇️ Связаться с сотрудником зоопарка, нажав по кнопке ниже:",
                     reply_markup=keyboard)

def output_question_and_answers(message, k):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = []
    for var in list(QuestionsAboutAnimals.items())[k][1]:
        buttons.append(types.KeyboardButton(text=var))
    keyboard.add(*buttons)

    return keyboard

def ask_question(message: types.Message, k=-1, counts=None):
    if counts is None:
        counts = {'1': 0, '2': 0, '3': 0, '4': 0}
    if k != len(QuestionsAboutAnimals) - 1:
        k += 1
        kb = output_question_and_answers(message, k)
        msg = bot.send_message(message.chat.id, text=list(QuestionsAboutAnimals.items())[k][0], reply_markup=kb)
        bot.register_next_step_handler(msg, process_answer, k, counts)
    else:
        bot.send_message(message.chat.id, text='Итак... \n\nТвое тотемное животное ',
                         reply_markup=types.ReplyKeyboardRemove())
        calculation_results(counts, message)

@bot.message_handler()
def process_answer(message: types.Message, k, counts):
    try:
        if re.search(r'^([1-4]\.\s)', message.text):
            counts[message.text[0]] += 1
            ask_question(message, k, counts)
        else:
            raise InputException("– Нажимайте на кнопки ниже, для того, чтобы дать ответ!")
    except InputException as e:
        bot.reply_to(message, f"‼️ Ошибка отправки сообщения: \n{e}")
        ask_question(message, k - 1, counts)

    print(counts)

def calculation_results(counts, message):
    max_count = max(counts.values())
    max_categories = [cat for cat, count in counts.items() if count == max_count]

    if len(max_categories) == 1:
        bot.send_message(message.chat.id, totem_zoo[str(max_categories[0])])
        bot.send_sticker(message.chat.id, list(totem_zoo.values())[int(max_categories[0]) - 1][1])
        final_choice(message)

    else:
        bot.send_message(message.chat.id, totem_zoo[tuple(sorted(max_categories))])
        bot.send_sticker(message.chat.id, totem_zoo[tuple(sorted(max_categories))][1])
        final_choice(message)

def final_choice(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    button1 = types.KeyboardButton("Связаться с сотрудником зоопарка")
    button2 = types.KeyboardButton("Перейти на официальный сайт Московского Зоопарка")
    button3 = types.KeyboardButton("Расскажите мне о программе опеки")
    button4 = types.KeyboardButton("Сыграть снова")
    button5 = types.KeyboardButton("Закончить игру")

    markup.add(button1)
    markup.add(button2)
    markup.add(button3)
    markup.add(button4)
    markup.add(button5)

    bot.send_message(message.chat.id, 'Выбери нужное', reply_markup=markup)

def MoskowZooSite(message):
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="Перейти на сайт московского зоопарка", url="https://moscowzoo.ru")
    keyboard.add(url_button)
    bot.send_message(message.chat.id, "⬇️ перейти на сайт зоопарка",
                     reply_markup=keyboard)

def guardianship_program(message):
    custody = ("\nУчастие в программе «Клуб друзей зоопарка» — это помощь в содержании наших обитателей, а также ваш "
               "личный вклад в дело сохранения биоразнообразия Земли и развитие нашего зоопарка. \n\nОсновная задача "
               "Московского зоопарка с самого начала его существования это — сохранение биоразнообразия планеты. Когда "
               "вы берете под опеку животное, вы помогаете нам в этом благородном деле. При нынешних темпах развития "
               "цивилизации к 2050 году с лица Земли могут исчезнуть около 10 000 биологических видов. Московский "
               "зоопарк вместе с другими зоопарками мира делает все возможное, чтобы сохранить их. \n\nТрадиция опекать "
               "животных в Московском зоопарке возникло с момента его создания в 1864г. Такая практика есть и в других "
               "зоопарках по всему миру. \n\nВ настоящее время опекуны объединились в неформальное сообщество — Клуб "
               "друзей Московского зоопарка. Программа «Клуб друзей» дает возможность опекунам ощутить свою причастность "
               "к делу сохранения природы, участвовать в жизни Московского зоопарка и его обитателей, видеть конкретные "
               "результаты своей деятельности.")
    bot.send_message(message.chat.id, custody)

bot.polling()
