import requests
from bs4 import BeautifulSoup


def extract_news(parser):
    list_of_news = []
    table_for_news = parser.table.findAll("table")[1]
    news = table_for_news.findAll("tr")
    inf_needed = {"title": "None", "url": "None", "author": "None", "points": 0}
    for i in range(len(news) - 1):
        news_ = news[i]
        if i % 3 == 0:
            inf_needed = {
                "title": "None",
                "url": "None",
                "author": "None",
                "points": 0,
                "comments": 0,
            }
        if news_.attrs:
            if news_.attrs["class"][0] == "athing":
                inf_needed["title"] = news_.find("span", class_="titleline").find("a").string
                link = news_.find("span", class_="titleline").find("a").get("href")
                if "http" in link:
                    inf_needed["url"] = link
                elif "item" in link:
                    inf_needed["url"] = "https://news.ycombinator.com/" + link
        else:
            if news_.find("span", class_="subline"):
                inf_needed["points"] = int(
                    news_.find("span", class_="subline").find("span", class_="score").string.split()[0]
                )
                inf_needed["author"] = news_.find("span", class_="subline").find("a", class_="hnuser").string
                number_of_comments = str(news_.find("span", class_="subline").findAll("a")[-1].string.split()[0])
                if number_of_comments.isdigit():
                    inf_needed["comments"] = int(number_of_comments)
                else:
                    inf_needed["comments"] = 0
            list_of_news.append(inf_needed)
    return list_of_news


def extract_next_page(parser):
    return parser.table.findAll("table")[1].findAll("tr")[-1].contents[2].find("a").get("href")

def get_news(url, number_of_pages=1):
    news = []
    while number_of_pages:
        print("Collecting data from page: {}".format(url))
        response = requests.get(url)
        beautiful_soup = BeautifulSoup(response.text, "html.parser")
        list_of_news = extract_news(beautiful_soup)
        next_page = extract_next_page(beautiful_soup)
        url = "https://news.ycombinator.com/" + next_page
        news.extend(list_of_news)
        number_of_pages -= 1
    return news


if __name__ == "__main__":
    url = "https://news.ycombinator.com/"
    response = requests.get(url)
    beautiful_soup = BeautifulSoup(response.text, "html.parser")
    list_of_news = get_news(url, number_of_pages=1)
    for l in list_of_news:
        print(l)
    with open("my.html", "w") as file:
        file.write(beautiful_soup.prettify())
