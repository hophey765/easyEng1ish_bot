import time
from idlelib.pyparse import trans

from Tools.scripts.objgraph import definitions

from bot_instance import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from words_game.game import Game
from nltk.corpus import wordnet as wn
import requests
from config import DEEPL_API_KEY

DEEPL_URL = "https://api-free.deepl.com/v2/translate"
user_games = {}

def get_user_game(user_id):
    if user_id not in user_games:
        user_games[user_id] = Game()
        return user_games[user_id]

def start_game(bot, message, user_first_name): #Choice, who first starts
    bot.send_message(message.chat.id, f"""So, {user_first_name}, the rules are quite simple:
    - Your answer can include only one word;
    - You can use only existing, non-slang, singular nouns;
    - Your word must start with the last letter of the last word of your opponent; 
     Here we go!""")
    time.sleep(3)
    bot.send_message(message.chat.id, "Do you have any word to start with or you want to give me this opportunity?", reply_markup=who_first(bot, message))



def who_first(bot, message, disable_all=False): # Function, who first starts
    buttons = InlineKeyboardMarkup()
    buttons.add(
        InlineKeyboardButton(
            "I'm starting",
            callback_data='disabled' if disable_all else "I_am"
        ),
        InlineKeyboardButton(
            "Let you start",
            callback_data='disabled' if disable_all else "You"
        )
    )
    return buttons


def translate_text(text, target_lang="UK"):
    """
    Перевод текста с помощью DeepL API.
    :param text: текст для перевода
    :param target_lang: язык перевода (например, UK для русского)
    :return: переведённый текст или None, если запрос не удался
    """
    payload = {
        "auth_key": DEEPL_API_KEY,
        "text": text,
        "target_lang": target_lang,
    }
    try:
        response = requests.post(DEEPL_URL, data = payload)
        response.raise_for_status() # Вызывает исключение при ошибке
        translated_text = response.json()["translations"][0]["text"]
        return translated_text
    except requests.exceptions.RequestException as e:
        print(f"Error with DeepL API: {e}")
        return None

# definition = "A fruit with sweet taste and crisp texture."
# translated_definition = translate_text(definition, target_lang="UK")
#
# if translated_definition:
#     print(f"Перевод {translated_definition}")
# else:
#     print("Ошибка перевода")


def game_buttons():
    print("Creating buttons with callback data: definition")
    """
    Создаёт кнопки для игры
    Definition и др.
    """
    buttons = InlineKeyboardMarkup()
    buttons.add(
        InlineKeyboardButton("Definition", callback_data="definition"),
        InlineKeyboardButton("Translation", callback_data="translation")
    )
    return buttons


@bot.callback_query_handler(func=lambda call: call.data == "translation")
def send_translation_word(call):
    user_id = call.message.chat.id

    if user_id not in user_games:
        bot.send_message(user_id, "No active game found. Start a new game with /start.")
        return

    game = user_games[user_id]

    if not game.last_bot_word:
        bot.send_message(user_id, "No word to translate")
        return

    # Translation of word
    word_translation = translate_text(game.last_bot_word, target_lang="UK")

    if word_translation:
        bot.send_message(
            user_id,
            f"Translation of word '{game.last_bot_word}': {word_translation}"
        )
    else:
        bot.send_message(user_id, "Translation failed, please try later")



@bot.callback_query_handler(func=lambda call: call.data == "definition")
def send_definition(call):
    print("function works")
    """
    Отправляет определение текущего слова
    """
    user_id = call.message.chat.id

    # Получаем экземпляр игры для пользователя
    if user_id not in user_games:
        bot.send_message(user_id, "No active game found. Start a new game with /start.")
        return

    game = user_games[user_id]

    if not game.last_bot_word: # Проверяем, есть ли текущее слово
        bot.send_message(user_id, "No word to define!")
        return

    # Получаем первое значение слова из WordNet
    synsets = wn.synsets(game.last_bot_word)
    if synsets:
        definition = synsets[0].definition()
        bot.send_message(
            user_id,
            f"Definition of '{game.last_bot_word}': {definition}",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("Translate Definition", callback_data="translate_definition")
            )
        )
        print(definition)
    else:
        bot.send_message(user_id, f"Sorry, I couldn't find a definition for word '{game.last_bot_word}' :(")


