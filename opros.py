# opros.py

class Survey:
    def __init__(self, title):
        self.title = title
        self.questions = []

    def add_question(self, text, options):
        self.questions.append(Question(text, options))

class Question:
    def __init__(self, text, options):
        self.text = text
        self.options = options

# Примеры опросов
surveys = {
    "food_survey": Survey("Предпочтения в еде"),
    "music_survey": Survey("Предпочтения в музыке"),
}

surveys["food_survey"].add_question("Какое ваше любимое блюдо?", ["Пицца", "Бургер", "Салат"])
surveys["food_survey"].add_question("Какая кухня вам больше всего нравится?", ["Итальянская", "Японская", "Мексиканская"])
surveys["food_survey"].add_question("Какие продукты вы предпочитаете?", ["Мясо", "Рыба", "Овощи"])

surveys["music_survey"].add_question("Какой ваш любимый музыкальный жанр?", ["Рок", "Поп", "Джаз"])
surveys["music_survey"].add_question("Какой инструмент вам больше всего нравится?", ["Гитара", "Пианино", "Скрипка"])
surveys["music_survey"].add_question("Какие песни вы слушаете чаще всего?", ["Классические хиты", "Современные хиты", "Альтернатива"])
