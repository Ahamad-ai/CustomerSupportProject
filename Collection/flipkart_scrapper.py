import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys
sys.path.append("D:/Projects/CustomerSupportSystem/")
from exception.exceptions import CustomerSupportSystemException
import emoji


class FlipkartScraper:
    """Class to scrape product details from Flipkart."""

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    BASE_URL = "https://www.flipkart.com/search?q={product_category}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"

    def __init__(self, product_category):
        self.product_category = product_category
        self.data_dict = {
            "product_title": [],
            "product_price": [],
            "product_rating": [],
            "product_highlights":[],
            "product_description": [],
            "product_reviews": [],
            "product_link": []
        }

    @staticmethod
    def get_title(soup):
        """Extracts the product title."""
        try:
            title = soup.find("span", attrs={"class": "VU-ZEz"})
            return title.text if title else "NA"
        except Exception as e:
            raise CustomerSupportSystemException(f"Error fetching title: {e}")

    @staticmethod
    def get_price(soup):
        """Extracts the product price."""
        try:
            price = soup.find("div", attrs={"class": "Nx9bqj CxhGGd"})
            return price.text if price else "NA"
        except Exception as e:
            raise CustomerSupportSystemException(f"Error fetching price: {e}")

    @staticmethod
    def get_rating(soup):
        """Extracts the product rating."""
        try:
            rating = soup.find("div", attrs={"class": "XQDdHH"})
            return rating.text if rating else "NA"
        except Exception as e:
            raise CustomerSupportSystemException(f"Error fetching rating: {e}")

    @staticmethod
    def get_description(soup):
        """Extracts the product description."""
        try:
            description = soup.find("div",attrs={"class":"yN+eNk w9jEaj"})
            return description.text if description and len(description.text) > 0 else "NA"
        except Exception as e:
            raise CustomerSupportSystemException(f"Error fetching description: {e}")

    @staticmethod
    def get_reviews(soup):
        """Extracts product reviews."""
        try:
            reviews = soup.find_all("div", attrs={"class": "ZmyHeo"})
            return " ".join([rev.text for rev in reviews]) if reviews else "NA"
        except Exception as e:
            raise CustomerSupportSystemException(f"Error fetching reviews: {e}")

    @staticmethod
    def get_highlights(soup):
        try:
            product_highlights= soup.find_all("li",attrs={"class":"_7eSDEz"})
            return " ".join([highlights.text for highlights in product_highlights]) if product_highlights else "NA"
        except Exception as e:
            raise CustomerSupportSystemException(f"Error fetching reviews: {e}")


    def get_product_links(self):
        """Fetches product links from Flipkart search results."""
        search_url = self.BASE_URL.format(product_category=self.product_category)
        webpage = requests.get(search_url, headers=self.HEADERS)
        soup = BeautifulSoup(webpage.content, "html.parser")

        links = soup.find_all("a", attrs={"class": "CGtC98"})
        return ["https://flipkart.com" + link.get("href") for link in links if link.get("href")]
    
    def remove_emojis(self,text):
        return emoji.replace_emoji(text, replace="")
    
    def remove_READMORE(self,text):
        return text.replace("READ MORE","")

    def scrape_products(self):
        """Scrapes product details and stores them in a DataFrame."""
        product_links = self.get_product_links()

        for product_link in product_links:
            new_webpage = requests.get(product_link, headers=self.HEADERS)
            new_soup = BeautifulSoup(new_webpage.content, "html.parser")

            self.data_dict["product_title"].append(self.get_title(new_soup))
            self.data_dict["product_price"].append(self.get_price(new_soup))
            self.data_dict["product_rating"].append(self.get_rating(new_soup))
            self.data_dict["product_highlights"].append(self.get_highlights(new_soup))
            self.data_dict["product_description"].append(self.get_description(new_soup))
            self.data_dict["product_reviews"].append(self.get_reviews(new_soup))
            self.data_dict["product_link"].append(product_link)

        flipkart_scrape_df=pd.DataFrame.from_dict(self.data_dict)
        flipkart_scrape_df.drop(flipkart_scrape_df[flipkart_scrape_df["product_title"] == "NA"].index,inplace=True)
        flipkart_scrape_df["product_reviews"]=flipkart_scrape_df["product_reviews"].apply(self.remove_READMORE)
        flipkart_scrape_df["product_reviews"]=flipkart_scrape_df["product_reviews"].apply(self.remove_emojis)
        return flipkart_scrape_df

# Example usage
if __name__ == "__main__":
    product_category = "samsung"
    scraper = FlipkartScraper(product_category)
    df = scraper.scrape_products()
    print(df.head())  
    df.to_csv("flipkart_data.csv", index=False)