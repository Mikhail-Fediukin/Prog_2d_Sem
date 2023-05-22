import csv
import string
from collections import defaultdict
from math import log

from db import News, session


class NaiveBayesClassifier:
    def __init__(
        self,
    ):
        self.number = 1
        self.set_of_words = set()  # хранение уникальных слов
        self.counters = defaultdict(lambda: defaultdict(int))  # словарь для подсчета слов
        self.class_counter = defaultdict(int)  # словарь для подсчета элементов класса
        self.words_count = 0  # счетчик слов

    def fit(self, X, y):  # подсчет статистики на основе входных данных X и меток y.
        """Fit Naive Bayes classifier according to X, y."""
        for x_, y_ in zip(X, y):  # итерация по соответствующим парам элементов X и y
            self.class_counter[y_] += 1  # увеличивается счетчик класса y_ в словаре class_counter
            for word in x_.split():  # итерация слов, полученных путем разделения строки х_ на
                # отдельные слова.
                self.counters[y_][word] += 1  # увеличивается счетчик слова word для класса у_ во
                # вложенном словаре counters
                self.set_of_words.add(word)  # слово word добавляется в множество set_of_words
                self.words_count += 1  # увеличивается счетчик words_count на 1.

    def predict(self, X):  # классификация для массива тестовых векторов X.
        """Perform classification on an array of test vectors X."""
        predicted = []
        for string in X:  # итерация по каждому элементу string в массиве X, который представляет тестовые векторы.
            predicted.append(self.predict_class(string))  # предсказание класса для каждого тестового вектора string
        return predicted  # полученные результаты

    def predict_class(self, string):  # вспомогательная функция
        """Auxiliary function to perform classification on an array of test vectors X."""
        class_highest_prob = None  # переменная для хранения метки класса с наибольшей вероятностью
        count_of_elements = sum(self.class_counter.values())  # общее количество элементов для вычисления вероятности
        # классов
        prime_value = float("-inf")  # переменная для хранения наилучшего значения вероятности класса
        for class_i in self.counters:  # итерация по классам
            current_value = log(self.class_counter[class_i] / count_of_elements)
            for word in string.split():
                current_word_class_counter = self.counters[class_i][word]  # количество вхождений слова word для
                # Текущего класса class_i из словаря counters.
                current_class_word_counter = sum(self.counters[class_i].values())  # вычисляем общее количество слов в
                # текущем классе class_i
                current_value += log(
                    (current_word_class_counter + self.number)
                    / (current_class_word_counter + self.number * len(self.set_of_words))
                )
            if prime_value < current_value:  # если текущее значение вероятности current_value лучше, чем текущее лучшее
                # значение вероятности best_value
                class_highest_prob = class_i
                prime_value = current_value
        if class_highest_prob is None:
            raise Exception("Classifier is not fitted")
        return class_highest_prob

    def score(self, X_test, y_test):  # метод, который вычисляет среднюю точность (accuracy) на основе предсказаний
        # модели для заданного набора тестовых данных X_test и соответствующих меток y_test.
        """Returns the mean accuracy on the given test data and labels."""
        prediction = self.predict(X_test)  # возвращает предсказанные классы для каждого тестового вектора.
        correct_predictions_count = sum(y == pred for y, pred in zip(y_test, prediction))  # общее количество правильных
        # предсказаний
        accuracy = correct_predictions_count / len(y_test)  # вычисляется точность (метрика)
        return accuracy


def clean(string_):  # очистка текстовой строки string_ от пунктуационных символов.
    """Getting rid of punctuation"""
    translator = str.maketrans("", "", string.punctuation)
    return string_.translate(translator)


def label_news():  # функция, которая добавляет метки к новостям в базе данных
    """Adding labels to news"""
    s = session()

    x_train = s.query(News.title).filter(News.label != None).all()  # выполняется запрос к базе данных
    y_train = s.query(News.label).filter(News.label != None).all()  # аналогичный запрос

    x_train = [clean(str(x)).lower() for x in x_train]  # очистка и приведение к нижнему регистру каждого элемента
    y_train = [clean(str(y)).lower() for y in y_train]  # аналогично

    model = NaiveBayesClassifier()  # создается объект модели
    model.fit(x_train, y_train)  # выполняется обучение модели на основе обучающих данных

    label_x_ = s.query(News.title).filter(News.label == None).all()  # запрос к базе данных
    label_x_ = [clean(str(xx)).lower() for xx in label_x_]  # приведение к нижнему регистру каждого элемента

    predicted_y_ = model.predict(label_x_)  # предсказание меток для новых данных label_x_
    rows = s.query(News).filter(News.label == None).all()  # запрос к базе данных

    i = 0  # для итерации по индексам предсказанных меток predicted_y_
    for row in rows:  # цикл, который проходит по каждой записи новости в переменной rows.
        row.label = predicted_y_[i]  # присваивается предсказанная метка новости в поле метки текущей новости.
        s.add(row)  # добавить измененную запись новости.
        s.commit()  # сохранить изменения в базе данных.
        i += 1  # инкрементируется переменная i, чтобы перейти к следующему индексу в списке предсказанных меток.


if __name__ == "__main__":
    with open("data/SMSSpamCollection") as f:
        data = list(csv.reader(f, delimiter="\t"))
    X, y = [], []
    for target, msg in data:
        X.append(msg)
        y.append(target)
    X = [clean(x).lower() for x in X]
    print(X[0], "|||", y[0])
    X_train, y_train, X_test, y_test = X[:3900], y[:3900], X[3900:], y[3900:]
    model = NaiveBayesClassifier()
    model.fit(X_train, y_train)
    print(model.score(X_test, y_test))
