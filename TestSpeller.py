import unittest
import json
import os
import random
import time
from unittest.mock import MagicMock, patch
from Speller import app 

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
        
    def test_start(self):
        result = self.app.get("/start/test/2")

        self.assertEqual(result.data, b'{"word": "*uk", "id": "test21"}')
        
    def test_next_word(self):
        self.app.get("/start/test/2")
        result = self.app.get("/next/test21/*uk/ly")
        
        self.assertEqual(result.data, b'{"word": "*uh", "id": "test21"}', "Next Failed")
    
    def test_faulty_answer(self):
        self.app.get("/start/test/2")
        self.app.get("/next/test21/*uk/j")
        result = self.app.get("/next/test21/*uh/j")

        self.assertEqual(result.data, b'{"result": "1 out of 2", "previous": []}', "Result Failed")
        
    def test_result(self):
        self.app.get("/start/test/2")
        self.app.get("/next/test21/*uk/j")
        self.app.get("/next/test21/*uh/j")
        self.app.get("/start/test/1")
        result = self.app.get("/next/test11/*uk/ly")

        self.assertEqual(result.data, b'{"result": "1 out of 1", "previous": ["1 out of 2"]}', "Result Failed")
        

if __name__ == '__main__':
    with patch("Speller.WORD_DICTIONARY", "test_words.json"):
        unittest.main()