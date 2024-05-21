import requests
import requests
from bs4 import BeautifulSoup

def web_crawler(url):
    def extract_data(html):
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        # Find the title tag
        title_tag = soup.find('title')
        # Extract the title text
        title = title_tag.text if title_tag else None
        history =
        return {
            "title": title
        }

    # Send a GET request to the specified URL
    response = requests.get(url, headers={'Cache-Control': 'max-age=3600'})

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Process the response data here
        # ...

        # Extract all the links from the HTML response
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')
        print("Found", len(links), "links")

        # Iterate over each link and extract the title
        for link in links:
            href = link.get('href')
            if(href.startswith('https') == False):
                href = "https://choipd.github.io/hgu-rules-static/" + href
            if href.startswith('https'):
                link_response = requests.get(href)
                if link_response.status_code == 200:
                    data = extract_data(link_response.text)
                    print(data)
                else:
                    print("Error: Request failed with status code", link_response.status_code)

    else:
        # Handle any errors or exceptions here
        print("Error: Request failed with status code", response.status_code)

web_crawler("https://choipd.github.io/hgu-rules-static")
