import os
import re

from ..crypto_pay_api_sdk import cryptopay
Crypto = cryptopay.Crypto(token=os.getenv("CRYPTO_TOKEN"), testnet=False)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_int_num(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def getPayUrl(text):
    pattern = r"'pay_url': '(.*?)'"
    pay_url_match = re.search(pattern, str(text))

    if pay_url_match:
        pay_url = pay_url_match.group(1)
        return pay_url
    
def getInv(text):
    pattern = r"'invoice_id': (\d+)"
    invoice_id_match = re.search(pattern, text)

    if invoice_id_match:
        invoice_id = invoice_id_match.group(1)
        return invoice_id


def checkInvoice(invoice):
    invoices = Crypto.getInvoices()
    invoice_ids = re.findall(r"'invoice_id': (\d+)", str(invoices))
    statuses = re.findall(r"'status': '(.*?)'", str(invoices))
    amounts = re.findall(r"'amount': '(.*?)'", str(invoices))

    for invoice_id, status, amount in zip(invoice_ids, statuses, amounts):
        if invoice_id==invoice:
            if status == "paid":
                return ["True",amount]
            else:
                return ["False"]