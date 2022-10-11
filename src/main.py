from typing import TypedDict, Union, Literal, Iterable, Optional

import requests
import logging

import spacy
import bs4
import pdfx

from spacy.tokens.doc import Doc

# Config
logging.basicConfig(format="%(message)s", level=logging.ERROR)
logger: logging.Logger = logging.getLogger("scraper")
logger.setLevel(logging.INFO)

NLP: spacy.Language = spacy.load("en_core_web_sm")

HEADER: dict[str, str] = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


# Type Alias
class ArticleDict(TypedDict):
    title: str
    link: str
    doc_link: str
    doc_kind: Union[Literal["PDF"], Literal["HTML"]]


# Functions
def reports_from_text(text: str) -> list[str]:
    """ Extracts sentences from text string. """
    document: Doc = NLP(text)
    reports: list[str] = []
    for sent in document.sents:
        text: str = sent.text.strip().replace("\n", ' ').replace("\t", ' ')
        if text: reports.append(text)
    return reports


def reports_from_site(url: str, kind: Union[Literal["PDF"], Literal["HTML"]] = "HTML") -> list[str]:
    """ Extracts sentences from website (PDF or HTML).  """
    print(f"Generating reports from site: {url}...", end=' ')
    response: requests.Response = requests.get(url, headers=HEADER)
    if response.status_code != 200:
        logger.warning(f"Couldn't reach {url} for scraping. Status Code: {response.status_code}")
        print("Failed.")
        return []

    text: str = ""
    if kind == "PDF":
        text = pdfx.PDFx(url).get_text()
    elif kind == "HTML":
        soup: bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, "html.parser")
        for p in soup.select("p"):
            text += p.text
    else:
        logger.warning(f"Invalid document kind: {kind} for function reports_from_site()")
    reports: list[str] = reports_from_text(text)
    print("Done.")
    return reports


def scrape_scholar(query: str, limit: int = 5, lang: str = "en", exts: Optional[Iterable[str]] = None) -> list[ArticleDict]:
    """ Generates dict with information from Google Scholar articles. """
    print(f"Scraping '{query}' from Google Scholar...", end=' ')

    articles: list[dict[str, str]] = []
    params: dict[str, str] = dict(q=query, hl=lang, start='0')

    if exts is None:  # Any Extension
        response: requests.Response = requests.get("https://scholar.google.com.br/scholar", params=params)
        if response.status_code != 200:
            logger.warning(f"Couldn't reach https://scholar.google.com.br/scholar for scraping. Status Code: {response.status_code}")
            print("Failed.")
            return articles

        soup: bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, "html.parser")
        for article_div in soup.select(".gs_r.gs_or.gs_scl")[:limit]:
            title: str = article_div.select_one(".gs_rt a").text
            link: str = article_div.select_one(".gs_rt a")["href"]
            doc_link: str = article_div.select_one(".gs_or_ggsm a")["href"]
            doc_kind: Union[Literal["PDF"], Literal["HTML"]] = article_div.select_one(".gs_or_ggsm a").select_one(".gs_ctg2").text[1:-1]
            article: ArticleDict = dict(title=title, link=link, doc_link=doc_link, doc_kind=doc_kind)
            articles.append(article)
    else:  # Only Defined Extensions
        exts = set(exts)
        count: int = 0
        has_next: bool = True
        while count < limit and has_next:
            response: requests.Response = requests.get("https://scholar.google.com.br/scholar", params=params)
            if response.status_code != 200:
                logger.warning(f"Couldn't reach https://scholar.google.com.br/scholar for scraping. Status Code: {response.status_code}")
                print("Failed.")
                return articles

            soup: bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, "html.parser")
            for article_div in soup.select(".gs_r.gs_or.gs_scl"):
                if count >= limit: break

                doc_div: Optional[bs4.element.Tag] = article_div.select_one(".gs_or_ggsm a")
                if doc_div is None: continue
                doc_kind: Union[Literal["PDF"], Literal["HTML"]] = article_div.select_one(".gs_or_ggsm a").select_one(".gs_ctg2").text[1:-1]
                if doc_kind not in exts: continue

                title: str = article_div.select_one(".gs_rt a").text
                link: str = article_div.select_one(".gs_rt a")["href"]
                doc_link: str = article_div.select_one(".gs_or_ggsm a")["href"]
                article: ArticleDict = dict(title=title, link=link, doc_link=doc_link, doc_kind=doc_kind)
                articles.append(article)
                count += 1

            # Find next button
            if soup.select_one(".gs_ico_nav_next") is not None:
                has_next = True
                params["start"] = str(int(params['start']) + 10)
            else:
                has_next = False

    print("Done.")
    return articles


def main() -> None:
    logger.debug("Program Start")
    subject: str = "Natural Language Processing"
    articles: list[ArticleDict] = scrape_scholar(subject, 5, "en", ["PDF", "HTML"])
    # print(*articles, sep='\n')
    for article in articles:
        url: str = article["doc_link"]
        reports: list[str] = reports_from_site(url, kind=article['doc_kind'])
        print(f"{article['title']}({article['doc_link']}): {len(reports)} sentences.")
        start: int = len(reports) // 4
        for report in reports[start:start+3]:
            print(f"> '{report}'")
        print("...\n")

    logger.debug("Program End")


if __name__ == "__main__":
    main()
