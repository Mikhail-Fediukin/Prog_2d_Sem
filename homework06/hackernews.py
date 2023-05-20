import sqlalchemy
from bayes import NaiveBayesClassifier, label_news
from bottle import redirect, request, route, run, template
from db import News, session
from scraputils import get_news


@route("/all")
def all_news():
    s = session()
    rows = s.query(News).all()
    return template("news_template_2", rows=s.query(News).order_by(News.label).all())


@route("/news")
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template("news_template", rows=rows)


@route("/add_label/", method="GET")
def add_label():
    s = session()
    label_we_got = request.GET.get("label", "")
    id_we_got = int(request.GET.get("id", ""))
    row = s.query(News).filter(News.id == id_we_got).one()
    row.label = label_we_got
    s.add(row)
    s.commit()
    redirect("/all")
    return row


@route("/update")
def update_news():
    s = session()
    url = "https://news.ycombinator.com/"
    lst = get_news(url)
    for dictionary in lst:
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
    redirect("/news")


@route("/classify")
def classify_news():
    label_news()
    redirect("/news")


if __name__ == "__main__":
    run(host="localhost", port=8080)
