import sqlalchemy  # type: ignore
from bayes import NaiveBayesClassifier, label_news
from bottle import redirect, request, route, run, template  # type: ignore
from db import News, session
from scraputils import get_news


@route("/all")
def all_news():
    s = session()
    rows = s.query(News).all()  # запрос на все записи из таблицы News.
    return template("news_template_2", rows=s.query(News).order_by(News.label).all())

@route("/news")
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template("news_template", rows=rows)


@route("/add_label/", method="GET")
def add_label():
    s = session()
    label_we_got = request.GET.get("label", "")  # извлекается значение параметра label из GET-запроса.
    id_we_got = int(request.GET.get("id", ""))  # извлекается значение параметра id из GET-запроса.
    row = s.query(News).filter(News.id == id_we_got).one()
    row.label = label_we_got  # устанавливается значение поля label найденной записи равным полученной метке.
    s.add(row)
    s.commit()
    redirect("/all")  # перенаправление пользователя на другую страницу (в данном случае на страницу /all).
    return row  # возвращается объект row, представляющий измененную запись новости.


@route("/update")
def update_news():
    s = session()
    url = "https://news.ycombinator.com/"
    lst = get_news(url)
    for dictionary in lst:  # итерация по каждому словарю в списке
        try:
            row = s.query(News).filter(News.title == dictionary["title"]).one()
        except sqlalchemy.exc.NoResultFound:
            new_ = News(
                title=dictionary["title"],
                author=dictionary["author"],
                url=dictionary["url"],
                comments=dictionary["comments"],
                points=dictionary["points"],
            )
            s.add(new_)
            s.commit()
    redirect("/news")  # перенаправление пользователя на другую страницу (в данном случае на страницу /news).


@route("/classify")
def classify_news():
    label_news()
    redirect("/news")


if __name__ == "__main__":
    run(host="localhost", port=8080)
