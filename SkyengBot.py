# Импорт необходимых библиотек и загрузка переменных окружения
from dotenv import load_dotenv
import telebot
import json
import random
import os


# Загрузка токена бота и данных пользователей из файла
load_dotenv()
TOKEN = os.getenv('SkyengBotToken')
bot = telebot.TeleBot(TOKEN)
dictionary = os.getenv('dictionary')
try:
    with open(dictionary, 'r', encoding='utf-8') as f:
        user_data = json.load(f)
except FileNotFoundError:
    user_data = {}
    print(f'Файл {dictionary} не найден. Создан новый файл для хранения данных пользователей.')
except Exception as e:
    user_data = {}
    print(f'Ошибка при загрузке данных пользователей: {e}, сообщите о ней разработчику.')



# Команда /start для приветствия пользователя
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, 'Привет! Это бот для изучения английских слов.')

# Команда /cancel для отмены текущего действия
@bot.message_handler(commands=['cancel'])
def handle_cancel(message):
    try:
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.send_message(message.chat.id, 'Действие отменено.')
    except Exception as e:
        print(f'Ошибка при отмене действия: {e} в функции handle_cancel')
        bot.send_message(message.chat.id, 'Произошла ошибка при отмене действия. Пожалуйста, сообщите о проблеме разработчику.')



# Команда /learn для повторения слов из словаря пользователя
@bot.message_handler(commands=['learn'])
def handle_learn(message):
    global user_data
    chat_id = message.chat.id
    user_words = user_data.get(str(chat_id), {})
    #Если у пользователя есть слова для обучения, продолжаем на следующий шаг
    if user_words and len(user_words) > 0:
        bot.send_message(chat_id, f'У вас есть {len(user_words)} слов для обучения. Сколько слов вы хотите повторить?')
        bot.register_next_step_handler_by_chat_id(chat_id, ask_word_count, user_words)
    else:
        bot.send_message(chat_id, 'У вас нет добавленных слов. Используйте команду /addword, чтобы добавить слова для обучения.')        

# Функция для запроса количества слов для обучения у пользователя
def ask_word_count(message,user_words):
    chat_id = message.chat.id
    #Получить вводные данные от пользователя
    try:
        word_count = int(message.text.strip())
    except Exception as e:
        word_count = 1
        print(f'Ошибка при получении количества слов для обучения: {e} в функции ask_word_count')
        bot.send_message(chat_id, 'Произошла ошибка при загрузке количества слов для обучения. Пожалуйста, сообщите о проблеме разработчику.')
    #Проверить, достаточно ли слов для обучения, и продолжить на следующий шаг
    if word_count <= len(user_words):
        words_list = random.sample(list(user_words.keys()), word_count)
        ask_translation(chat_id, user_words, words_list)
    else:
        bot.send_message(chat_id, f'У вас недостаточно слов для обучения. \nУ вас есть {len(user_words)} слов. \nИспользуйте команду /addword, чтобы добавить слова для обучения.')

# Функция для запроса перевода слова у пользователя
def ask_translation(chat_id, user_words, words_left):
    #Проверить все ли слова были повторены
    if words_left == []:
        bot.send_message(chat_id, 'Вы повторили все слова! Отличная работа!')
    else:
        random_word = random.choice(words_left)
        bot.send_message(chat_id, text=f'Какой перевод слова "{random_word}"?')
        bot.register_next_step_handler_by_chat_id(chat_id,check_translation,random_word,user_words,words_left)

# Функция для проверки перевода слова, введенного пользователем
def check_translation(message, asked_word,user_words,words_left):
    user_translation = message.text.strip().lower()
    correct_translation = user_words[asked_word]
    #Проверить правильность перевода и отправить соответствующее сообщение пользователю
    if correct_translation == user_translation:
        bot.send_message(message.chat.id, 'Правильно!')
    else:
        bot.send_message(message.chat.id, f'Неправильно! Правильный перевод слова - "{correct_translation}".')
    #Удалить слово из списка слов для повторения и продолжить повторение остальных слов
    words_left.remove(asked_word)
    ask_translation(message.chat.id, user_words, words_left)



# Команда /addword для добавления слова и его перевода в словарь пользователя
@bot.message_handler(commands=['addword'])
def handle_addword(message):
    global user_data
    chat_id = message.chat.id
    #Получить словарь пользователя, если он существует, иначе создать новый словарь
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
    #Получить вводные данные от пользователя
    try:
        word = message.text.strip().lower()
    except Exception as e:
        word = ''
        print(f'Ошибка при добавлении слова: {e} в функции addword')
        bot.send_message(chat_id, 'Произошла ошибка при добавлении слова. Пожалуйста, сообщите о проблеме разработчику.')
    #Проверить, есть ли уже такое слово в словаре пользователя
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
    #Получить вводные данные от пользователя
    try:
        translation = message.text.strip().lower()
    except Exception as e:
        translation = ''
        print(f'Ошибка при получении перевода слова: {e} в функции addtranslation')
        bot.send_message(chat_id, 'Произошла ошибка при загрузке вашего перевода. Пожалуйста, сообщите о проблеме разработчику.')
    user_dict[word] = translation
    user_data[str(chat_id)] = user_dict
    #Сохранить обновленные данные пользователя в файл
    try:
        with open(dictionary, 'w', encoding='utf-8') as file:
            json.dump(user_data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f'Ошибка при сохранении данных: {e} в функции addtranslation')
        bot.send_message(chat_id, 'Произошла ошибка при сохранении ваших данных. Пожалуйста, сообщите о проблеме разработчику.')
    bot.send_message(message.chat.id, f'Слово "{word}" с переводом "{translation}" добавлено!')

