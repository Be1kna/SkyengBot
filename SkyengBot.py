from email.mime import message
from dotenv import load_dotenv

import telebot
import json
import random
import os

dictionary = '/Users/yuliana_school/Projects/Be1kna Skyeng/user_data.json'
try:
    with open(dictionary, 'r', encoding='utf-8') as f:
        user_data = json.load(f)
except FileNotFoundError:
    user_data = {}
    print(f'Файл {dictionary} не найден. Создан новый файл для хранения данных пользователей.')
except Exception as e:
    user_data = {}
    print(f'Ошибка при загрузке данных пользователей: {e}, сообщите о ней разработчику.')

load_dotenv()
TOKEN = os.getenv('SkyengBotToken')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, 'Привет! Это бот для разных задач.')

@bot.message_handler(commands=['learn'])
def handle_learn(message):
    global user_data
    chat_id = message.chat.id
    user_words = user_data.get(str(chat_id), {})
    if len(message.text.split()) < 2:
        word_count = 1
    else:
        word_count = int(message.text.split()[1])
    if user_words and len(user_words) > 0:
        if word_count <= len(user_words):
            words_list = random.sample(list(user_words.keys()), word_count)
            ask_translation(chat_id, user_words, words_list)
        else:
            bot.send_message(chat_id, f'У вас недостаточно слов для обучения. \nУ вас есть {len(user_words)} слов. \nИспользуйте команду /addword <слово> <перевод>, чтобы добавить слова для обучения.')
    else:
        bot.send_message(chat_id, 'У вас нет добавленных слов. Используйте команду /addword <слово> <перевод>, чтобы добавить слова для обучения.')

def ask_translation(chat_id, user_words, words_left):
    if words_left == []:
        bot.send_message(chat_id, 'Вы повторили все слова! Отличная работа!')
    else:
        random_word = random.choice(words_left)
        bot.send_message(chat_id, text=f'Какой перевод слова "{random_word}"?')
        bot.register_next_step_handler_by_chat_id(chat_id,check_translation,random_word,user_words,words_left)
    

def check_translation(message, asked_word,user_words,words_left):
    user_translation = message.text.strip().lower()
    correct_translation = user_words[asked_word]
    if correct_translation == user_translation:
        bot.send_message(message.chat.id, 'Правильно!')
    else:
        bot.send_message(message.chat.id, f'Неправильно! Правильный перевод слова - "{correct_translation}".')
    words_left.remove(asked_word)
    ask_translation(message.chat.id, user_words, words_left)



# Команда /addword для добавления слова и его перевода в словарь пользователя
@bot.message_handler(commands=['addword'])
def handle_addword(message):
    global user_data
    chat_id = message.chat.id
    try:
        user_dict = user_data.get(str(chat_id), {})
    except Exception as e:
        user_dict = {}
        print(f'Ошибка при получении данных пользователя: {e} в функции handle_addword')
        bot.send_message(chat_id, 'Произошла ошибка при загрузке ваших данных. Пожалуйста, сообщите о проблеме разработчику.')
    bot.send_message(chat_id, 'Пожалуйста, напишите слово которое хотите добавить')
    bot.register_next_step_handler_by_chat_id(chat_id, addword, user_dict)
# Функция для добавления слова и его перевода в словарь пользователя
def addword(message, user_dict):
    global user_data
    chat_id = message.chat.id
    try:
        word = message.text.strip().lower()
    except Exception as e:
        word = ''
        print(f'Ошибка при добавлении слова: {e} в функции addword')
        bot.send_message(chat_id, 'Произошла ошибка при добавлении слова. Пожалуйста, сообщите о проблеме разработчику.')
    if word in user_dict:
        bot.send_message(chat_id, f'Слово "{word}" уже есть в вашем словаре. Пожалуйста, напишите другое слово.')
        bot.register_next_step_handler_by_chat_id(chat_id, addword, user_dict)
    else:
        bot.send_message(chat_id, f'Пожалуйста, напишите перевод слова "{word}"')
        bot.register_next_step_handler_by_chat_id(chat_id, addtranslation, user_dict, word)
