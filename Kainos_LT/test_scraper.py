import unittest
from unittest.mock import patch, MagicMock
from selenium.webdriver.common.by import By
from scraper import Scraper
from models import Category, Item, Shop

class TestScraper(unittest.TestCase):
    def setUp(self):
        # Initialize the Scraper with headless option for testing
        self.scraper = Scraper(headless=True)

    @patch('selenium.webdriver.Chrome')
    def test_load_page(self, MockWebDriver):
        self.scraper.driver = MockWebDriver()
        self.scraper.load_page()
        self.scraper.driver.get.assert_called_with(self.scraper.base_url)

    def test_initialization(self):
        """
        Test the initialization of the Scraper class to ensure the base URL, shut_down flag,
        and threads list are correctly set.
        """
        self.assertEqual(self.scraper.base_url, 'https://www.kainos.lt/')
        self.assertFalse(self.scraper.shut_down)
        self.assertIsInstance(self.scraper.threads, list)

    @patch('concurency.Worker.cancel_all')
    def test_cancel(self, mock_cancel_all):
        self.scraper.cancel()
        self.assertTrue(self.scraper.shut_down)
        mock_cancel_all.assert_called_once()

if __name__ == '__main__':
    unittest.main()
