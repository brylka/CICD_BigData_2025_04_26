import unittest
from application import application


class FlaskAppTest(unittest.TestCase):
    def setUp(self):
        self.app = application.test_client()
        self.app.testing = True

    def test_home_page(self):
        """Test czy strona główna zawiera oczekiwany tekst."""
        response = self.app.get('/')
        data = response.data.decode('utf-8')
        self.assertIn('Hello, BigData z Pythonem!', data)

    def test_page_loads(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
