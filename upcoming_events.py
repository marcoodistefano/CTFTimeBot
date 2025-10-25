from bs4 import BeautifulSoup # Import BeautifulSoup for parsing HTML and XML documents
import re # Import the regular expression module
import requests # Import requests for making HTTP requests
import json # Import json for working with JSON data

location_pattern = r"On-line" # Define a regex pattern to match "On-line" for event locations

# Function to find all events within a target HTML division (table)
def find_all_events(target_div):
    events = [] # Initialize an empty list to store found events
    # Iterate through each table row (<tr>) within the target_div
    for tr in target_div.find_all("tr"):
        # Check if the row text contains the 'location_pattern' (i.e., "On-line")
        if re.search(location_pattern, tr.text):
            data = [] # Initialize an empty list to store data from table cells
            # Iterate through each table data cell (<td>) within the current row
            for td in tr.find_all("td"):
                data.append(td.text.strip()) # Append the stripped text content of the cell to data
                if len(data) == 3: # If we have collected 3 pieces of data (e.g., name, schedule, type)
                    break # Stop collecting data for this row
            # Find the first anchor tag (<a>) within the row and get its 'href' attribute (the link)
            link = tr.find("a")['href'] if tr.find("a") else None
            # If we have 3 data points and a link, add the event to the events list
            if len(data) == 3 and link:
                # Add a tuple (event_name, event_schedule, event_type, event_link) to the results list
                events.append((data[0], data[1], data[2], link))
                
    return events # Return the list of extracted events

def main() -> None:
    # Define the URL for the upcoming CTFtime events list
    url = 'https://ctftime.org/event/list/upcoming'
    # Define HTTP headers to mimic a web browser, which can be helpful to avoid being blocked
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}

    # Make an HTTP GET request to the URL with the defined headers
    r = requests.get(url, headers=headers)
    # Parse the HTML content of the response using BeautifulSoup
    soup = BeautifulSoup(r.content, 'html.parser')

    # Find the target <div> (which is actually a <table> in this case) that contains the event list
    # We are looking for a <table> with the class "table table-striped"
    target_div = soup.find("table", class_="table table-striped") # Ensure the correct class is used

    # Extract the events using the find_all_events function
    events = find_all_events(target_div)
    # Print the extracted events as a JSON formatted string to standard output
    print(json.dumps(events))

# This block ensures that main() is called only when the script is executed directly
if __name__ == '__main__':
    main()