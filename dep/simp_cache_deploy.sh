#!/bin/bash
#°ïÖúÐÅÏ¢ 
help_info(){
    echo -e "-d,\tdeploy and install simp cache"
    echo -e "-s,\tstop simp cache"
    echo -e "-r,\trestart you sim cache"
    echo "example:"
    echo -e "\tsh simp_cache_deploy.sh -d "
}


CACHE_PORT=65288
function check_simp_port_and_path() {
echo -e "\n" | telnet localhost $CACHE_PORT 2>/dev/null | grep Connected &>/dev/null
if [ $? -eq 0 ]; then
		if [ -d "~/.install_simp_cache" ]; then
			echo "port $CACHE_PORT listened, installed path exist, simp cache have been installed"
			exit 1
		fi
else 
		echo "simp cache haven't been installed"
fi
}

function deploy_simp_cache() {

check_simp_port_and_path
stop_simp_cache
FILENAME="install_simp_cache.tar.gz"
echo "==============begin download envirment of simp cache============"
if [ -f "./$FILENAME" ];then
		rm $FILENAME;
fi
cd ~
wget nj02-rp-5yue-bu-recommend-personal063.nj02.baidu.com:/home/work/download/$FILENAME
echo "==============end download envirment of simp cache============"
tar zxvf $FILENAME
cd .install_simp_cache ;
sh start_simp_cache.sh;
sleep 1
./sofa detect 127.0.0.1:${CACHE_PORT}:8 &>/dev/null
if [ `echo $?` = "0" ]; then
		echo "================simp cache has already started===================="
		cd ..
		rm $FILENAME
		exit 1
fi

}

function restart_simp_cache() {
	pid=`netstat -nlp | grep $CACHE_PORT | awk '{print $7}' | awk -F'[/]' '{ print $1}'`
	#echo -e "pid\t$pid"	
  	supervise_id=`ps -ef | grep $pid | grep -v grep | awk '{print $3}'`
	#echo -e "supervise_id\t$supervise_id"	
	supervise=`ps -ef | grep $supervise_id | grep supervise | grep cache`
	if [ "$supervise" != "" ]; then
		kill -9 $pid
		echo "kill pid $pid"
	else
		echo "supervise not exist, installed "
		deploy_simp_cache
	fi

	
}


function stop_simp_cache() {
	pid=`netstat -nlp | grep $CACHE_PORT | awk '{print $7}' | awk -F'[/]' '{ print $1}'`
	#echo -e "pid\t$pid"	
  	supervise_id=`ps -ef | grep $pid | grep -v grep | awk '{print $3}'`
	#echo -e "supervise_id\t$supervise_id"	
	supervise=`ps -ef | grep $supervise_id | grep supervise | grep cache`
	if [ "$supervise" != "" ]; then
		kill -9 $supervise_id $pid
		echo "kill supervise $supervise_id"
		echo "kill simp_cache $pid"
	else
		kill -9 $pid
		echo "kill simp_cache $pid"

	fi

	
}




function nomal_opts_act()
{
    echo -e "\n### nomal_opts_act ###\n"

    while [ -n "$1" ]
    do
    case "$1" in 
        -d)
            echo "Found the -d option, now we deploy "
            deploy_simp_cache
			;;
    	-s)
            echo "Found the -s option, now we stop"
           	stop_simp_cache 
			;;
	
		-r)
            echo "Found the -r option, now we restart"
			restart_simp_cache			
			shift
            ;;
        *)
             echo "$1 is not an option"
            ;;
    esac
    shift
    done
}

echo $#
if [ $# -eq 0 ]
then
    help_info
else 
	nomal_opts_act $*
fi



