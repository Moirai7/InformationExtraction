#coding:'utf-8'
#f = open('ooresqi','rb')
strs=''
import sys
for line in sys.stdin:
	if line:
		line=line.strip('\n')
		if line.find('high score result( ')!=-1:
		#if line.find('high score result(')!=-1 :
			l= line.split('\t')
			#print '\n'+l[0]+'\t'+l[1]+'\t'+l[2]+''+l[3],
			if len(l)<5:
				print '\n'+line
			else:
				if strs == l[0].split(' : ')[1] and float(l[3])>20.0:
					print l[2]+' '+l[3],
				if float(l[3])>49.0 :
					if strs!=l[0].split(' : ')[1]:
						strs = l[0].split(' : ')[1]
						print '\n'+strs+'\t'+sys.argv[1]+'\t'+l[2]+' '+l[3],
				#	else:
				#		print l[2]+' '+l[3],
				#print line
		#elif line.find('too small')!=-1:
		#	print line
	else:
		break
