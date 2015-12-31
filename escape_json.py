import sys
# SO MANY HACKS!!!
print (
	'\'"' + # escaped single quote quotes the entire descriptor as an argument to avr-gcc. double quote is for the c string literal
	open(sys.argv[1], "r").read()
	.replace('\n', ' ') # get rid of newlines
	.replace('\\', r'\\') # escape backslashes
	.replace('"', r'\"') # escape double quotes
	.replace("'", r"'\''") + # escaping single quotes is not possible. instead we close the bash string, append an escaped ' character, and reopen the string. Someone please fix this
	'"\''
	)