from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
import json


class RequestFailedError(Exception):
    """Exception raised when the request was not successful (status code not equal to 200)."""

    def __init__(self, status_code):
        self.status_code = status_code
        message = f"Request failed with status code {status_code}"
        super().__init__(message)


class WikipediaScraper:
    """Class for scraping Wikipedia data and handling related operations."""

    def __init__(self):
        """Initialize the WikipediaScraper object."""
        self.base_url = "https://country-leaders.onrender.com"
        self.country_endpoint = "/countries"
        self.leaders_endpoint = "/leaders"
        self.cookies_endpoint = "/cookie"
        self.leaders_data = {}
        self.cookie = self.refresh_cookie()

    def refresh_cookie(self):
        """Refresh the authentication cookie from the server."""
        response = requests.get(self.base_url + self.cookies_endpoint)
        cookie = response.cookies.get_dict()
        if self.is_cookie_valid(cookie):
            return cookie
        else:
            response = requests.get(self.base_url + self.cookies_endpoint)
            new_cookie = response.cookies.get_dict()
            return new_cookie

    def is_cookie_valid(self, cookie):
        """Check if the authentication cookie is still valid."""
        if 'expires' in cookie:
            expire_time = datetime.strptime(cookie['expires'], '%a, %d %b %Y %H:%M:%S %Z')
            current_time = datetime.now()
            return expire_time > current_time
        else:
            return False

    def get_countries(self):
        """Retrieve the list of supported countries from the server."""
        response = requests.get(self.base_url + self.country_endpoint, cookies=self.cookie)
        countries = response.json()
        return countries

    def get_leaders(self, country: str):
        """Retrieve the list of leaders for a specific country from the server."""
        params = {"country": country}
        response = requests.get(self.base_url + self.leaders_endpoint, params=params, cookies=self.cookie)
        leaders = response.json()
        return leaders

    def get_first_paragraph(self, wikipedia_url: str):
        """
        Retrieve the first paragraph of the content from a Wikipedia URL.

        Parameters:
            wikipedia_url (str): The URL of the Wikipedia page.

        Returns:
            str: The cleaned first paragraph of the content.
        """
        response = requests.get(wikipedia_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
        else:
            raise RequestFailedError(response.status_code)

        paragraphs = soup.find_all("p")

        for paragraph in paragraphs:
            first_paragraph = paragraph.text.strip().replace('\n', '')
            cleaned_first_paragraph = re.sub(r'\[\d+\]', '', first_paragraph)
            cleaned_first_paragraph = re.sub(r'\\u[0-9a-fA-F]{4}', '', cleaned_first_paragraph)

            if first_paragraph:
                break
            else:
                print("Failed to fetch website data. Status code:", response.status_code)
        return cleaned_first_paragraph

    def to_json_file(self, filepath: str, leaders: dict, leader_id: str, cleaned_first_paragraph: str, indent: int = 0):
        """
        Write leader data with a cleaned first paragraph to a JSON file.

        Parameters:
            filepath (str): The path to the JSON file.
            leaders (dict): Dictionary containing leader data.
            leader_id (str): ID of the leader to update.
            cleaned_first_paragraph (str): Cleaned first paragraph of the content.
            indent (int): Indentation level for JSON formatting (default is 0).
        """
        leader_to_find = leader_id

        for leader in leaders:
            if 'id' in leader and leader['id'] == leader_to_find:
                leader["paragraph"] = cleaned_first_paragraph
                with open(filepath, 'w') as file:
                    json.dump(leader, file, indent=indent)
                break
        else:
            print(f"No entry found for the name '{leader_to_find}'.")
