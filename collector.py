import requests
import json
import time
from bs4 import BeautifulSoup


def web_crawler(url):
    def extract_data(html, href):
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        # Find the title tag
        title_tag = soup.find("title")
        # Extract the title text
        title = title_tag.text if title_tag else None
        history = []  # array
        outer_rows = soup.find_all("td", {"align": "right", "colspan": "2"})
        for outer_row in outer_rows:
            nested_table = outer_row.find("table")
            if nested_table:
                inner_rows = nested_table.find_all("tr")
                for inner_row in inner_rows:
                    font_tags = inner_row.find_all("font", size="2")
                    for font in font_tags:
                        text = font.text.strip()
                        if "개정" in text or "제정" in text:
                            history.append(text)

        # Extract rules
        rules = []
        bylaws = []

        current_chapter = None
        current_section = None
        current_article = None
        current_item = None

        rows = soup.find_all("tr")
        for row in rows:
            # Check for chapter
            chapter_tag = row.find(
                "a", attrs={"name": lambda x: x and "제" in x and "장" in x}
            )
            if chapter_tag:
                chapter_name = chapter_tag.text.strip()
                existing_chapter = next(
                    (
                        chapter
                        for chapter in rules
                        if chapter["chapter"] == chapter_name
                    ),
                    None,
                )
                if not existing_chapter:
                    current_chapter = {
                        "chapter": chapter_name,
                        "sections": [],
                    }
                    rules.append(current_chapter)
                else:
                    current_chapter = existing_chapter
                current_section = None
                current_article = None
                continue

            # Check for section (절)
            section_tag = row.find("b", text=lambda x: x and "절" in x)
            if section_tag:
                current_section = {
                    "section": section_tag.text.strip(),
                    "articles": [],
                }
                if current_chapter:
                    current_chapter["sections"].append(current_section)
                else:
                    current_chapter = {
                        "chapter": None,
                        "sections": [],
                    }
                    current_chapter["sections"].append(current_section)
                current_article = None
                current_item = None
                continue

            # Check for article (조)
            article_tag = row.find("b", text=lambda x: x and "조" in x)
            if article_tag:
                current_article = {
                    "article": article_tag.text.strip(),
                    "items": [],
                }
                if current_section:
                    current_section["articles"].append(current_article)
                elif current_chapter:
                    current_chapter["sections"].append(
                        {"section": None, "articles": [current_article]}
                    )
                else:
                    rules.append(
                        {
                            "chapter": None,
                            "sections": [
                                {"section": None, "articles": [current_article]}
                            ],
                        }
                    )
                current_item = None
                continue

            # Check for item (항)
            td_tags = row.find_all("td")
            if len(td_tags) > 1 and td_tags[0].get("width") == "15":
                font_tag = td_tags[1].find("font", size="2")
                if font_tag and current_article:
                    current_item = font_tag.text.strip()
                    current_article["items"].append(current_item)

            # Append content to the current level
            if current_item:
                current_item += " " + row.text.strip()
            elif current_article:
                current_article["items"].append(row.text.strip())
            elif current_section:
                current_section["articles"].append(row.text.strip())
            elif current_chapter:
                current_chapter["sections"].append(row.text.strip())
            # else:
            #     # If no chapter, section, or article is found, add the content directly to rules
            #     rules.append(
            #         {
            #             "chapter": None,
            #             "sections": [
            #                 {
            #                     "section": None,
            #                     "articles": [
            #                         {"article": None, "items": [row.text.strip()]}
            #                     ],
            #                 }
            #             ],
            #         }
            #     )

        return {"title": title, "history": history, "rules": rules, "URL": href}

    # Send a GET request to the specified URL
    # response = requests.get(url, headers={"Cache-Control": "max-age=3600"})
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Process the response data here
        # ...

        # Extract all the links from the HTML response
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a")
        print("Found", len(links), "links")

        results = []

        # Iterate over each link and extract the title
        for link in links:
            # time.sleep(1)
            href = link.get("href")
            if href.startswith("https") == False:
                href = "https://rule.handong.edu" + href[1:]
            if href.startswith("https"):
                print(href)
                link_response = requests.get(href)
                link_response.encoding = link_response.apparent_encoding

                if link_response.status_code == 200:
                    data = extract_data(link_response.text, href)
                    results.append(data)
                else:
                    print(
                        "Error: Request failed with status code",
                        link_response.status_code,
                    )

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"./result/result_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        print(f"Results saved to {filename}")

    else:
        # Handle any errors or exceptions here
        print("Error: Request failed with status code", response.status_code)


web_crawler("https://rule.handong.edu")
