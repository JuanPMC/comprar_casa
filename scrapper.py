import requests
from bs4 import BeautifulSoup
import time
from random import randint
import os

# Function to define headers for the requests
def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }

# Function to send a GET request to the URL and get the response
def fetch_page(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        return response
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# Function to parse the page with BeautifulSoup and find the div by class
def parse_html(response, div_class):
    soup = BeautifulSoup(response.text, 'html.parser')
    div = soup.find('div', class_=div_class)
    return div

# Function to extract content from the div if it exists
def extract_content(div):
    if div:
        return div.text.strip()
    else:
        return "Div not found."

# Function to simulate human-like behavior by adding a delay
def random_sleep():
    time.sleep(randint(2, 5))  # Random sleep between 2-5 seconds to mimic human behavior

# Function to save the page content to a local file
def save_page_locally(url, content):
    filename = url.replace("https://", "").replace("http://", "").replace("/", "_") + ".html"
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Page saved locally as {filename}")

# Function to load the page content from a local file
def load_page_from_file(url):
    filename = url.replace("https://", "").replace("http://", "").replace("/", "_") + ".html"
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    else:
        return None

# Main function that brings everything together
def get_div_content(url, div_class):
    headers = get_headers()  # Get headers
    
    # Try fetching the page, or load from local file if available
    response = fetch_page(url, headers)
    if not response:  # If the request fails, try loading from local file
        print("Fetching failed. Trying to load from local file...")
        page_content = load_page_from_file(url)
        if page_content:
            print("Loaded page from local file.")
            response = type('obj', (object,), {'text': page_content})  # Create a mock response object
        else:
            print("Page not found locally either.")
            return None

    # Save the fetched page locally for future use
    save_page_locally(url, response.text)

    # Parse the HTML and extract the div content
    div = parse_html(response, div_class)
    content = extract_content(div)  # Extract the content from the div
    return content

# If this script is run directly, you can use this block for testing
if __name__ == "__main__":
    url = "https://www.idealista.com/areas/alquiler-viviendas/con-precio-hasta_1000,de-dos-dormitorios,de-tres-dormitorios,de-cuatro-cinco-habitaciones-o-mas/pagina-2?shape=%28%28qvgvFbaxVbsEcjX_nRcdf%40vqt%40%7EnD%7Bl%40tvy%40_if%40pG%29%29"  # Replace with the URL you want to scrape
    div_class = "item-info-container"   # Replace with the class of the div you're looking for

    # Scrape the content from the URL
    content = get_div_content(url, div_class)

    if content:
        print("Div content:", content)

    # Implement a delay to avoid being flagged as a bot
    random_sleep()
