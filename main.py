import re
import bs4
import requests
from fake_headers import Headers

def get_articles_info(browser: str, os: str) -> list:
    """ Собирает информацию о статьях со страницы https://habr.com/ru/articles/ .

        Входные параметры:
        browser, os - названия браузера и операционной системы для создания поддельного заголовка

        Возвращаемое значение:
        Список словарей, содержащих информацию о статьях. Каждый словарь имеет следующие элементы:
            title - название статьи
            author - никнэйм автора
            href - абсолютная ссылка на статью
            time - время публикации
            keywords - список ключевых слов
            abstract - аннотация статьи
    """

    response = requests.get(
        'https://habr.com/ru/articles/',
        headers=Headers(browser=browser, os=os).generate()
    )

    soup = bs4.BeautifulSoup(response.text, features='lxml')
    articles = soup.select('div.tm-article-snippet')

    articles_info = []
    for article in articles:
        title = article.select_one('h2 > a > span').text
        author = article.select_one('div.tm-article-snippet__meta-container > div.tm-article-snippet__meta > span > a')["title"]
        href = 'https://habr.com' + article.select_one('div.tm-article-snippet__meta-container > div.tm-article-snippet__meta > span > span > a.tm-article-datetime-published')["href"]
        time = article.select_one('div.tm-article-snippet__meta-container > div.tm-article-snippet__meta > span > span > a.tm-article-datetime-published > time')["title"]
        all_keywords = [tag.text for tag in article.select('div.tm-publication-hubs__container > div > span > a > span')]
        keywords = list(filter(lambda word: word != '*', all_keywords))
        abstract = article.select_one('div.tm-article-body > div > div > div.article-formatted-body').text

        articles_info.append({
            "title": title, "author": author, "href": href,
            "time": time, "keywords": keywords,
            "abstract": abstract
        })

    return articles_info


def get_matched_articles(search_words: list, articles_info: list) -> list:
    """ Сопоставляет информацию о статьях со списком поисковых слов.

        Входные параметры:
        search_words - список слов для поиска
        articles_info - список словарей, содержащих информацию о статье.
        Каждый словарь должен содержать следующие элементы:
            title - название статьи
            author - никнэйм автора
            href - абсолютная ссылка на статью
            time - время публикации
            keywords - список ключевых слов
            abstract - аннотация статьи

        Возвращаемое значение:
        Список словарей, содержащих информацию о подходящих статьях. Каждый словарь имеет следующие элементы:
            title - название статьи
            href - абсолютная ссылка на статью
            time - время публикации
    """

    matched_articles = []
    for article in articles_info:
        title_words = {word.lower() for word in re.findall(r"[\w-]+", article["title"])}
        keywords_words = {word.lower() for word in re.findall(r"[\w-]+", ' '.join(article["keywords"]))}
        abstract_words = {word.lower() for word in re.findall(r"[\w-]+", article["abstract"])}
        article_set = {*title_words, article["author"], *keywords_words, *abstract_words}
        if set.intersection(article_set, set(search_words)):
            matched_articles.append({"title": article["title"], "time": article["time"], "href": article["href"]})

    return matched_articles


if __name__ == "__main__":
    search_words = [] # слова для поиска
    articles_info = get_articles_info('chrome', 'lin')
    matched_articles = get_matched_articles(search_words, articles_info)

    for article in matched_articles:
        print(f'{article["time"]} - {article["title"]} - {article["href"]}')