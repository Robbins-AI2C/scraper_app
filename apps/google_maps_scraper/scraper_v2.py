#Generated by ChatGPT as suggested improvements from v1

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from dataclasses import dataclass, asdict, field
import argparse
import pandas as pd
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# Data structure for storing business details
@dataclass
class Business:
    name: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    phone_number: Optional[str] = None


# Wrapper class for managing a list of businesses
@dataclass
class BusinessList:
    business_list: list[Business] = field(default_factory=list)

    def to_dataframe(self):
        """Converts the business list to a pandas DataFrame."""
        return pd.json_normalize((asdict(business) for business in self.business_list), sep="")

    def save_to_csv(self, filename: str):
        """Saves the business list to a CSV file."""
        self.to_dataframe().to_csv(f"{filename}.csv", index=False)
        logging.info(f"Data saved to {filename}.csv")

    def save_to_excel(self, filename: str):
        """Saves the business list to an Excel file."""
        self.to_dataframe().to_excel(f"{filename}.xlsx", index=False)
        logging.info(f"Data saved to {filename}.xlsx")


def scrape_google_maps(search_query: str, headless: bool = True, timeout: int = 30000):
    """Scrapes Google Maps for business data based on the search query."""
    business_list = BusinessList()

    with sync_playwright() as p:
        try:
            logging.info("Launching browser...")
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()

            logging.info("Navigating to Google Maps...")
            page.goto("https://www.google.com/maps", timeout=timeout)

            # Input search query
            logging.info(f"Searching for: {search_query}")
            page.locator('//input[@id="searchboxinput"]').fill(search_query)
            page.keyboard.press("Enter")
            page.wait_for_timeout(10000)  # Wait for search results to load

            # Extract business listings
            listings = page.locator('//div[@role="article"]').all()
            logging.info(f"Found {len(listings)} listings.")

            for i, listing in enumerate(listings[:5], start=1):  # Limit to top 5 results
                logging.info(f"Processing listing {i}...")
                listing.click()
                page.wait_for_timeout(2000)  # Wait for details to load

                # Extract business details
                business = Business()
                try:
                    business.name = page.locator('//h1[contains(@class, "fontHeadlineLarge")]/span[2]').inner_text()
                except PlaywrightTimeoutError:
                    logging.warning("Failed to extract business name.")
                try:
                    business.address = page.locator('//button[@data-item-id="address"]//div[contains(@class, "fontBody")]').inner_text()
                except PlaywrightTimeoutError:
                    logging.warning("Failed to extract business address.")
                try:
                    business.website = page.locator('//a[@data-item-id="authority"]//div[contains(@class, "fontBody")]').inner_text()
                except PlaywrightTimeoutError:
                    logging.warning("Failed to extract business website.")
                try:
                    business.phone_number = page.locator('//button[contains(@data-item-id, "phone:tel:")]//div').inner_text()
                except PlaywrightTimeoutError:
                    logging.warning("Failed to extract business phone number.")

                business_list.business_list.append(business)

            # Save results
            business_list.save_to_csv("google_maps_data")
            business_list.save_to_excel("google_maps_data")

        except Exception as e:
            logging.error(f"An error occurred: {e}")
        finally:
            browser.close()
            logging.info("Browser closed.")

    return business_list


def main():
    parser = argparse.ArgumentParser(description="Scrape Google Maps for business details.")
    parser.add_argument("-s", "--search", type=str, default="restaurants", help="Search term (e.g., 'restaurants').")
    parser.add_argument("-l", "--location", type=str, default="New York", help="Location for the search.")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode.")
    parser.add_argument("--timeout", type=int, default=30000, help="Page timeout in milliseconds.")
    args = parser.parse_args()

    # Combine search term and location
    search_query = f"{args.search} {args.location}"
    logging.info(f"Starting scrape with query: {search_query}")

    # Run the scraping function
    scrape_google_maps(search_query, headless=args.headless, timeout=args.timeout)


if __name__ == "__main__":
    main()