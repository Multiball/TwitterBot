"""
This code automates sending tweets to Twitter.
It may be helpful to follow the Twitter documentation: https://dev.twitter.com/docs
Especially "Authorizing a Request:" https://dev.twitter.com/docs/auth/authorizing-request
"""

import base64
from hashlib import sha1
import hmac
import random
import string
import socket
import time
from numpy import load
from urllib import quote, quote_plus

#Read secure information from a config file. Output errors if something's wrong.
secure_args = {}
try:
	config_file = open("twitbot.config")
	for line in config_file:
		line = line.strip().split(" ")
		secure_args[line[0]] = line[1]
	consumer_secret = secure_args["consumer_secret"]
	consumer_key = secure_args["consumer_key"]
	access_token_secret = secure_args["access_token_secret"]
	access_token = secure_args["access_token"]
except IOError:
	print ("The configuration file \"twitbot.config\" could not be found or could"
	+ " not be read. Please ensure that there are no missing lines and that the "
	+ "file starts on the first line. Refer to the README for more information.")
	quit()
except NameError:
	print ("You're missing some information from the configuration file" + 
			" \"twitbot.config\", or the it is not properly formatted. " +
			". Please make sure you have values for " +
			"\"consumer_secret\", \"consumer_key\", \"access_token_secret\"," +
			" and \"access_token\", and that these names are all spelled " +
			" exactly as they are here. These values should be obtained from " +
			"the twitter account being used. Refer to the README for more " + 
			"information.")



# this funciton generates a random 42-character alphanumeric string.
def generate_oauth_nonce():
	nonce = ""
	for i in range(1,42):
		letter_or_number = random.randint(0,1)
		if letter_or_number:
			number_index = random.randint(0,9)
			nonce += string.digits[number_index]
		else:
			letter_index = random.randint(0,51)
			nonce += string.ascii_letters[letter_index]
	return nonce

# this function generates signatures as per the procedure
# desribed here: https://dev.twitter.com/docs/auth/creating-signature
#
# arguments is a dictionary of arguments that we want to encode.
# in this case, it should be the arguments we want to include in
# our HTTP header.
def generate_oauth_signature(arguments):
	#print "Generating signature with ", arguments, "..."
	sig_param_string = ""
	for name, value in sorted(arguments.iteritems()):
		sig_param_string += quote(name) + "=" + quote(value) + "&"
	# The header for all our Http request will always be 
	# POST 1.1/statuses/update.json
	# or
	# GET 1.1/account/verify_credentials.json
	# with api.twitter.com as the host. We start with that, percent-encoded.
	sig_param_string = sig_param_string[0:len(sig_param_string)-1] # remove trailing '&'
	print "param string|", sig_param_string
	if "status" in arguments.keys():
		sig_base_string = "POST&https%3A%2F%2Fapi.twitter.com%2F1.1%2Fstatuses%2Fupdate.json&"
	else:
		sig_base_string = "GET&https%3A%2F%2Fapi.twitter.com%2F1.1%2Faccount%2Fverify_credentials.json&"
	#	sig_base_string = "GET&https%3A%2F%2Fapi.twitter.com%2F1.1%2Faccount%2Fverify_credentials.json%3Finclude_identities%3Dtrue&"
	sig_base_string += quote(sig_param_string)
	print "base string|", sig_base_string
	# The signing key is the consumer secret "&" access token secret.
	# We use those provided us by Twitter for our particular application.
	signing_key = consumer_secret + "&" + access_token_secret 
	#note: below is provided example by Twitter
	#signing_key = "kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw&LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE"
	encoder = hmac.new(key=signing_key, digestmod=sha1)
	encoder.update(sig_base_string)
	return base64.b64encode(encoder.digest())

