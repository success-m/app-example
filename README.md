# app-example
Am example app to charge a credit card. Application explores the concept of cryptography, proxy and payment gateways based on a Flask API.

## Requirements

### 3 Backend APIs

* Locker
* Proxy
* Payment Gateway

### 1 Front end client with Inputs

* Name on Card
* Credit Card Number
* Expiry Month, Expiry Year
* CVV

### Workflow

* Get public key from Locker
* Encrypt Credit Card Number with public key
* Post encrypted Credit Card to Locker
* Locker returns a token mapped with the Credit Card Number
* Post all data to Proxy along with the token
* Proxy sends request to Locker along with the token
* Locker de-tokenizes the token and sends request to Payment Gateway with actual Credit Card Number

## Details

### Python version
python 3.5.2

### Install Dependencies
```
pip install -r requirements.txt
```

### Run application
```
python app.py
```

### Application URL
```
http://localhost:5000/
```

## Notes

* All routes are registered in app.py
* API resource controllers are in resource_controller.py
* Front-end template is in templates/home.html
* Additional front-end resources are loaded through a CDN


