import os

import requests

import spacy
from bs4 import BeautifulSoup
from spacy.tokens.doc import Doc

NLP: spacy.Language = spacy.load("en_core_web_sm")


def reports_from_text(text: str) -> list[str]:
    """ Extracts sentences from text string. """
    document: Doc = NLP(text)
    return [sent.text for sent in document.sents]


def reports_from_site(url: str) -> list[str]:
    """ Extracts sentences from website (PDF or HTML).  """
    reports: list[str] = []
    response: requests.Response = requests.get(url)
    if response.status_code != 200:
        return reports
    soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
    # TODO: Scrape html/pdf for sentences
    return reports


def scrape_scholar(query: str, limit: int = 5, lang: str = "en") -> list[dict[str, str]]:
    """ Generates dict with information from Google Scholar articles. """
    articles: list[dict[str, str]] = []
    params: dict[str, str] = dict(q=query, hl=lang)
    response: requests.Response = requests.get("https://scholar.google.com.br/scholar", params=params)
    if response.status_code != 200: return articles

    soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")

    for article_div in soup.select(".gs_r.gs_or.gs_scl")[:limit]:
        title: str = article_div.select_one(".gs_rt a").text
        link: str = article_div.select_one(".gs_rt a")["href"]
        doc_link: str = article_div.select_one(".gs_or_ggsm a")["href"]
        article: dict[str, str] = dict(title=title, link=link, doc_link=doc_link)
        articles.append(article)
    return articles


def main() -> None:
    subject: str = "Natural Language Processing"
    # articles: list[dict[str, str]] = scrape_scholar(subject, 5, "en")
    # print(*articles, sep='\n')
    with open("../resources/article.txt", 'r', encoding="UTF-8") as f:
        reports: list[str] = reports_from_text(f.read())
        for report in reports:
            print(">", report)


if __name__ == "__main__":
    main()
