import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import logging
from dataclasses import dataclass

# Configure logging for discrete error reporting
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProductData:
    """Dataclass holding extracted product information."""
    title: str
    price: float
    image_url: str
    source_url: str

class ScraperError(Exception):
    """Custom exception for scraping failures."""
    def __init__(self, message: str, url: str):
        self.url = url
        super().__init__(f"{message} | URL: {url}")

def get_soup(url: str) -> BeautifulSoup:
    """
    Fetches HTML content from URL and returns BeautifulSoup object.
    
    Args:
        url: The product URL to scrape.

    Returns:
        BeautifulSoup object.

    Raises:
        ScraperError: If HTTP request fails.
    """
    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/91.0.4472.124 Safari/537.36')
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        raise ScraperError(str(e), url)

def _parse_numeric_price(price_text: str) -> float:
    """Cleans price string and converts to float."""
    # Remove currency symbols and common delimiters
    clean_text = ''.join(c for c in price_text if c.isdigit() or c == '.')
    try:
        return float(clean_text)
    except ValueError:
        return 0.0

def scrape_example_shop(url: str) -> Optional[ProductData]:
    """
    Scraper logic implementation for Example Shop domains.
    Brutal extraction logic based on specific selectors.

    Args:
        url: Target product page URL.

    Returns:
        ProductData object or None if extraction fails.
    """
    try:
        soup = get_soup(url)
        
        # Brutally fetch elements based on assumed DOM structure
        # These selectors must be updated based on real target configuration
        title_element = soup.select_one('h1.product-title')
        price_element = soup.select_one('span.price-item--regular')
        image_element = soup.select_one('img.product__main-img')

        if not all([title_element, price_element, image_element]):
            logger.warning(f"Failed to find all required elements on {url}")
            return None

        title = title_element.get_text(strip=True)
        price_text = price_element.get_text(strip=True)
        price = _parse_numeric_price(price_text)
        
        # Extract src or data-src for image
        image_url = image_element.get('src') or image_element.get('data-src')
        if image_url and image_url.startswith('//'):
            image_url = 'https:' + image_url

        return ProductData(
            title=title,
            price=price,
            image_url=image_url if image_url else '',
            source_url=url
        )

    except ScraperError:
        return None
    except AttributeError as e:
        logger.error(f"Parsing error on {url}: {e}")
        return None

if __name__ == "__main__":
    # Test block for standalone execution of the scraper module
    TEST_URL = "https://example.com/product"
    print(f"Testing scrape on: {TEST_URL}")
    result = scrape_example_shop(TEST_URL)
    if result:
        print(f"Successfully scraped: {result}")
    else:
        print("Scraping failed.")