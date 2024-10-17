import requests
from bs4 import BeautifulSoup
import json

def fetch_link(year, month, date):
    # Format the URL
    url = "https://www.xwordinfo.com/Crossword?date={}/{}/20{}".format(month,date,year)
    
    # Fetch the webpage
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    
    # Parse the content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    return soup

def extract_clues(soup,type):
    # Find the clues container
    clues_container = soup.find('div', id='{}CluesPan'.format(type))
    clues = []

    # Get all the <div> elements in the clues section
    clue_divs = clues_container.find_all('div', class_='numclue')[0].find_all('div')

    for i in range(0, len(clue_divs), 2):  # Step by 2 to get pairs of number and clue
        number = clue_divs[i].text.strip()  # The number
        clue_text = clue_divs[i + 1].text.split(':')[0].strip()  # The clue text before the colon
        clues.append((int(number), clue_text))  # Append as tuple (number, clue)

    return clues

def get_grid(soup):    
    # Find the table
    table = soup.find('table', id='PuzTable')
    matrix = []
    
    # Iterate over rows in the table
    for row in table.find_all('tr'):
        row_data = []
        for cell in row.find_all('td'):
            if cell.get('class') == ['black']:
                row_data.append(".")  # Empty string for black cells
            else:
                letter_div = cell.find('div', class_='letter')
                row_data.append(letter_div.text.strip())
        matrix.append(row_data)

    return matrix

def get_gridnums(soup):
    # Find the table
    table = soup.find('table', id='PuzTable')
    matrix = []
    
    # Iterate over rows in the table
    for row in table.find_all('tr'):
        row_data = []
        for cell in row.find_all('td'):
            num_div = cell.find('div', class_='num')
            if num_div and num_div.text.strip():  # Check if num_div has text
                row_data.append(int(num_div.text.strip()))  # Number as string
            else:
                 row_data.append(0)
        matrix.append(row_data)

    return matrix


year = 24  # Replace with desired year
month = '10'  # Replace with desired month
date = '16'   # Replace with desired date
result = fetch_link(year, month, date)

across_clues = extract_clues(result,'A')
down_clues = extract_clues(result,'D')
grid = get_grid(result)
gridnums = get_gridnums(result)

data = {}
data['grid'] = grid
data['gridnums'] = gridnums
data['size'] = {}
data['size']['rows'] = len(grid)
data['size']['cols'] = len(grid[0])

data['clues'] = {}
data['clues']['across'] = {}
data['clues']['down'] = {}

for i in across_clues:
    data['clues']['across'][str(i[0])] = i[1]

for i in down_clues:
    data['clues']['down'][str(i[0])] = i[1]

json.dump(data,open('{}_{}_{}.json'.format(year,month,date),'w'))