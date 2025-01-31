# Cобственно тут будет организован весь основной функционал и объеденены все модули
# from math import gamma

from nltk.corpus.europarl_raw import english

from bot_instance import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import words_game.logic
from words_game.game import Game
from words_game.logic import user_games, get_user_game
#импортируем модули

user_levels = {} #Store user language preferences

def main_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Playing Words', callback_data='game_words'))
    return markup

#user_first_name = None

@bot.message_handler(commands=['start']) #Кнопки выбора левела
def send_greeting(message):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("Починаючий", callback_data="level_beginner"))
    markup.row(InlineKeyboardButton("I speak English quite good", callback_data="level_intermediate"))
    bot.send_message(
        message.chat.id,
        "Привіт! Обери свій рівень",
        reply_markup=markup
    )


def start_game_in_eng(user_id):
    # Используем общую функцию для получения игры пользователя
    game = get_user_game(user_id)
    game.reset_game()

    bot.send_message(
        user_id,
        f"So, what are we gonna do? Let's choose right now!",
        reply_markup=main_menu()
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("level_"))
def handle_level_selection(call):
    user_id = call.message.chat.id
    if call.data == "level_beginner":
        user_levels[user_id] = "ukrainian"
        bot.send_message(user_id, "Вітаємо, всі підказки будуть українською мовою.")
        #Redirect to Ukainian flow
    elif call.data == "level_intermediate":
        user_levels[user_id] = "english"
        bot.send_message(user_id, "Welcome! All further hints will be in English.")
        #Redirect to English flow
        start_game_in_eng(user_id)


@bot.message_handler(commands=["english"])
def send_welcome(message):
    user_id = message.chat.id
    start_game_in_eng(user_id)

# @bot.callback_query_handler(func=lambda call: call.data == "level_intermediate")
# def handle_english_callback(call):
#     user_id = call.message.chat.id
#     start_game_in_eng(user_id)



print("Bot is running...")
bot.polling()