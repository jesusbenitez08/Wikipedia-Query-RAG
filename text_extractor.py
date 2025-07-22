import requests
from bs4 import BeautifulSoup

def scrape_webpage():
    url = "https://en.wikipedia.org/wiki/Willem_Dafoe"  
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        content_div = soup.find("div", class_="mw-parser-output")
        paragraphs = content_div.find_all("p")
        text = "\n\n".join(p.get_text() for p in paragraphs)

        with open("Selected_Document.txt", "w", encoding="utf-8") as f:
            f.write(text)

        print("Article text saved to 'Selected_Document.txt'.") 
        return text
    else:
        print(f"Failed to fetch the article. HTTP Status Code: {response.status_code}") 
        return ""

if __name__ == "__main__":

    scrape_webpage()