@bot.callback_query_handler(func=lambda call: call.data == "translate_definition")
def send_translation_definition(call):
    user_id = call.message.chat.id

    if user_id not in user_games:
        bot.send_message(user_id, "No active game found. Start a new game with /start.")
        return

    game = user_games[user_id]

    if not game.last_bot_word:
        bot.send_message(user_id, "No word to translate")
        return

    # Получаем определение слова
    synsets = wn.synsets(game.last_bot_word)
    if synsets:
        definition = synsets[0].definition()
        definition_translation = translate_text(definition, target_lang="UK")

        if definition_translation:
            bot.send_message(
                user_id,
                f"Translation of the definition for word '{game.last_bot_word}': {definition_translation}"
            )
        else:
            bot.send_message(user_id, "Translation of the definition failed. Try again later.")
    else:
        bot.send_message(user_id, f"Sorry, no definition found for '{game.last_bot_word}'.")


@bot.callback_query_handler(func=lambda call: True) # Start of game
def callback_handler(call):
    user_id = call.message.chat.id

    if user_id not in user_games:
        user_games[user_id] = Game()

    game = user_games[user_id]

    user_first_name = call.from_user.first_name
    if call.data == 'game_words':
        start_game(bot, call.message, user_first_name)
    elif call.data in ['I_am', 'You']:
        if call.data == 'I_am':
            bot.send_message(call.message.chat.id, "Ok, let's go!")
            game.reset_game() # Очищаем использованные слова для новой игры
        elif call.data == 'You':
            game.reset_game() # Очищаем использованные слова для новой игры
            bot_word = game.get_random_word() # Бот выбирает случайное слово
            game.add_word(bot_word) # Добавляем слово в список использованных
            game.last_bot_word = bot_word
            bot.send_message(
                call.message.chat.id,
                f"So, my word is '{bot_word}'. Your turn! Your letter is '{bot_word[-1].upper()}'",
            reply_markup=game_buttons()
            )



        # Обновляем клавиатуру, делая все кнопки неактивными
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None     #who_first(bot, call.message, disable_all=True)
        )



@bot.message_handler(func=lambda message: not message.text.startswith('/')) # Игнорируем команды
def handle_user_word(message):  # Обработка ввода текста
    user_id = message.chat.id

    if user_id not in user_games:
        bot.send_message(user_id, "Please start a new game using /start.")
        return

    game = user_games[user_id]
    user_word = message.text.strip().lower() # Приводим слово к нижнему регистру и убираем лишние пробелы

    # Проверяем валидность слова
    if not game.is_valid_word(user_word):
        if user_word in game.used_words:
            bot.send_message(message.chat.id, "We already used this word in this game, let figure out another one!")
        else:
            bot.send_message(message.chat.id, "Invalid word! Try again.")
        return

    # Проверяем, на правильную ли букву начинается слово
    if game.last_bot_word and user_word[0] != game.last_bot_word[-1]:
        bot.send_message(message.chat.id, f"Your word must start with '{game.last_bot_word[-1].upper()}'. Try again!")
        return

    # Добавляем слово пользователя в список использованных
    game.add_word(user_word)

    # Бот отвечает
    bot_word = game.get_random_word(starting_letter=user_word[-1]) # Бот ищет слово на последнюю букву
    if bot_word:
        game.add_word(bot_word)
        game.last_bot_word = bot_word # Обновляем последнее слово бота
        time.sleep(1.5)
        bot.send_message(
            message.chat.id,
            f"My word is '{bot_word}'. Your turn! Your letter is '{bot_word[-1].upper()}'",
        reply_markup=game_buttons()
        )
    else:
        bot.send_message(message.chat.id, f"I have no words left. You win!")



@bot.callback_query_handler(func=lambda call: True)
def debug_all_callback(call):
    print(f"Received callback: {call.data}") # Печатает все callback_data