import sys

paired_delimiters = ["\""]
endpoint_delimiters = [".", "?", "!", "--"]
midpoint_delimiters = [",", ";", ":"]
open_expression = "",False

def scan_sentance_end(line, index):
	# this assumes endpoint delimiters of only one character
	while index < 140 and index > 0 and line[index] in endpoint_delimiters:
		index += 1
	
	return index

def find_latest(expression_set, line, index):
	index = scan_sentance_end(line, index)
	for expression in expression_set:
		test_index = index
		while test_index < 140 and test_index > 0:
			index = test_index
#			print str(index) + "[" + line[index+1] + "] finding next..."
			test_index = scan_sentance_end(line, line.find(expression, index+len(expression)))
	return index

def find_break_index(line):

	global open_expression
	index = -1
	
	for expression in paired_delimiters:
		index = line.find(expression)
		if index == 0: 
			# expression starts with paired delimiter;
			# return breakpoint just after its mate
			index = line.find(expression, len(expression))
			if index > 0 and index < (140-len(expression)):
				return index + len(expression)
			else:
				open_expression = (expression, True)
		elif index > 0 and index < 140:
			if open_expression[1] == False:
			# expression includes paired delimiter not in front;
			# stop right before it.
				return index
			elif open_expression[0] == expression:
			# the end of our previously open expression.
				open_expression = ("",False)
				return index + len(expression)
		
	for expression in endpoint_delimiters:
		index = line.find(expression)
		if index > 0 and index < 140:
			# adjust to put mark inside
			if expression == "--":
				return index + 2
			else:
				return scan_sentance_end(line, index)

	for expression in midpoint_delimiters:
		# these should break /after/ the instance of the expression
		index = line.find(expression)
		if index > 0 and index < 140:
			index = find_latest(midpoint_delimiters, line, index) + len(expression)
			return index

	# no good place to break: find nearest word and break there.
	index = 140
	while index > 0:
		if line[index] == ' ':
			return index
		else:
			index -= 1

	# 140 characters and no space. What author would do this?
	# return maximum possible characters, 140
	return 140


def newline_stripper(bookname):
	book = open(bookname + ".txt")
	contents = book.readlines()
	new_contents = ""

	for line in contents:
		if len(line) <= 0:
			new_comments += "\n"
			continue
		if line == "\n" or line == "\r" or line == "\r\n":
			new_contents += "\n"
			continue
		if line.endswith("\r\n"):
			new_contents += line[0:len(line)-2] + " "
		elif line.endswith("\n") or line.endswith("\r") :
			new_contents += line[0:len(line)-1] + " "

	#ensure end of file
	new_contents += "\n"

	new_book = open(bookname + "_stripped.txt", "w")
	new_book.write(new_contents)		

def parse_project_gutenburg_book(filename):
	global open_expression

	# Project Gutenburg books are all parsed into lines of something 
	# like 80 characters. We need to eliminate the extra newlines
	# to parse properly.
	newline_stripper(filename)

	book = open(filename + "_stripped.txt", "r")
	returner = []
	for line in book:
		if len(line) == 0 or line.isspace():
			continue
		line = line.strip()
		while len(line) > 140:
			break_index = find_break_index(line)
			returner.append(line[0:break_index].strip(" \n\r"))
			#print "|" + line[0:break_index].strip(" \n\r") + "|"
			line = line[break_index:len(line)].strip(" \n\r")
		#line less than 140 characters
		for expression in paired_delimiters:
			index = line.find(expression)
			if index > 0:
				if open_expression[1] == True and open_expression[0] == expression:
					open_expression = ("",False)

		returner.append(line.strip(" \n\r"))
		#print "|" + line + "|"

	newname = filename + "_parsed.txt"
	result = open(newname, "w")
	for line in returner:
		result.write(line + "\n")


