from src.scraper import WikipediaScraper

def main():
    """
    Main function to interact with the WikipediaScraper and retrieve leader data.
    
    The function prompts the user to select a country, then a leader within that country,
    and retrieves the first paragraph of the leader's Wikipedia page. It then saves the
    leader data along with the first paragraph to a JSON file.
    """
    # Create WikipediaScraper object
    scraper = WikipediaScraper()

    # Get supported countries
    countries = scraper.get_countries()
    
    # Display the list of countries
    print("\nAvailable countries:")
    for i, country in enumerate(countries, 1):
        print(f"{i}. {country}")  

    # Ask the user to select a country
    selection = input("\nEnter the number of the country you want to get leaders for: ")

    # Validate user input
    try:
        selection_index = int(selection) - 1
        if selection_index < 0 or selection_index >= len(countries):
             raise ValueError
    except ValueError:
        print("Invalid selection. Please enter a valid number.")
        exit()

    # Get the selected country
    country = countries[selection_index]

    # Get leaders for the selected country
    leaders = scraper.get_leaders(country)        

    # Display the list of leaders in the selcted country
    print("\nAvailable leaders:")
    for i, leader in enumerate(leaders, 1):
        print(f"{i}. {leader['first_name'] + ' ' + leader['last_name']}")  

    # Ask the user to select a leader
    selection = input("\nEnter the number of the leader you want to get the 1st quote for: ")
    
    # Validate user input
    try:
        selection_index = int(selection) - 1
        if selection_index < 0 or selection_index >= len(leaders):
             raise ValueError
    except ValueError:
        print("Invalid selection. Please enter a valid number.")
        exit()

    # Extract Wikipedia URL based on leader's selection
    wikipedia_url = leaders[selection_index]['wikipedia_url']    
    first_paragraph = scraper.get_first_paragraph(wikipedia_url)    

    # Save leaders data to JSON file
    leader_id = leaders[selection_index]['id']
    scraper.to_json_file("leaders_data.json", leaders, leader_id, first_paragraph) 
     
if __name__ == "__main__":
    main()
