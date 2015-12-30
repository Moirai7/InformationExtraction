#coding:utf-8
a=0
b=0
c=0
d=0
import sys
for line in sys.stdin:
	line = line.strip('\r\n').strip('\n') 
	if line:
		if line.find('test info : ')==-1:
			continue
		if len(sys.argv)==3:
			if d>=int(sys.argv[2]):
				break
		line=line.strip().split(' ')
		yc = line[5]
		fr = line[7]
		an = line[4]
		if yc ==sys.argv[1] and fr.find(an)!=-1:
			a+=1
		elif yc ==sys.argv[1] and fr.find(an)==-1:
			#print ' '.join(line)
			b+=1
		elif yc=='emma' and fr.find(an)!=-1:
			#print ' '.join(line)
			c+=1
		d+=1
	else:
		break

print a
print b
print c
print d-a-b-c
print d
print (a*1.0)/(a+c)
print (a*1.0)/(a+b)
