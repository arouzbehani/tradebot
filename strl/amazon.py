import requests
from bs4 import BeautifulSoup

# Product URL
url = "https://www.amazon.com/dp/B07FDF9B46"  

def scrape_page():
  
    # Get HTML and parse
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract relevant data
    data = {
        "title": soup.select_one("#productTitle").get_text().strip(),
        "price": float(soup.select_one("span .a-price-whole").get_text()),
        "rating": float(soup.select_one("i.reviewCountText").get_text().split()[0]), 
        "description": soup.select_one("#feature-bullets").get_text().strip()
    }
    
    return data

def print_data(data):

    print('Product Data:')
    for key, value in data.items():
        print(f'- {key}: {value}')

# Main function
def main():

    data = scrape_page()
    print_data(data)

if __name__ == '__main__':
    main()