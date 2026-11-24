import unittest
import os
import random
import time
from unittest.mock import MagicMock, patch
from Speller import app
from Dictionary import Dictionary

class SpellerTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        time.time = MagicMock(return_value=1)
        random.randrange = MagicMock(return_value=0)

    def tearDown(self):
        if (os.path.exists('test21')):
            os.remove('test21')
        if (os.path.exists('test.res')):
            os.remove("test.res")

    def test_count(self):
        result = self.app.get("/count")
        
        self.assertEqual(result.data, b'{"count": 2}')
        
    def test_dictionary(self):
        result = self.app.get("/dictionary")
        
        self.assertEqual(result.data, b'{"words": ["lyuk", "juh"]}')
    
    def test_dictionary_add_remove(self):
        result = self.app.get("/dictionary/add/faj")
        
        self.assertEqual(result.data, b'{"word": "faj"}')
        
        result = self.app.get("/dictionary")
        
        self.assertEqual(result.data, b'{"words": ["lyuk", "juh", "faj"]}')
        
        result = self.app.get("/dictionary/delete/faj")
        
        self.assertEqual(result.data, b'{"words": ["lyuk", "juh"]}')
        
    def test_start(self):
        result = self.app.get("/start/test/2/normal")

        self.assertEqual(result.data, b'{"word": "*uk", "id": "test21"}')
        
    def test_word(self):
        self.app.get("/start/test/2/normal")

        result = self.app.get("/word/test21/0")
                
        self.assertEqual(result.data, b'{"word": "*uk", "id": "test21"}', "Word Failed")

        result = self.app.get("/word/test21/1")
        
        self.assertEqual(result.data, b'{"word": "*uh", "id": "test21"}', "Word Failed")
    
    def test_faulty_answer(self):
        self.app.get("/start/test/2/normal")
        self.app.get("/answer/test21/0/j")
        result = self.app.get("/answer/test21/1/j")

        self.assertEqual(result.data, b'{"result": "1 out of 2", "previous": []}', "Result Failed")
        
    def test_result(self):
        self.app.get("/start/test/2/normal")
        self.app.get("/answer/test21/0/j")
        self.app.get("/answer/test21/1/j")
        self.app.get("/start/test/1/normal")
        result = self.app.get("/answer/test11/0/ly")

        self.assertEqual(result.data, b'{"result": "1 out of 1", "previous": ["1 out of 2"]}', "Result Failed")

    def test_recurring(self):
        self.app.get("/start/test/1/recurring")
        result = self.app.get("/answer/test11/0/j")
        
        self.assertEqual(result.data, b'{"word": "*uk", "id": "test11"}', "Answer Failed")
        
        result = self.app.get("/answer/test11/0/j")
        
        self.assertEqual(result.data, b'{"word": "*uk", "id": "test11"}', "Answer Failed")
        
        result = self.app.get("/answer/test11/0/ly")
        
        self.assertEqual(result.data, b'{"result": "2 times failed", "previous": []}', "Result Failed")
        
    def test_recurring_result(self):
        self.app.get("/start/test/1/recurring")
        self.app.get("/answer/test11/0/j")
        self.app.get("/answer/test11/1/ly")
        self.app.get("/start/test/1/recurring")
        result = self.app.get("/answer/test11/0/ly")
        
        self.assertEqual(result.data, b'{"result": "0 times failed", "previous": ["1 times failed"]}', "Result Failed")

    def test_error_word(self):
        result = self.app.get("/word/test21/1")

        self.assertEqual(result.data, b'{"error": "Failed to load test"}')

    def test_error_answer(self):
        result = self.app.get("/answer/test21/1/j")

        self.assertEqual(result.data, b'{"error": "Failed to load test"}')

if __name__ == '__main__':
    dictionary = Dictionary("test_words.json")
    with patch("Speller.dictionary", dictionary):        
        unittest.main()