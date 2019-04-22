import urllib.parse

from flask_restful import Resource
from flask import request
import http.client
import json

from config import ap_url
from locker import Ap_Locker
from payment_gateway import Ap_Payment_Gateway


class Ap_Base_Resource(Resource):
    # Base Class to manage REST Resource Controllers
    def __init__(self):
        self.get_methods = {}
        self.post_methods = {}

    def get_data(self, key="", default=""):
        return request.values.get(key, default)

    def get(self, type=""):
        # returns JSON datatype through endpoint, handled by flask-restful lib.
        if type in self.get_methods:
            return self.get_methods[type]()
        else:
            return self.no_route()

    def post(self, type=""):
        # returns JSON datatype through endpoint, handled by flask-restful lib.
        if type in self.post_methods:
            return self.post_methods[type]()
        else:
            return self.no_route()

    def no_route(self):
        return {"status": 404, "message": "Oops!! Nothing to display"}

class Ap_Locker_Controller(Ap_Base_Resource):
    # Resource Controller to manage the routes as a Facade for Locker
    def __init__(self):
        super(Ap_Locker_Controller, self).__init__()

        # register all get methods
        self.get_methods = {
            "public_key": self.public_key
        }

        # register all post methods
        self.post_methods = {
            "token": self.get_token,
            "detokenize": self.detokenize
        }

    def get_token(self):
        card = self.get_data(key="card", default="")
        return {"token": Ap_Locker().get_token(data=card)}

    def public_key(self):
        return {"key": Ap_Locker().get_password()}

    def detokenize(self):
        form_data = {
            "token": self.get_data(key="token", default=""),
            "name": self.get_data(key="name", default=""),
            "card_number": self.get_data(key="card_number", default=""),
            "expiry": self.get_data(key="expiry", default=""),
            "cvv": self.get_data(key="cvv", default="")
        }

        return Ap_Locker().detokenize(form_data=form_data)


class Ap_Payment_Gateway_Controller(Ap_Base_Resource):
    def __init__(self):
        super(Ap_Payment_Gateway_Controller, self).__init__()

        # register all post methods
        self.post_methods = {
            "process": self.process
        }

    def process(self):
        form_data = {
            "token": self.get_data(key="token", default=""),
            "name": self.get_data(key="name", default=""),
            "card_number": self.get_data(key="card_number", default=""),
            "expiry": self.get_data(key="expiry", default=""),
            "cvv": self.get_data(key="cvv", default="")
        }

        return Ap_Payment_Gateway.process(form_data)


class Ap_Proxy_Controller(Ap_Base_Resource):
    def __init__(self):
        super(Ap_Proxy_Controller, self).__init__()

        # register all post methods
        self.post_methods = {
            "process": self.process
        }

    def process(self):
        try:
            form_data = {
                "token": self.get_data(key="token", default=""),
                "name": self.get_data(key="name", default=""),
                "card_number": self.get_data(key="card_number", default=""),
                "expiry": self.get_data(key="expiry", default=""),
                "cvv": self.get_data(key="cvv", default="")
            }

            # detokenize card number without API call
            # return Ap_Locker().detokenize(form_data=form_data)

            conn = http.client.HTTPConnection(ap_url)
            payload = urllib.parse.urlencode(form_data)
            headers = {'Content-Type': "application/x-www-form-urlencoded"}
            conn.request("POST", "/locker/detokenize", payload, headers)
            res = conn.getresponse()
            data = res.read()
            return json.loads(data.decode("utf-8"))
        except Exception as e:
            return {"status": 400, "message": "Cannot read card number."}

