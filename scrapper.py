import requests
from bs4 import BeautifulSoup
import time
from random import randint
import os
import csv

def list_to_csv(data, csv_filename):
    """
    Converts a list of dictionaries into a CSV file.
    
    Parameters:
        data (list): A list of dictionaries to be converted into CSV.
        csv_filename (str): The name of the output CSV file.
    """
    if not data:
        print("The input data is empty.")
        return

    # Extract the fieldnames from the keys of the first dictionary
    fieldnames = data[0].keys()

    try:
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # Write header (fieldnames)
            writer.writeheader()

            # Write the rows
            for row in data:
                # Clean up the 'localidad' field to remove unwanted newline characters
                row['localidad'] = row['localidad'].strip()  # Remove leading/trailing whitespaces and newlines
                writer.writerow(row)

        print(f"CSV file '{csv_filename}' has been created successfully!")
    except Exception as e:
        print(f"An error occurred while writing the CSV file: {e}")
        
# Function to define headers for the requests
def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }

def local_content_loader(page):
    with open(f'./cached_pages/index-{page}.html', 'r', encoding='utf-8') as file:
        content = file.read()
        print("Loaded content from local file './index.html'.")
        response = type('obj', (object,), {'text': content})  # Create a mock response object
        return response
    return None
# Function to send a GET request to the URL and get the response
def fake_fetch_page(url, headers):
    local_content_loader(1)

def fetch_page(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=1000)
        response.raise_for_status()  # Raise an error for bad status codes
        return response
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# Function to parse the page with BeautifulSoup and find the div by class
def parse_html(response, div_class):
    soup = BeautifulSoup(response.text, 'html.parser')
    divs = soup.find_all('div', class_=div_class)
    return divs

# Function to extract all the inner HTML from each div
def extract_content(divs):
    content_list = []
    for div in divs:
        try:
            if div:
                caracteristicas = div.find("div", class_="item-detail-char").find_all("span", class_="item-detail")

                habitaciones = caracteristicas[0].get_text().split(" ")[0]
                tamanio = caracteristicas[1].get_text().split(" ")[0]
                descripcion = caracteristicas[2].get_text()
                precio = div.find("span", class_="item-price h2-simulated").get_text().split("€")[0]
                direccion = "".join(div.find("a", class_="item-link").get_text()[9:].replace("\n","").split(",")[:2])
                link = div.find("a", class_="item-link")["href"]

                # Using .decode_contents() to get all inner HTML as a string
                #content_list.append(div.decode_contents().strip())
                content_list.append({"precio":precio,"localidad": direccion,"tamanio":tamanio,"habitaciones":habitaciones,"descripcion":descripcion, "link":link})
            else:
                content_list.append("Div not found.")
        except Exception:
            pass # Incase error in parsing don't add rubbish data
    return content_list

# Function to simulate human-like behavior by adding a delay
def random_sleep():
    time.sleep(randint(2, 20))  # Random sleep between 2-5 seconds to mimic human behavior

# Function to save the page content to a local file
def save_page_locally(url, content):
    filename = "./cached_pages/" + url.replace("https://", "").replace("http://", "").replace("/", "_") + ".html"
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
    divs = parse_html(response, div_class)
    content = extract_content(divs)  # Extract the content from the div
    return content

def get_div_content_local(id, div_class):
    
    # Try fetching the page, or load from local file if available
    response = local_content_loader(id)
    if not response:  # If the request fails, try loading from local file
        print("Fetching failed. Trying to load from local file...")
        page_content = load_page_from_file(id)
        if page_content:
            print("Loaded page from local file.")
            response = type('obj', (object,), {'text': page_content})  # Create a mock response object
        else:
            print("Page not found locally either.")
            return None

    # Save the fetched page locally for future use
    save_page_locally(url, response.text)

    # Parse the HTML and extract the div content
    divs = parse_html(response, div_class)
    content = extract_content(divs)  # Extract the content from the div
    return content


def get_url_for_page_number(page: int) -> str:
    return f"https://www.idealista.com/areas/alquiler-viviendas/con-precio-hasta_1200,de-dos-dormitorios,de-tres-dormitorios,de-cuatro-cinco-habitaciones-o-mas/pagina-{page}?shape=%28%28qvgvFbaxVbsEcjX_nRcdf%40vqt%40%7EnD%7Bl%40tvy%40_if%40pG%29%29"

if __name__ == "__main__":

    lista_final = []

    for i in range(6,10):
        url = get_url_for_page_number(i)
        div_class = "item-info-container"

        print(url)

        # Scrape the content from the URL
        content = get_div_content(url,div_class)#get_div_content_local(i,div_class)
        lista_final.extend(content)

        # Implement a delay to avoid being flagged as a bot
        random_sleep()
    
    list_to_csv(lista_final, 'properties.csv')
