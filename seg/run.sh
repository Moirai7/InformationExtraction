while read query
do
	echo "$query"|awk -F ' \t' '{print $1}'|while read result
	do
		echo "-N ["$result"] [0("$result")] [] -H 1000"
	done
done
