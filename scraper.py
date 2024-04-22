import requests
from bs4 import BeautifulSoup
import sqlite3

import requests

# Connect to the database
db = sqlite3.connect('news.db')
cursor = db.cursor()

def scrape_news(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Scrape the news articles on the page
        for index, element in enumerate(soup.select('.default__item')):
            title = element.select_one('.default__item--title').get_text().strip()
            category = soup.select('.bread-crumb__title')[-1].get_text().strip()
            link = url
            image = element.select_one('.default__item--img img')['data-src']
            content = element.select_one('.default__item--content').get_text().strip() or None

            # Insert the news article into the database
            cursor.execute('''
                INSERT INTO news (title, category, link, image, content)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, category, link, image, content))
            db.commit()
            print(f"Scraped news article {index + 1}: {title}")

        # Get the next page link
        next_link = soup.select_one('.prev-next-item-next')['href']
        if next_link:
            scrape_news(next_link)
        else:
            print("No more pages to scrape.")
            db.close()

# Check if the database and table already exist
cursor.execute('SELECT * FROM news LIMIT 1')
row = cursor.fetchone()

if row:
    # Get the latest link from the database
    cursor.execute('SELECT link FROM news ORDER BY id DESC LIMIT 1')
    latest_link = cursor.fetchone()[0]

    # Get the next page link
    response = requests.get(latest_link)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        next_link = soup.select_one('.prev-next-item-next')['href']
        if next_link:
            scrape_news(next_link)
        else:
            print("No more pages to scrape.")
            db.close()
else:
    # Create the table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            category TEXT,
            link TEXT,
            image TEXT,
            content TEXT
        )
    ''')

    # Set the starting URL
    starting_url = 'https://www.maannews.net/news/1.html'
    scrape_news(starting_url)