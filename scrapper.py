import requests
from bs4 import BeautifulSoup
import time
from random import randint
import os
import csv
from fetcher import fetch_page


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
                # Remove leading/trailing whitespaces and newlines
                row['localidad'] = row['localidad'].strip()
                writer.writerow(row)

        print(f"CSV file '{csv_filename}' has been created successfully!")
    except Exception as e:
        print(f"An error occurred while writing the CSV file: {e}")


def local_content_loader(page):
    with open(f'./cached_pages/index-{page}.html', 'r', encoding='utf-8') as file:
        content = file.read()
        print("Loaded content from local file './index.html'.")
        # Create a mock response object
        response = type('obj', (object,), {'text': content})
        return response
    return None


# Function to parse the page with BeautifulSoup and find the div by class
def parse_html(response, div_class):
    soup = BeautifulSoup(response, 'html.parser')
    divs = soup.find_all('div', class_=div_class)
    return divs

# Function to extract all the inner HTML from each div


def extract_content(divs):
    content_list = []
    for div in divs:
        try:
            if div:
                caracteristicas = div.find(
                    "div", class_="item-detail-char").find_all("span", class_="item-detail")

                habitaciones = caracteristicas[0].get_text().split(" ")[0]
                tamanio = caracteristicas[1].get_text().split(" ")[0]
                descripcion = caracteristicas[2].get_text()
                precio = div.find(
                    "span", class_="item-price h2-simulated").get_text().split("€")[0]
                direccion = "".join(div.find(
                    "a", class_="item-link").get_text()[9:].replace("\n", "").split(",")[:2])
                link = div.find("a", class_="item-link")["href"]

                # Using .decode_contents() to get all inner HTML as a string
                # content_list.append(div.decode_contents().strip())
                content_list.append({"precio": precio, "localidad": direccion, "tamanio": tamanio,
                                    "habitaciones": habitaciones, "descripcion": descripcion, "link": link})
            else:
                content_list.append("Div not found.")
        except Exception:
            pass  # Incase error in parsing don't add rubbish data
    return content_list


# Function to simulate human-like behavior by adding a delay
def random_sleep():
    time.sleep(randint(2, 20))


# Function to save the page content to a local file
def save_page_locally(url, content):
    filename = "./cached_pages/" + \
        url.replace("https://", "").replace("http://",
                                            "").replace("/", "_") + ".html"
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Page saved locally as {filename}")


# Function to load the page content from a local file
def load_page_from_file(url):
    filename = url.replace("https://", "").replace("http://",
                                                   "").replace("/", "_") + ".html"
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    else:
        return None


# Main function that brings everything together
def get_div_content(url, div_class):

    # Try fetching the page, or load from local file if available
    response = fetch_page(url)
    if not response:  # If the request fails, try loading from local file
        print("Fetching failed. Trying to load from local file...")
        page_content = load_page_from_file(url)
        if page_content:
            print("Loaded page from local file.")
            # Create a mock response object
            response = type('obj', (object,), {'text': page_content})
        else:
            print("Page not found locally either.")
            return None

    # Save the fetched page locally for future use
    save_page_locally(url, response)

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
            # Create a mock response object
            response = type('obj', (object,), {'text': page_content})
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
    return f"https://www.idealista.com/alquiler-viviendas/barcelona/ciutat-vella/con-de-un-dormitorio,de-dos-dormitorios,de-tres-dormitorios/pagina-{page}.htm"


if __name__ == "__main__":

    lista_final = []

    for i in range(2, 3):
        url = get_url_for_page_number(i)
        div_class = "item-info-container"

        print(url)

        # Scrape the content from the URL
        # get_div_content_local(i,div_class)
        content = get_div_content(url, div_class)
        lista_final.extend(content)

        # Implement a delay to avoid being flagged as a bot
        random_sleep()

    list_to_csv(lista_final, 'properties.csv')
