import sys

for line in sys.stdin: 
	line = line.strip('\r\n').strip('\n').split('\t')
	print line[0]+'\t'+sys.argv[1]+'\t'+line[1]
