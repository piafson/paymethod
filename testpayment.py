#!/usr/bin/python3

import payment
import sys
import hashlib
import requests

import billmgr.logger as logging

MODULE = 'payment'
logging.init_logging('testpayment')
logger = logging.get_logger('testpayment')


class TestPaymentCgi(payment.PaymentCgi):
    def Process(self):
        # необходимые данные достаем из self.payment_params, self.paymethod_params, self.user_params
        # здесь для примера выводим параметры метода оплаты (self.paymethod_params) и платежа (self.payment_params) в лог
        logger.info(f"paymethod_params = {self.paymethod_params}")
        logger.info(f"payment_params = {self.payment_params}")

        # переводим платеж в статус оплачивается
        payment.set_in_pay(self.elid, '', 'external_' + self.elid)


# url для перенаправления c cgi
# здесь, в тестовом примере сразу перенаправляем на страницу BILLmanager
# должны перенаправлять на страницу платежной системы
# redirect_url = self.pending_page;
url = "https://securepay.tinkoff.ru/v2/Init"
paymethodamount = 100 * float(self.payment_params["paymethodamount"]) # сумма платежа в копейках
# subaccount = self.payment_params["subaccount"] # код л/с клиента

# тестовые данные платежа
data = {
    "TerminalKey": "TinkoffBankTest",
    "Amount": paymethodamount,
    "OrderId": "210900"
}

# получаем токен
t = []

for key, value in data.items():
    t.append({key: value})
t = sorted(t, key=lambda x: list(x.keys())[0])
t = "".join(str(value) for item in t for value in item.values())
sha256 = hashlib.sha256()
sha256.update(t.encode('utf-8'))
t = sha256.hexdigest()
data["Token"] = t  # добавляем токен к данным платежа

response = requests.post(url, json=data)
if response.json().get('PaymentURL'):
    redirect_url = response.json().get('PaymentURL')
else:
    redirect_url = self.fail_page # страница неудачной оплаты

# формируем html и отправляем в stdout
# таким образом переходим на redirect_url
payment_form = "<html>\n";
payment_form += "<head><meta http-equiv='Content-Type' content='text/html; charset=UTF-8'>\n"
payment_form += "<link rel='shortcut icon' href='billmgr.ico' type='image/x-icon' />"
payment_form += "       <script language='JavaScript'>\n"
payment_form += "               function DoSubmit() {\n"
payment_form += "                       window.location.assign('" + redirect_url + "');\n"
payment_form += "               }\n"
payment_form += "       </script>\n"
payment_form += "</head>\n"
payment_form += "<body onload='DoSubmit()'>\n"
payment_form += "</body>\n"
payment_form += "</html>\n";

sys.stdout.write(payment_form)

TestPaymentCgi().Process()

