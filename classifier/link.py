
f1 = open('alloo','rb')
strs=[]

line=f1.readline()
while line:
	line=line.strip()
	if line.find('test info :')!=-1:
		h=line.split(' : ')[1].split(' ')[3]
		strs.append(h)
	line=f1.readline()


f2 = open('newoomuqin','rb')
strs2=[]

line=f2.readline()
while line:
        line=line.strip()
        if line.find('test info :')!=-1:
                h=line.split(' : ')[1].split(' ')[3]
                strs2.append(h)
        line=f2.readline()

strs= list(set(strs).difference(set(strs2))) 
for s in strs:
	print s
