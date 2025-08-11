import json
import hashlib
import requests
import base64
import OpenSSL
from OpenSSL import crypto
from django.conf import settings
from conf.utils import log_debug, log_error


class BlinkPay:
    username = None
    password = None
    url = None

    def __init__(self):
        self.credentials()
        self.url = settings.BLINKURL

    def credentials(self):
        self.username = settings.BLINKUSERNAME
        self.password = settings.BLINKPASSWORD

    def depositmobilemoney(self, params):
        ''' This API is used to deposit mobile money into your account/wallet. '''
        req = None
        msisdn = params.get('msisdn')
        amount = params.get('amount')
        narrative = params.get('narrative')
        reference = params.get('reference')

        payload = {
            "username": self.username,
            "password": self.password,
            "api": "depositmobilemoney",
            "msisdn": "%s" % msisdn,
            "amount": int(float(amount)),
            "narrative": narrative,
            "reference": reference,
        }

        res = self.make_request(payload)

        if not res:
            return {
                "status": "FAILED",
                "message": "System Failure. Contact Admin"
            }

        reference_code = None

        error = res.get('error')
        if error:
            status = 'FAILED'
            message = res['message']
            reference_code = None
        else:
            status = res.get('status')
            reference_code = res.get('reference_code')
            message = res.get('message') if res.get('message') else res.get('bundles')

        response = {"error": error, "status": status, "message": message, "reference_code": reference_code}

        return response

    def withdrawmobilemoney(self, params):
        '''This API is used to withdraw mobile money from your account.'''
        msisdn = params.get('msisdn')
        amount = params.get('amount')
        narrative = params.get('narrative')
        reference = params.get('reference')

        payload = {
            "username": self.username,
            "password": self.password,
            "api": "withdrawmobilemoney",
            "msisdn": "%s" % msisdn,
            "amount": amount,
            "narrative": narrative,
            "reference": reference,
        }
        res = self.make_request(payload)

        if not res:
            return {
                "status": "FAILED",
                "message": "System Failure. Contact Admin"
            }

        error = res.get('error')
        if error:
            status = 'FAILED'
            message = res['message']
            reference_code = None
        else:
            status = res.get('status')
            reference_code = res.get('reference_code')
            message = res.get('message') if res.get('message') else res.get('bundles')

        response = {"error": error, "status": status, "message": message, "reference_code": reference_code}

        return response

    def buyairtime(self, params):
        '''This API is used to Buy airtime from your account.'''
        msisdn = params.get('msisdn')
        amount = params.get('amount')
        narrative = params.get('narrative')
        reference = params.get('reference')

        payload = {
            "username": self.username,
            "password": self.password,
            "api": "buyairtime",
            "amount": amount,
            "msisdn": "%s" % msisdn,
            "narrative": narrative,
            "reference": reference,
        }
        res = self.make_request(payload)

        error = res.get('error')
        if error:
            status = 'FAILED'
            message = res['message']
            reference_code = None
        else:
            status = res.get('status')
            reference_code = res.get('reference_code')
            message = res.get('message') if res.get('message') else res.get('bundles')

        response = {"error": error, "status": status, "message": message, "reference_code": reference_code}

        if not response:
            return {
                "status": "FAILED",
                "message": "System Failure. Contact Admin"
            }
        return response

    def getbundle(self, params):

        msisdn = params.get('msisdn')

        payload = {
            "username": self.username,
            "password": self.password,
            "api": "getdatabundles",
            "msisdn": "%s" % msisdn,
        }
        request = self.make_request(payload)

        if not request:
            return {
                "status": "FAILED",
                "message": "System Failure. Contact Admin"
            }
        return request

    def buy_bundle(self, params):
        '''This API is used to Buy airtime from your account.'''
        msisdn = params.get('msisdn')
        narrative = params.get('narrative')
        reference = params.get('reference')
        id = params.get('id')
        reference_code = None

        payload = {
            "username": self.username,
            "password": self.password,
            "api": "buydatabundle",
            "msisdn": "%s" % msisdn,
            "id": id,
            "narrative": narrative,
            "reference": reference,
        }
        res = self.make_request(payload)

        error = res.get('error')
        if error:
            status = 'FAILED'
            message = res['message']
        else:
            status = res.get('status')
            reference_code = res.get('reference_code')
            message = res.get('message') if res.get('message') else res.get('bundles')

        response = {"error": error, "status": status, "message": message, "reference_code": reference_code}

        if not response:
            return {
                "status": "FAILED",
                "message": "System Failure. Contact Admin"
            }
        return response

    def check_status(self, reference_code):
        payload = {
            "username": self.username,
            "password": self.password,
            "api": "checktransactionstatus",
            "reference_code": reference_code
        }
        request = self.make_request(payload)

        if not request:
            return {
                "status": "FAILED",
                "message": "System Failure. Contact Admin"
            }
        return request  # {'status': u'SUCCESSFUL', 'message': None, 'reference_code': reference_code} #request

    def check_balance(self, msisdn, _type):
        payload = {
            "username": self.username,
            "password": self.password,
            "api": "checkmsisdnnetworkbalance",
            "msisdn": "%s" % msisdn,
            "type": _type
        }
        if _type == "URA" or _type == 'BILL PAYMENTS':
            return self.check_bill_balance()
        request = self.make_request(payload)

        if not request:
            return {
                "status": "FAILED",
                "message": "System Failure. Contact Admin"
            }
        return request

    def check_network(self, msisdn, service):
        payload = {
            "username": self.username,
            "password": self.password,
            "api": "checknetworkstatus",
            "msisdn": "%s" % msisdn,
            "service": service
        }
        request = self.make_request(payload)

        if not request:
            return {
                "status": "FAILED",
                "message": "System Failure. Contact Admin"
            }
        return request

    def bill_payment(self, params):
        payment_item_id = params.get('payment_item_id')
        status_notification_url = ''
        validation_id = params.get('validation_id')
        nonce = ''
        account_number = params.get('account_number')
        amount = params.get('amount')
        phone_number = params.get('phone_number')
        reference = params.get('reference')

        credentials = "%s:%s" % (self.username, self.password)
        base64_encoded_auth = base64.b64encode(credentials)
        key_file = open(settings.OPENSSLFILE, "r")
        key = key_file.read()
        key_file.close()
        if key.startswith('-----BEGIN '):
            # pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, key, password)
            pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, key)
        else:
            pkey = crypto.load_pkcs12(key, self.password).get_privatekey()

        payload = {
            "api": "makepayment",
            "nonce": str(reference),
            "amount": int(float(amount)),
            "account_number": str(account_number),
            "phone_number": phone_number,
            "payment_item_id": payment_item_id,
            "deliver_exact_amount": True,
            "status_notification_url": "",
            "validation_id": str(validation_id)
        }

        json_payload = json.dumps(payload)
        signature = OpenSSL.crypto.sign(pkey, hashlib.sha1(json_payload).hexdigest(), "sha1")
        base64_encoded_signature = base64.b64encode(signature)
        header = {"Content-Type": "application/json", "Authorization": "Basic %s" % base64_encoded_auth,
                  "Signature": base64_encoded_signature}
        r = requests.post(self.url, data=json_payload, headers=header, verify=False)
        print('Billing Response %s ' % r.text)
        print('Billing Response %s ' % payload)
        return json.loads(r.text)

    def check_bill_balance(self):
        credentials = "%s:%s" % (self.username, self.password)
        base64_encoded_auth = base64.b64encode(credentials)
        key_file = open(settings.OPENSSLFILE, "r")
        key = key_file.read()
        key_file.close()
        if key.startswith('-----BEGIN '):
            # pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, key, password)
            pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, key)
        else:
            pkey = crypto.load_pkcs12(key, self.password).get_privatekey()

        payload = {
            "api": "checkpaymentsbalance"
        }

        json_payload = json.dumps(payload)
        signature = OpenSSL.crypto.sign(pkey, hashlib.sha1(json_payload).hexdigest(), "sha1")
        base64_encoded_signature = base64.b64encode(signature)
        header = {"Content-Type": "application/json", "Authorization": "Basic %s" % base64_encoded_auth,
                  "Signature": base64_encoded_signature}
        r = requests.post(self.url, data=json_payload, headers=header, verify=False)
        return json.loads(r.text)

    def get_payment_menu(self):
        credentials = "%s:%s" % (self.username, self.password)
        base64_encoded_auth = base64.b64encode(credentials)
        key_file = open(settings.OPENSSLFILE, "r")
        key = key_file.read()
        key_file.close()
        if key.startswith('-----BEGIN '):
            # pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, key, password)
            pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, key)
        else:
            pkey = crypto.load_pkcs12(key, self.password).get_privatekey()

        payload = {
            "api": "getpaymentsmenu"
        }

        json_payload = json.dumps(payload)
        signature = OpenSSL.crypto.sign(pkey, hashlib.sha1(json_payload).hexdigest(), "sha1")
        base64_encoded_signature = base64.b64encode(signature)
        header = {"Content-Type": "application/json", "Authorization": "Basic %s" % base64_encoded_auth,
                  "Signature": base64_encoded_signature}
        r = requests.post(self.url, data=json_payload, headers=header, verify=False)
        return json.loads(r.text)

    def make_request(self, payload):
        reference_code = None
        try:
            status = "SUCCESSFUL"
            message = None
            header = {"Content-Type": "json"}
            log_debug(payload)

            r = requests.post(self.url, json=payload, verify=False)
            log_debug("Blink Response: %s" % r.text)

            res = r.json()

            result = res  # {"error": error, "status": status, "message": message, "reference_code": reference_code}
            return result
        except Exception as e:
            result = {"status": "INDETERMINATE", "message": "System Error during MM %s Request." % e,
                      "reference_code": None, "error": True}
            log_debug(e)
            return result
