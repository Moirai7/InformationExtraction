f = open('zhangfu.an','rb')

while True:
	line = f.readline()
	if line:
		line=line.strip('\n')
		if line.find('high score')!=-1:
			l= line.split('\t')
			if len(l)<5:
				print '\n'+line
			else:
				print l[0]+'\t'+l[1]+'\t'+l[2]+'\t'+l[3]
		elif line.find('too small')!=-1:
			print line
	else:
		break