# Функция для добавления перевода слова в словарь пользователя
def addtranslation(message, user_dict, word):
    global user_data
    chat_id = message.chat.id
    try:
        translation = message.text.strip().lower()
    except Exception as e:
        translation = ''
        print(f'Ошибка при получении перевода слова: {e} в функции addtranslation')
        bot.send_message(chat_id, 'Произошла ошибка при загрузке вашего перевода. Пожалуйста, сообщите о проблеме разработчику.')
    user_dict[word] = translation
    user_data[str(chat_id)] = user_dict
    try:
        with open(dictionary, 'w', encoding='utf-8') as file:
            json.dump(user_data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f'Ошибка при сохранении данных: {e} в функции addtranslation')
        bot.send_message(chat_id, 'Произошла ошибка при сохранении ваших данных. Пожалуйста, сообщите о проблеме разработчику.')
    bot.send_message(message.chat.id, f'Слово "{word}" с переводом "{translation}" добавлено!')

# Команда /deleteword для удаления слова из словаря пользователя
@bot.message_handler(commands=['deleteword'])
def handle_deleteword(message):
    global user_data
    chat_id = message.chat.id
    user_words = user_data.get(str(chat_id), {})
    words_text = "\n".join(word.capitalize() for word in user_words.keys())
    if user_words:
        text = f'Пожалуйста, напишите слово, которое хотите удалить из вашего словаря. У вас есть такие слова: \n{words_text}'
    else:
        text = 'У вас нет добавленных слов для удаления. Используйте команду /addword <слово> <перевод>, чтобы добавить слова для обучения.'
    bot.send_message(chat_id, text)
    bot.register_next_step_handler_by_chat_id(chat_id, delete_word, user_words)

def delete_word(message, user_words):
    global user_data
    chat_id = message.chat.id
    try:
        word_to_delete = message.text.strip().lower()
    except Exception as e:
        word_to_delete = ''
        print(f'Ошибка при получении слова для удаления: {e} в функции delete_word')
        bot.send_message(chat_id, 'Произошла ошибка при загрузке слова для удаления. Пожалуйста, сообщите о проблеме разработчику.')
    if word_to_delete in user_words:
        del user_words[word_to_delete]
        user_data[str(chat_id)] = user_words
        try:
            with open(dictionary, 'w', encoding='utf-8') as file:
                json.dump(user_data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f'Ошибка при сохранении данных: {e} в функции delete_word')
            bot.send_message(chat_id, 'Произошла ошибка при сохранении ваших данных. Пожалуйста, сообщите о проблеме разработчику.')
        bot.send_message(chat_id, f'Слово "{word_to_delete}" удалено из вашего словаря!')
    else:
        bot.send_message(chat_id, f'Слово "{word_to_delete}" не найдено в вашем словаре. Попробуйте снова.')



# Команда /help для получения информации о боте и его возможностях
@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, 'Привет! Это бот для разных задач:\n/start - начать\n/learn - обучение\n/help - помощь\nИли просто напишити сообщение, и я постараюсь ответить!\n\nБот создан Be1kna для Skyeng.')

# Обработчик для всех остальных сообщений, которые не являются командами
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text.lower() == 'привет' or message.text.lower() == 'привет!':
        bot.send_message(message.chat.id, 'Привет! Как дела?')
    elif message.text.lower() == 'пока' or message.text.lower() == 'пока!':
        bot.send_message(message.chat.id, 'Пока! До встречи!')
    elif message.text.lower() == 'как дела?':
        bot.send_message(message.chat.id, 'У меня все отлично! Спасибо, что спросил.')
    elif message.text.lower() == 'как тебя зовут?':
        bot.send_message(message.chat.id, 'Меня зовут Skyeng Bot. А тебя?')
    elif message.text.lower() == 'кто ты?':
        bot.send_message(message.chat.id, 'Я бот, созданный Be1kna. Могу отвечать на сообщения!')
    elif 'эхо' in message.text.lower():
        echo_text = message.text[message.text.lower().find('эхо') + len('эхо'):].strip()
        if echo_text == '':
            bot.send_message(message.chat.id, 'Пожалуйста, напишите текст после слова "эхо"')
        else:
            bot.send_message(message.chat.id, echo_text)
    else:
        bot.send_message(message.chat.id, 'Извини, я не поняла твое сообщение.')

# Запуск бота
if __name__ == '__main__':
    print('Bot running...')
    bot.polling(none_stop=True)
