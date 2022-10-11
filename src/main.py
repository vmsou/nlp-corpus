from typing import TypedDict

import requests
import logging

import spacy
import bs4
from spacy.tokens.doc import Doc

# Config
logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)
NLP: spacy.Language = spacy.load("en_core_web_sm")

HEADER: dict[str, str] = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


# Type Alias
class ArticleDict(TypedDict):
    title: str
    link: str
    doc_link: str


# Functions
def reports_from_text(text: str) -> list[str]:
    """ Extracts sentences from text string. """
    # logging.info(f"Generating reports from text: {text[:20]}...")
    document: Doc = NLP(text)
    reports: list[str] = [sent.text for sent in document.sents]
    # logging.info(f"Done. Reports generated from text: {text[:20]}...")
    return reports


def reports_from_site(url: str) -> list[str]:
    """ Extracts sentences from website (PDF or HTML).  """
    logging.info(f"Generating reports from site: {url}...")
    response: requests.Response = requests.get(url, headers=HEADER)
    if response.status_code != 200: return []
    text: str = ""
    if url.endswith(".pdf"):
        # TODO: Extract Text from PDF
        ...
    else:  # Website
        soup: bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, "html.parser")
        for p in soup.select("p"):
            text += p.text
    # TODO: Scrape html/pdf for sentences
    reports: list[str] = reports_from_text(text)
    logging.info(f"Done. Reports generated from site: {url}.")
    return reports


def scrape_scholar(query: str, limit: int = 5, lang: str = "en") -> list[ArticleDict]:
    """ Generates dict with information from Google Scholar articles. """
    logging.info(f"Scraping {query} from Google Scholar...")

    articles: list[dict[str, str]] = []
    params: dict[str, str] = dict(q=query, hl=lang)
    response: requests.Response = requests.get("https://scholar.google.com.br/scholar", params=params)
    if response.status_code != 200: return articles

    soup: bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, "html.parser")

    for article_div in soup.select(".gs_r.gs_or.gs_scl")[:limit]:
        title: str = article_div.select_one(".gs_rt a").text
        link: str = article_div.select_one(".gs_rt a")["href"]
        doc_link: str = article_div.select_one(".gs_or_ggsm a")["href"]
        article: ArticleDict = dict(title=title, link=link, doc_link=doc_link)
        articles.append(article)
    logging.info(f"Done. Articles scraped from query: {query}.")
    return articles


def main() -> None:
    logging.debug("Program Start")
    subject: str = "Natural Language Processing"
    articles: list[ArticleDict] = scrape_scholar(subject, 5, "en")
    for article in articles:
        url: str = article["doc_link"]
        reports: list[str] = reports_from_site(url)
        print(f"{article['title']}: {len(reports)} sentences.")
    logging.debug("Program End")


if __name__ == "__main__":
    main()
