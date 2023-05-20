import csv
import string
from collections import defaultdict
from math import log

from db import News, session


class NaiveBayesClassifier:
    def __init__(self):
        self.number = 1
        self.set_of_words = set()
        self.counters = defaultdict(lambda: defaultdict(int))
        self.class_counter = defaultdict(int)
        self.words_count = 0

        
    def fit(self, X, y):
        for x_, y_ in zip(X, y):
            self.class_counter[y_] += 1
            for word in x_.split():
                self.counters[y_][word] += 1
                self.set_of_words.add(word)
                self.words_count += 1

                
    def predict(self, X):
        predicted = []
        for string in X:
            predicted.append(self.predict_class(string))
        return predicted

    
    def predict_class(self, string):
        class_highest_prob = None
        count_of_elements = sum(self.class_counter.values())
        prime_value = float("-inf")
        for class_i in self.counters:
            current_value = log(self.class_counter[class_i] / count_of_elements)
            for word in string.split():
                current_word_class_counter = self.counters[class_i][word]
                current_class_word_counter = sum(self.counters[class_i].values())
                current_value += log(
                    (current_word_class_counter + self.number)
                    / (current_class_word_counter + self.number * len(self.set_of_words))
                )
            if prime_value < current_value:
                class_highest_prob = class_i
                prime_value = current_value
        if class_highest_prob is None:
            raise Exception("Classifier is not fitted")
        return class_highest_prob

    
    def score(self, X_test, y_test):
        prediction = self.predict(X_test)
        correct_predictions_count = sum(y == pred for y, pred in zip(y_test, prediction))
        accuracy = correct_predictions_count / len(y_test)
        return accuracy


def clean(string_):
    translator = str.maketrans("", "", string.punctuation)
    return string_.translate(translator)


def label_news():
    s = session()

    x_train = s.query(News.title).filter(News.label != None).all()
    y_train = s.query(News.label).filter(News.label != None).all()

    x_train = [clean(str(x)).lower() for x in x_train]
    y_train = [clean(str(y)).lower() for y in y_train]

    model = NaiveBayesClassifier()
    model.fit(x_train, y_train)

    label_x_ = s.query(News.title).filter(News.label == None).all()
    label_x_ = [clean(str(xx)).lower() for xx in label_x_]

    predicted_y_ = model.predict(label_x_)
    rows = s.query(News).filter(News.label == None).all()

    i = 0
    for row in rows:
        row.label = predicted_y_[i]
        s.add(row)
        s.commit()
        i += 1


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
