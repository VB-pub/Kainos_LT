
from scraper import Scraper

scraper = Scraper()
scraper.load_page()
scraper.cookie_trust_handle()

root_categories = scraper.get_category_root()

for cat in root_categories:
    scraper.try_get_category_recursive(cat)

print('OK')