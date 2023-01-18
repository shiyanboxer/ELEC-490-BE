import requests
from server import server
import flask.app as app
import unittest
from flask import Flask
import json

# https://docs.python.org/3/library/unittest.html
# https://www.w3schools.com/python/ref_requests_response.asp
# https://www.youtube.com/watch?v=iQVvpnRYl-w
# https://www.geeksforgeeks.org/get-post-requests-using-python/
# https://www.ontestautomation.com/writing-tests-for-restful-apis-in-python-using-requests-part-1-basic-tests/

API_URL_HELLO = "http://127.0.0.1:5000/"
API_URL_PREDICT = "http://127.0.0.1:5000/predict"

class TestCase(unittest.TestCase):
    # HELLO - status code - 200 (ok)
    def test_hello_status(self):
        response = requests.get(API_URL_HELLO)
        self.assertEqual(response.status_code, 200)
    
    # HELLO - checking request url
    def test_url(self):
        response = requests.get(API_URL_HELLO)
        self.assertEqual(response.url, API_URL_HELLO)

    # HELLO - request type
    def test_hello_status(self):
        response = requests.get(API_URL_HELLO)
        self.assertTrue(str(response.request), "[GET]")

    # HELLO - read contents type
    def test_hello_readcontent(self):
        response = requests.get(API_URL_HELLO)
        self.assertEqual(response.headers["Content-Type"], "text/html; charset=utf-8")
    
    # # HELLO - check for data returned
    def test_read_content(self):
        expectedResult = "hello world"
        response = requests.get(API_URL_HELLO)
        self.assertEqual(response.text, expectedResult)
    
    # -------------------------------------------------

    # # PREDICT - status code - 200 (ok) with parameters
    def test_predict_successful(self):
        parameter = {"total_funding": 100, "founded_year": 100}
        response = requests.post(API_URL_PREDICT, json = parameter)
        self.assertEqual(response.status_code, 200)

    # # PREDICT - method not allowed without parameters
    def test_predict_no_param(self):
        response = requests.post(API_URL_PREDICT)
        self.assertEqual(response.status_code, 500)
      
    # # PREDICT - check status code if only one paramters is passed in
    def test_predict_one_param(self):
        parameter_1 = {"total_funding": 100}
        parameter_2 = {"founded_year": 100}
        response_1 = requests.post(API_URL_PREDICT, json = parameter_1)
        response_2 = requests.post(API_URL_PREDICT, json = parameter_2)
        self.assertEqual(response_1.status_code, 500)
        self.assertEqual(response_2.status_code, 500)

    # # PREDICT - check status code if invalid parameter type is passed
    def test_predict_invalid_input(self):
        parameter = {"total_funding": 100, "founded_year": "one thousand"}
        response = requests.post(API_URL_PREDICT, json = parameter)
        self.assertEqual(response.status_code, 400)

    # # PREDICT - check response
    def test_predict_successful(self):
        parameter = {"total_funding": 100, "founded_year": 100}
        response = requests.post(API_URL_PREDICT, json = parameter)
        expected_result = "1.0"
        self.assertIn(expected_result, response.text)

if __name__ == '__main__':
    unittest.main()