# Команда /delword для удаления слова из словаря пользователя
@bot.message_handler(commands=['delword'])
def handle_deleteword(message):
    global user_data
    chat_id = message.chat.id
    user_words = user_data.get(str(chat_id), {})
    words_text = "\n".join(word.capitalize() for word in user_words.keys())
    #Проверить, есть ли слова для удаления
    if user_words:
        text = f'Пожалуйста, напишите слово, которое хотите удалить из вашего словаря. У вас есть такие слова: \n{words_text}'
    else:
        text = 'У вас нет добавленных слов для удаления. Используйте команду /addword, чтобы добавить слова для обучения.'
    bot.send_message(chat_id, text)
    bot.register_next_step_handler_by_chat_id(chat_id, delete_word, user_words)

# Функция для удаления слова из словаря пользователя
def delete_word(message, user_words):
    global user_data
    chat_id = message.chat.id
    #Получить вводные данные от пользователя
    try:
        word_to_delete = message.text.strip().lower()
    except Exception as e:
        word_to_delete = ''
        print(f'Ошибка при получении слова для удаления: {e} в функции delete_word')
        bot.send_message(chat_id, 'Произошла ошибка при загрузке слова для удаления. Пожалуйста, сообщите о проблеме разработчику.')
    #Проверить, есть ли такое слово в словаре пользователя и удалить его
    if word_to_delete in user_words:
        del user_words[word_to_delete]
        user_data[str(chat_id)] = user_words
        #Сохранить обновленные данные пользователя в файл
        try:
            with open(dictionary, 'w', encoding='utf-8') as file:
                json.dump(user_data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f'Ошибка при сохранении данных: {e} в функции delete_word')
            bot.send_message(chat_id, 'Произошла ошибка при сохранении ваших данных. Пожалуйста, сообщите о проблеме разработчику.')
        bot.send_message(chat_id, f'Слово "{word_to_delete}" удалено из вашего словаря!')
    else:
        bot.send_message(chat_id, f'Слово "{word_to_delete}" не найдено в вашем словаре. Попробуйте снова.')

# Команда /words для отображения всех слов и их переводов из словаря пользователя
@bot.message_handler(commands=['words'])
def handle_words(message):
    global user_data
    chat_id = message.chat.id
    user_words = user_data.get(str(chat_id), {})
    #Проверить, есть ли слова в словаре пользователя и отобразить их
    if user_words:
        words_text = "\n".join(f'{word.capitalize()} - {translation.capitalize()}' for word, translation in user_words.items())
        bot.send_message(chat_id, f'Ваш словарь:\n{words_text}')
    else:
        bot.send_message(chat_id, 'У вас нет добавленных слов. Используйте команду /addword, чтобы добавить слова для обучения.')

# Команда /help для получения информации о боте и его возможностях
@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, 'Привет! Это бот для разных задач:\n/start - начать\n/learn - повторить\n/addword - добавить слово\n/delword - удалить слово\n/help - помощь\nИли просто напишити сообщение, и я постараюсь ответить!\n\nБот создан Be1kna для Skyeng.')

# Обработчик для всех остальных сообщений, которые не являются командами
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    #Ответы на определенные ключевые слова в сообщении пользователя
    replyText = ''
    if 'привет' in message.text.lower():
        replyText += 'Привет! '
    if 'пока' in message.text.lower():
        replyText += 'Пока! До встречи! '
    if 'как дела' in message.text.lower():
        replyText += 'У меня все отлично! Спасибо, что спросил. '
    if 'как тебя зовут' in message.text.lower():
        replyText += 'Меня зовут Skyeng Bot. А тебя? '
    if 'кто ты' in message.text.lower():
        replyText += 'Я бот, созданный Be1kna. Могу отвечать на сообщения! '
    if 'эхо' in message.text.lower():
        echo_text = message.text[message.text.lower().find('эхо') + len('эхо'):].strip()
        if echo_text == '':
            replyText += 'Пожалуйста, напишите текст после слова "эхо". '
        else:
            replyText += echo_text
    if replyText == '':
        replyText += 'Извини, я не поняла твое сообщение. '
    bot.send_message(message.chat.id, replyText)

# Запуск бота
if __name__ == '__main__':
    print('Bot running...')
    bot.polling(none_stop=True)
