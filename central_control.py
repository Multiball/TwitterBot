import book_parser
import twitterutils
import time
import socket
import ssl

buffer_size = 1024
wait_interval = 1 # sixty thousand milliseconds == one minute

twitter_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
twitter_socket = ssl.wrap_socket(twitter_socket)
twitter_socket.connect(("api.twitter.com", 443)) #80 is default HTTP port; 443 is default HTTPS port

book_list =open("book_queue.txt")

for book_name in book_list:
	book_name = book_name.strip()
	book_parser.parse_project_gutenburg_book(book_name)
	current_book = open(book_name + "_parsed.txt", "r")
	for line in current_book:
#		request = twitterutils.generate_update_request(line)
#		twitter_socket.send(request)
		print line
		time.sleep(wait_interval)

