#cat spo_qizi.haiming20 |python __init__.py 
last=""
while read query
	do	
		echo "$query"|awk -F'\t' '{print $1,$2,$3}'|while read name type answer
		do
		#if [ "$type"x = 'name' ]
		#then
		#	continue
		if [ "$type"x = "qizix" ]
		then
			echo `curl -XPOST nmg01-kgb-odin1.nmg01:8051/1 -d '{"method":"search","params" : [["'$name'","妻子"], 100, 40, 10]}'`|python Process.py $name $type $answer
		elif [ "$type"x = "zhangfux" ]
		then
			echo `curl -XPOST nmg01-kgb-odin1.nmg01:8051/1 -d '{"method":"search","params" : [["'$name'","丈夫"], 100, 40, 10]}'`|python Process.py $name $type $answer
		elif [ "$type"x = "nvyoux" ]
		then
			echo `curl -XPOST nmg01-kgb-odin1.nmg01:8051/1 -d '{"method":"search","params" : [["'$name'","女友"], 100, 40, 10]}'`|python Process.py $name $type $answer
		elif [ "$type"x = "nanyoux" ]
		then
			echo `curl -XPOST nmg01-kgb-odin1.nmg01:8051/1 -d '{"method":"search","params" : [["'$name'","男友"], 100, 40, 10]}'`|python Process.py $name $type $answer
		elif [ "$type"x = "fuqinx" ]
		then
			echo `curl -XPOST nmg01-kgb-odin1.nmg01:8051/1 -d '{"method":"search","params" : [["'$name'","父亲"], 100, 40, 10]}'`|python Process.py $name $type $answer
		elif [ "$type"x = "muqinx" ]
		then
			echo `curl -XPOST nmg01-kgb-odin1.nmg01:8051/1 -d '{"method":"search","params" : [["'$name'","母亲"], 100, 40, 10]}'`|python Process.py $name $type $answer
		elif [ "$type"x = "nverx" ]
		then
			echo `curl -XPOST nmg01-kgb-odin1.nmg01:8051/1 -d '{"method":"search","params" : [["'$name'","女儿"], 100, 40, 10]}'`|python Process.py $name $type $answer
		elif [ "$type"x = "erzix" ]
		then
			echo `curl -XPOST nmg01-kgb-odin1.nmg01:8051/1 -d '{"method":"search","params" : [["'$name'","儿子"], 100, 40, 10]}'`|python Process.py $name $type $answer
		fi
		done
	done
exit 0
#curl -XPOST nmg01-kgb-odin1.nmg01:8051/1 -d '{"method":"search","params" : [["王菲","女儿"], 100, 40, 10]}'
