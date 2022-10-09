import spacy

NLP: spacy.Language = spacy.load("en_core_web_sm")


def generate_reports(text: str) -> list[str]: ...


def reports_from_site(url: str) -> list[str]: ...


def main() -> None:
    urls: list[str] = [
        "https://strathprints.strath.ac.uk/2611/1/strathprints002611.pdf",
    ]
    for url in urls:
        reports: list[str] = reports_from_site(url)
        print(f"Site: {url}")
        for report in reports:
            print(f"\t{report}")
        print()


if __name__ == "__main__":
    main()