# this is the meaty function that assembles the oauth values required
# for the HTTP header so that we may succesfully tweet things.
#
# header_arguments is a dictionary with all entries having keys corresponding 
# to the 
def generate_oauth_arguments(header_arguments):

	
	# this number is app-specific and provided by Twitter. 
	#TODO: put this in a config file or something
	header_arguments["oauth_consumer_key"] = consumer_key
	#random alphanumeric sequence to be produced however
	header_arguments["oauth_nonce"] = generate_oauth_nonce()
	# Twitter specifies HMAC-SHA1
	header_arguments["oauth_signature_method"] = "HMAC-SHA1" 
	# timestamp in seconds since Unix epoch
	header_arguments["oauth_timestamp"] = str(int(time.time()))
	# Because this app is intended for dedicated use with one channel,
	# We use the token provided by Twitter.
	# https://dev.twitter.com/docs/auth/obtaining-access-tokens
	header_arguments["oauth_token"] = access_token 
	# Twitter tells us to use 1.0
	header_arguments["oauth_version"] = "1.0"
	# generating a signature is a process detailed by Twitter: 
	# https://dev.twitter.com/docs/auth/creating-signature
	signature = generate_oauth_signature(header_arguments)
	header_arguments["oauth_signature"] = signature
	

	# DEBUG: used to copy-paste information known to be correct because
	# it was generated by Twitter.
	"""
	header_arguments["include_entities"] = "true"
#	header_arguments["status"] = "auto-generated tweet"
	# this number is app-specific and provided by Twitter. TODO: put this in a config file
	header_arguments["oauth_consumer_key"] = "Z3nHeXhrmLPKyaL7iYpbw" 
	#random alphanumeric sequence to be produced however
	header_arguments["oauth_nonce"] = "408424514afe5c8d5ac017da9eb0f608"
	# Twitter specifies HMAC-SHA1
	header_arguments["oauth_signature_method"] = "HMAC-SHA1" 
	# timestamp in seconds since Unix epoch
	header_arguments["oauth_timestamp"] = "1342208259"
	# I don't entirely understand how this works. There might be
	# two kinds of access token? Right now, I'm using the one generated by
	# Twitter for this app, but there are other ways of getting one:
	# https://dev.twitter.com/docs/auth/obtaining-access-tokens
	header_arguments["oauth_token"] = "371952177-uHFwanOtiCTs5AGosoaXxg9n3wSOZNO2zZTv5TwN" 
	# Twitter tells us to use 1.0
	header_arguments["oauth_version"] = "1.0"
	# generating a signature is a process detailed by Twitter: 
	# https://dev.twitter.com/docs/auth/creating-signature
	signature = generate_oauth_signature(header_arguments)
	header_arguments["oauth_signature"] = signature	
	"""

	
	if "status" in header_arguments.keys():
		del header_arguments["status"]
	#	del header_arguments["include_entities"]
	returner = ""
	for name, value in sorted(header_arguments.iteritems()):
		returner += name + "=\"" + quote_plus(value) + "\", "
	returner = returner[0:len(returner)-2] # remove trailing ", "
	return returner

# main control function, that assembles the header and sends it to Twitter
def generate_update_request(status):

	if len(status) > 140:
		return "status request too long (length "+ str(len(status)) +"); not sent"
	status_string = quote(status)

	arguments = {"status":status_string}

	#header
	request =   "POST /1.1/statuses/update.json HTTP/1.1\r\n"
	request +=	"Accept: */*\r\n"
	request +=	"Connection: close\r\n"
	request +=	"User-Agent: OAuth gem v0.4.4\r\n"
	request +=	"Content-Type: applicaton/x-www-form-urlencoded\r\n"
	request +=	"Authorization: OAuth " + generate_oauth_arguments(arguments) + "\r\n"
	request +=	"Content-Length: " + str(len(("status="+status_string)) ) + "\r\n"
	request +=	"Host: api.twitter.com\r\n\r\n"
	#body
	request += "status=" + status_string + "\r\n\r\n"

	return request

def generate_verify_credentials_request():

	arguments = {"include_entities":"true"}
	request_target = "GET /1.1/account/verify_credentials.json"
	if len(arguments) > 0:
		request_target += "?"
		print arguments
		for k,v in arguments.iteritems():
			request_target += k + "=" + v + "&"
		#remove trailing '&'
		request_target = request_target[0:len(request_target)-1] 

	#header
	request =   request_target + " HTTP/1.1\r\n"
	request +=	"Accept: */*\r\n"
	request +=	"Connection: close\r\n"
	request +=	"User-Agent: OAuth gem v0.4.4\r\n"
	request +=	"Content-Type: applicaton/x-www-form-urlencoded\r\n"
	request +=	"Authorization: OAuth " + generate_oauth_arguments(arguments) + "\r\n"
	request +=	"Content-Length: 0" + "\r\n"
	request +=	"Host: api.twitter.com\r\n"
	request += "\r\n"
	#body
	
	request += "\r\n" #"include_entities=true" + "\r\n"
	request += "\r\n"

	return request
