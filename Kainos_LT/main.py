
from scraper import Scraper
import argparse, helpers, models

def main():
    parser = argparse.ArgumentParser(description='Run a web scraper with customizable options.')
    parser.add_argument('--time_limit', type=int, default=120, help='Time limit for the scraping process in seconds.')
    parser.add_argument('--thread_count', type=int, default=2, help='Number of threads for concurrent scraping.')
    parser.add_argument('--max_thread_count', type=int, default=5, help='Maximum number of threads for concurrent scraping.')
    args = parser.parse_args()

    scraper = Scraper(item_page_concurency=args.thread_count, max_concurency=args.max_thread_count)
    scraper.run(time_limit=args.time_limit)
    
    json_str = helpers.Data2Json.convert(models.Element.categories)
    helpers.Data2Json.save_to_disk(json_str)

    print('OK')

if __name__ == '__main__':
    main()