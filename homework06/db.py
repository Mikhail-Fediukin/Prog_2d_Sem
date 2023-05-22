from scraputils import get_news
from sqlalchemy import Column, Integer, String, create_engine  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore


def create_db(lst):
    s = session()
    inf_needed = {
        "title": "None",
        "url": "None",
        "author": "None",
        "points": 0,
        "comments": 0,
    }
    for dictionary in lst:
        if dictionary != inf_needed:
            # inf_needed
            news_ = News(
                title=dictionary["title"],
                author=dictionary["author"],
                url=dictionary["url"],
                comments=dictionary["comments"],
                points=dictionary["points"],
            )
            s.add(news_)
            s.commit()


Base = declarative_base()
engine = create_engine("sqlite:///news.db")
session = sessionmaker(bind=engine)


class News(Base):  # type: ignore
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    url = Column(String)
    comments = Column(Integer)
    points = Column(Integer)
    label = Column(String)


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    url = "https://news.ycombinator.com/"
    news_list = get_news(url, number_of_pages=1)
    create_db(news_list)
