import random

from nltk.corpus import wordnet as wn

class Game:
    def __init__(self):
        self.used_words = set()  # Храним слова, которые уже использовались
        self.last_bot_word = None # Храним последнее слово бота

    def reset_game(self):
        """Сбрасывает игру, очищая использованные слова."""
        self.used_words.clear()


    # Валидация слова на наличие в словаре
    def is_valid_word(self, word, pos='n'):
        """
        Проверяет, является ли слово валидным:
        - Существует в словаре WordNet.
        - Ещё не использовалось в игре.
        - Соответствует части речи (по умолчанию 'n' — существительное).
        """
        # if word in self.used_words:
        #     bot
        return bool(wn.synsets(word, pos=pos)) and word not in self.used_words

    def add_word(self, word):
        """
        Добавляет слово в список использованных.
        """
        self.used_words.add(word)


    def get_random_word(self, starting_letter=None, pos='n'):
        """
        Возвращает случайное слово из WordNet, начинающееся с указанной буквы.
        Если буква не указана, выбирается любое слово.
        """
        words = [
            lemma.name() for synset in wn.all_synsets(pos=pos)
            for lemma in synset.lemmas()
            if '_' not in lemma.name() # Убираем словосочетания
        ]
        if starting_letter:
            words = [word for word in words if word.startswith(starting_letter.lower())]

        bot_word = random.choice(words) if words else None
        self.last_bot_word = bot_word # Сохраняем последнее слово

        return bot_word
