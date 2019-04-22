from authorizenet import apicontractsv1
from authorizenet.apicontrollers import createTransactionController

class Ap_Payment_Gateway():
    @staticmethod
    def process(data):
        # reference https://github.com/AuthorizeNet/sample-code-python/blob/master/PaymentTransactions/charge-credit-card.py
        # todo testing in a sandbox environment.

        try:
            # prepare data for sending out to Authorize.net
            name = data["name"].strip().split(" ")
            data["first_name"] = name[0] if len(name) else ""
            data["last_name"] = name[len(name) - 1] if len(name) > 1 else ""
            data["card_number"] = data["card_number"].replace("-", "").replace("/", "")
            data["expiry"] = data["expiry"].replace("-", "").replace("/", "")

            # Create a merchantAuthenticationType object with authentication details
            # retrieved from the constants file
            merchantAuth = apicontractsv1.merchantAuthenticationType()
            merchantAuth.name = "login id"
            merchantAuth.transactionKey = "transaction key"

            # Create the payment data for a credit card
            creditCard = apicontractsv1.creditCardType()
            creditCard.cardNumber = data["card_number"]
            creditCard.expirationDate = data["expiry"]
            creditCard.cardCode = data["cvv"]

            # Add the payment data to a paymentType object
            payment = apicontractsv1.paymentType()
            payment.creditCard = creditCard

            # Set the customer's Bill To address
            customerAddress = apicontractsv1.customerAddressType()
            customerAddress.firstName = data["first_name"]
            customerAddress.lastName = data["last_name"]

            # Add values for transaction settings
            duplicateWindowSetting = apicontractsv1.settingType()
            duplicateWindowSetting.settingName = "duplicateWindow"
            duplicateWindowSetting.settingValue = "600"
            settings = apicontractsv1.ArrayOfSetting()

            settings.setting.append(duplicateWindowSetting)

            # Create a transactionRequestType object and add the previous objects to it.
            transactionrequest = apicontractsv1.transactionRequestType()
            transactionrequest.transactionType = "authCaptureTransaction"
            transactionrequest.amount = '12'
            transactionrequest.payment = payment
            transactionrequest.billTo = customerAddress
            transactionrequest.transactionSettings = settings

            # Assemble the complete transaction request
            createtransactionrequest = apicontractsv1.createTransactionRequest()
            createtransactionrequest.merchantAuthentication = merchantAuth
            createtransactionrequest.refId = "MerchantID-0001"
            createtransactionrequest.transactionRequest = transactionrequest
            # Create the controller
            createtransactioncontroller = createTransactionController(
                createtransactionrequest)
            createtransactioncontroller.execute()

            response = createtransactioncontroller.getresponse()

            output = {}

            if response is not None:
                # Check to see if the API request was successfully received and acted upon
                if response.messages.resultCode == "Ok":
                    # Since the API request was successful, look for a transaction response
                    # and parse it to display the results of authorizing the card
                    if hasattr(response.transactionResponse, 'messages') is True:

                        output = {"status": 200, "message": response.transactionResponse.
                              messages.message[0].description}
                    else:
                        if hasattr(response.transactionResponse, 'errors') is True:
                            output = {"status": 405, "message": response.transactionResponse.errors.error[0].errorText}
                        else:
                            output = {"status": 405, "message": response.messages.message[0]['text'].text}
                # Or, print errors if the API request wasn't successful
                else:
                    if hasattr(response.transactionResponse, 'errors') is True:
                        output = {"status": 406, "message": response.transactionResponse.errors.error[0].errorText}
                    else:
                        output = {"status": 406, "message": response.messages.message[0]['text'].text}
            else:
                output = {"status": 407, "message": "No Response from Server"}

            return output
        except Exception as e:
            # print(e)
            return {"status": 408, "message": "Unexpected error. Please contact the administrator"}