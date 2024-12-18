from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import argparse
import pandas as pd

# sets up the data objects to be collected
@dataclass
class Business:
    name:str = None
    address:str = None
    website:str = None
    phone_number:str = None
    
# creates the list of the businesses collected
@dataclass
class BusinessList:
    business_list:list[Business] = field(default_factory=list)
    
    def dataframe(self):
        return pd.json_normalize((asdict(business) for business in self.business_list), sep='')
    
    def save_to_csv(self,filename):
        self.dataframe().to_csv(f"{filename}.csv", index=False)
        
    def save_to_excel(self,filename):
        self.dataframe().to_excel(f"{filename}.xlsx", index=False)
    
    
def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.goto('https://www.google.com/maps', timeout=60000) # timeout is 60 seconds
        page.wait_for_timeout(2000) # sleeps for 2 seconds but not needed
        
        page.locator('//input[@id="searchboxinput"]').fill(search_for)
        page.wait_for_timeout(1000)
        
        page.keyboard.press('Enter')
        page.wait_for_timeout(1000)
        
        listings = page.locator('//div[@role="article"]').all()
        print(len(listings))
        
        business_list = BusinessList() #no argument passed because of first line in BusinessList class
        
        for listing in listings[:5]:
            listing.click()
            page.wait_for_timeout(2000)

            # grabs the data from each section in the html
            name_xpath = '//h1[contains(@class, "fontHeadlineLarge")]/span[2]'
            # address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBody")]'
            # website_xpath = '//a[@data-item-id-"authority"]//div[contains(@class, "fontBodyMe)]'
            # phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains()]'
            
            # grabs just the text in the html and stores it within the Business dataclass 
            business = Business()
            business.name = page.locator(name_xpath).inner_text()
            # business.address = page.locator(address_xpath).inner_text()
            # business.website = page.locator(website_xpath).inner_text()
            # business.phone_number = page.locator(phone_number_xpath).inner_text()
            
            business_list.business_list.append(business)
            
        business_list.save_to_csv('google_maps_data')
        business_list.save_to_excel('google_maps_data')
        
        browser.close()
    
        
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search", type=str)
    parser.add_argument("-l", "--location", type=str)
    args = parser.parse_args()
    
    if args.location and args.search:
        search_for = f'{args.search} {args.location}'
    else:
        search_for = 'restaurants new york'
        
    main()