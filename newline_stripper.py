bookname = "david_copperfield"

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

