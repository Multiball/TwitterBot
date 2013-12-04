import ssl
import socket
import twitterutils

buffer_size = 1024

twitter_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
twitter_socket = ssl.wrap_socket(twitter_socket)
twitter_socket.connect(("api.twitter.com", 443)) #80 is default HTTP port; 443 is default HTTPS port

#request = twitterutils.generate_verify_credentials_request()
#request = twitterutils.generate_update_request("Maybe he'll finally find his keys")

request = twitterutils.request("POST","/1.1/statuses/update","Test tweet.")

#header
"""
request =   "POST /1/statuses/update.json HTTP/1.1\r\n" 
request +=	"Accept: */*\r\n"
request +=	"Connection: close\r\n"
request +=	"User-Agent: OAuth gem v0.4.4\r\n"
request +=	"Content-Type: applicaton/x-www-form-urlencoded\r\n"
request +=	"Authorization: OAuth oauth_consumer_key=\"Z3nHeXhrmLPKyaL7iYpbw\", oauth_nonce=\"e511866355c3887d475690b14558492c\", oauth_signature=\"4miMIxyh8ZsGH%2FkIqWDevQXhenU%3D\", oauth_signature_method=\"HMAC-SHA1\", oauth_timestamp=\"1360559092\", oauth_token=\"371952177-uHFwanOtiCTs5AGosoaXxg9n3wSOZNO2zZTv5TwN\", oauth_version=\"1.0\"\r\n"
request +=	"Content-Length: 68\r\n"
request +=	"Host: api.twitter.com\r\n\r\n"
#body
request +=	"status=Maybe%20he%27ll%20finally%20find%20his%20keys.%20%23peterfalk\r\n\r\n"
"""

print "sending request:"
print "***********"
print request
print "***********"

twitter_socket.send(request)
response = twitter_socket.recv(buffer_size)
while response:
	print response
	response = twitter_socket.recv(buffer_size)
	
