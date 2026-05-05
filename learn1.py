import requests # This is the "Hand" that grabs the webpage
from bs4 import BeautifulSoup # This is the "Eyes" that read the webpage

# 1. The Target (Change this to a real product URL later)
URL = "https://www.amazon.com/dp/B08L5TNJHG" 

# 2. Tell the website you are a human, not a bot
headers = {"User-Agent": "Mozilla/5.0"}

def check_price():
    # Grab the page
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    # This is the hard part - finding the price "ID" on the page
    # For now, we will just print the title to see if it works
    title = soup.find(id="productTitle").get_text()
    print(f"I am watching: {title.strip()}")

check_price()
