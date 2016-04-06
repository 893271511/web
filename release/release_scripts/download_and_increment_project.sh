#!/bin/sh
#$1 project_name
#$2 env
#$3 要调用函数的名称
#脚本使用例：sh download_and_deploy_project.sh renren-licai porduction {download increment_deploy} [IP]
echo $1
echo $2
echo $3
echo $4
export PATH="/usr/kerberos/bin:$PATH"
export KRB5CCNAME=/tmp/krb5cc_pub_$$
trap kdestroy 0 1 2 3 5 15
kinit -k -t /etc/krb5.keytab

#环境变量
export LANG="en_US.UTF-8"
export LC_ALL="en_US.utf8"
export LC_LANG="en_US.utf8"

script_path="`pwd`"
logs_dir="${script_path}/logs"
test ! -d ${logs_dir} && mkdir ${logs_dir}
log_file="${logs_dir}/${script_name}.log"
project_bak="/data/project_bak"
timestamp=`date +%Y-%m-%d-%H-%M-%S`
script_path="`pwd`"
conf_dir="${script_path}/conf"
script_name="`basename $0`"
proj_name=$1
env=$2
cmd=$3
deploy_ip=$4
nginx_conf="/data/web/nginx/conf/nginx.conf"
ver_log="${logs_dir}/${proj_name}.version.log"

echo "start time:`date`" |tee -a ${log_file}

if [ `ps -ef |grep -v grep |grep "\`basename $0\` ${proj_name}" |wc -l` -gt 3 ];then
	echo "${proj_name} running, Please try again later!"
	exit 1
fi

if echo ${proj_name} |grep "renren-fenqi-ams" &>/dev/null;then
	echo "renren-fenqi-ams not release increment" >> ${log_file}
	exit 1
else
	if [ -e "${conf_dir}/${proj_name}.config" ];then
		. ${conf_dir}/${proj_name}.config
	else
		echo "config file not exist"
		exit 1
	fi
fi

test -z "$proj_name" && echo "variable proj_name is not null" && exit 1
test -z "$target" && echo "variable target is not null" && exit 1
test -z "$hosts" && echo "variable hosts is not null" && exit 1
test -z "$cmd" && echo "variable cmd is not null" && exit 1

staging_IP="10.4.37.233"

download()
{
        echo "开始尝试停止${staging_IP}:${port}"
        ssh ${staging_IP} "sh ${stop_cmd}"
        sleep 5
        if ssh ${staging_IP} "netstat -antlp |grep LIST |grep :${port}";then
            TCP=`ssh ${staging_IP} "netstat -antlp |grep LIST |grep :${port}"`
            PID=`echo $TCP |awk '{print $7}' |awk -F/ '{print $1}'`
            ssh ${staging_IP} "/bin/kill -9 $PID"
            sleep 1
            if ssh ${staging_IP} "netstat -antlp |grep LIST |grep :${port}";then
                        echo "${staging_IP} resin stop error" |tee -a ${log_file}
                        exit 1
            fi
            echo "${host} resin stop suceed" |tee -a ${log_file}
        else
            echo "${host} resin stop suceed" |tee -a ${log_file}
        fi

        echo "start copy ${hosts}:${target}/${proj_name} to ${staging_IP}:${target}/${proj_name}"
        if ssh ${staging_IP} "rm -rf ${target}/${proj_name};test  ! -d ${target}/${proj_name}";then
                echo "删除${target}/${proj_name}成功"
                echo "下载代码开始-----------------------------------------------------"
                scp -r ${hosts}:${target}/${proj_name} ${staging_IP}:${target}/${proj_name}
                if [ $? -eq 0 ];then
                        echo "copy ${hosts}:${target}/${proj_name} to ${staging_IP}:${target}/${proj_name} suceeed"
                else
                        echo "copy ${hosts}:${target}/${proj_name} to ${staging_IP}:${target}/${proj_name} error"
                        exit 1
                fi
        else
                echo "ssh cmd error"
                exit 1
        fi
        echo "-----------------------------------------------------"
}

deploy()
{
echo "#####deploy"
echo "同步包到各服务器"
count=${#hosts[@]}
i=0
for host in ${hosts[@]}; do
        i=$(($i+1))
        echo "共${count}台，第${i}台:${host}"
        if [ ${proj_name} != "renren-fenqi-ams" ];then 
                ssh $host "test ! -e ${project_bak} && mkdir -pv ${project_bak}; rm -rf ${project_bak}/${proj_name}.increment"
                test $? -ne 0 && echo "ssh error" && exit 1
		echo "检查项目配置"
		if [ ${proj_name} == "renren-licai-credit-manager" ];then
			if [ ${env} == "test" ];then
        		        ssh ${staging_IP} "grep -E \"<param-value>${env}</param-value>\" ${target}/${proj_name}/WEB-INF/web.xml"
				test $? != 0 && echo "config error" && exit 1
			else
        		        ssh ${staging_IP} "grep -E \"<param-value>production</param-value>\" ${target}/${proj_name}/WEB-INF/web.xml"
				test $? != 0 && echo "config error" && exit 1
			fi
		else	
			project_xml="${target}/${proj_name}/WEB-INF/classes/applicationContext_test.xml"
        	        if [ $env == "production" ] || [ $env == "staging" ];then
        	                if ssh ${staging_IP} "test -f ${project_xml}";then
        	                        echo " exist" |tee -a ${log_file}
        	                        exit 1
        	                else
        	                        echo "${project_xml} not exist" |tee -a ${log_file}
        	                fi

        	        else
        	                if ssh ${staging_IP} "test -f ${project_xml}";then
        	                       echo "${project_xml} exist" |tee -a ${log_file}
        	                else
        	                        echo "${project_xml} not exist" |tee -a ${log_file}
        	                        exit 1
        	                fi
        	        fi
		fi
                scp -r ${staging_IP}:${target}/${proj_name} $host:${project_bak}/${proj_name}.increment &>>${log_file}
                if [ $? -eq 0 ];then 
                    echo "rsync suceed" |tee -a ${log_file}
                else
                    echo "rsync error" |tee -a ${log_file}
                    exit 1
                fi
        else
                ssh $host "test ! -d ${project_bak} && mkdir ${project_bak};rm -rf ${project_bak}/ams_${ver}_${env}_${instance}"
                test $? -ne 0 && echo "ssh error" && exit 1
                echo "rsync -ztrvl ${project_bak}/ams_${ver}_${env}_${instance} $host:${project_bak}/" |tee -a ${log_file}
                rsync -ztrvl ${project_bak}/ams_${ver}_${env}_${instance} $host:${project_bak}/ &>>${log_file}
                if [ $? -eq 0 ];then 
                    echo "rsync suceed" |tee -a ${log_file}
                else
                    echo "rsync error" |tee -a ${log_file}
                    exit 1
                fi
        fi
        if [ ${env} == "production" ];then
                echo "offline resin............" |tee -a ${log_file}
                for proxy in ${proxys[@]};do
                        echo "ssh ${proxy} \"cp -f ${nginx_conf} /tmp/nginx.conf.${timestamp}\"" | tee -a ${log_file}
                        ssh ${proxy} "cp -f ${nginx_conf} /tmp/nginx.conf.${timestamp}" 
                        echo "ssh ${proxy} \"sed -i -r 's/(^[ \t]*server[ \t]*${host}:${port}.*)(;.*$)/\1 down\2/g' ${nginx_conf}\"" | tee -a ${log_file} 
                        ssh ${proxy} "sed -i -r 's/(^[ \t]*server[ \t]*${host}:${port}.*)(;.*$)/\1 down\2/g' ${nginx_conf}" 
                        if [ $? -eq 0 ];then
                                ssh ${proxy} "grep -E \"^[ \t]*server[ \t]*${host}:${port}.*down;\" ${nginx_conf}" 
                                if [ $? -eq 0 ];then 
                                    echo "${proxy} nginx change suceed" |tee -a ${log_file}
                                else
                                    echo "${proxy} nginx change error" |tee -a ${log_file}
                                    exit 1
                                fi
                        else
                            echo "${proxy} nginx change error" |tee -a ${log_file}
                            exit 1
                        fi

                        ssh ${proxy} "/data/web/nginx/sbin/nginx -s reload"
                        if [ $? -eq 0 ];then 
                            echo "${proxy} nginx reload suceed" |tee -a ${log_file}
                        else
                            echo "${proxy} nginx reload error" |tee -a ${log_file}
                            exit 1
                        fi
                done
	else
		echo "非生产环境，跳过nginx下线resin"
        fi

	if [ ${env} == "production" ];then
		echo "检查项目可用性，以做备份" |tee -a ${log_file}
		echo "curl http://${host}:${port}/api/system/check" 
        	response=`curl http://${host}:${port}/api/system/check 2>/dev/null`
        	if (echo ${response} |grep -E '"flag" *: *true');then
        	        echo "${host} start backup " |tee -a ${log_file}
        	else
        	        echo "${host} system check failed.请联系运维!" |tee -a ${log_file}
        	        #exit 1
        	fi
	else
		echo "非生产环境，不检查项目可用性，直接备份" |tee -a ${log_file}
	fi

        echo "${host} stop resin" |tee -a ${log_file}
        echo "ssh $host \"sh ${stop_cmd}\"" |tee -a ${log_file}
        ssh $host "sh ${stop_cmd}"
        sleep 5
        if ssh $host "netstat -antlp |grep LIST |grep :${port}";then
            TCP=`ssh $host "netstat -antlp |grep LIST |grep :${port}"`
            PID=`echo $TCP |awk '{print $7}' |awk -F/ '{print $1}'`
            ssh $host "/bin/kill -9 $PID"
            sleep 1
            if ssh $host "netstat -antlp |grep LIST |grep :${port}";then
                        echo "${host} resin stop error" |tee -a ${log_file}
                        exit 1
            fi
            echo "${host} resin stop suceed" |tee -a ${log_file}
        else
            echo "${host} resin stop suceed" |tee -a ${log_file}
        fi

        if [ ${proj_name} != "renren-fenqi-ams" ];then
                echo "异地备份项目"
		rm -rf ${project_bak}/${host}/${proj_name}
		test ! -d ${project_bak}/${host}/${proj_name} && rsync -ztrvl $host:${target}/${proj_name} ${project_bak}/${host}/ &>>${log_file} 
                if [ $? -eq 0 ];then 
                    echo "${host} project remote backup suceed" |tee -a ${log_file}
                else
                    echo "${host} project remote backup error" |tee -a ${log_file}
                    exit 1
                fi
                echo "本地备份项目"
                ssh $host "rm -rf ${project_bak}/${proj_name}.bak;test -d ${target}/${proj_name} && mv ${target}/${proj_name} ${project_bak}/${proj_name}.bak"
                if [ $? -eq 0 ];then 
                    echo "${host} project local backup suceed" |tee -a ${log_file}
                else
                    echo "${host} project local backup error" |tee -a ${log_file}
                    exit 1
                fi
                echo "替换项目"
                ssh $host "cp -Rf ${project_bak}/${proj_name}.increment ${target}/${proj_name}"
                if [ $? -eq 0 ];then 
                    echo "${host} project replace suceed" |tee -a ${log_file}
                else
                    echo "${host} project replace error" |tee -a ${log_file}
                    exit 1
                fi
        else
                echo "异地备份项目"
                rm -rf ${project_bak}/ams_${instance}_${host}
                test ! -d ${project_bak}/ams_${instance}_${host} && scp -r $host:${target}/ROOT ${project_bak}/ams_${instance}_${host} &>>${log_file}
                if [ $? -eq 0 ];then 
                    echo "${host} project remote backup suceed" |tee -a ${log_file}
                else
                    echo "${host} project remote backup error" |tee -a ${log_file}
                    exit 1
                fi
                echo "本地备份项目"
                ssh $host "rm -rf ${project_bak}/ams.bak_${instance};test -d ${target}/ROOT && mv ${target}/ROOT ${project_bak}/ams.bak_${instance}"
                if [ $? -eq 0 ];then 
                    echo "${host} project local backup suceed" |tee -a ${log_file}
                else
                    echo "${host} project local backup error" |tee -a ${log_file}
                    exit 1
                fi

                echo "替换项目"
                ssh $host "cp -Rf ${project_bak}/ams_${ver}_${env}_${instance} ${target}/ROOT"
                if [ $? -eq 0 ];then 
                    echo "${host} project replace suceed" |tee -a ${log_file}
                else
                    echo "${host} project replace error" |tee -a ${log_file}
                    exit 1
                fi
        fi

        echo "${host} start resin" |tee -a ${log_file}
        echo "ssh $host \"sh ${start_cmd}\"" |tee -a ${log_file} 
        ssh $host "sh ${start_cmd}" 
        if [ $? -eq 0 ];then 
            sleep 10
            if ssh $host "netstat -antlp |grep LIST |grep :${port}";then
                if [ ${proj_name} == "renren-fenqi-ams" ];then
                        echo "curl http://${host}:${port}/api/system/check" 
                        response=`curl http://${host}:${port}/api/system/check 2>/dev/null`
                        if (echo ${response} |grep -E '"flag" *: *true') && (echo ${response} |grep -E "\"comment\" *:");then
                                echo "${host} resin start suceed" |tee -a ${log_file}
                        else
                                echo "${host} resin start error" |tee -a ${log_file}
                                exit 1
                        fi
                else
                        echo "curl http://${host}:${port}/api/system/check" 
                        response=`curl http://${host}:${port}/api/system/check 2>/dev/null`
                        if [ ${env} == "test" ];then
                                if (echo ${response} |grep -E '"flag" *: *false') && (echo ${response} |grep -E "\"comment\" *:");then
                                        echo "${host} resin start suceed" |tee -a ${log_file}
                                else
                                        echo "${host} resin start error" |tee -a ${log_file}
                                        exit 1
                                fi
                        else
                                if (echo ${response} |grep -E '"flag" *: *true') && (echo ${response} |grep -E "\"comment\" *:");then
                                        echo "${host} resin start suceed" |tee -a ${log_file}
                                else
                                        echo "${host} resin start error" |tee -a ${log_file}
                                       #exit 1
                                fi
                        fi

                fi

            else
                echo "${host} resin start error" |tee -a ${log_file}
                exit 1
            fi
        else
                echo "${host} resin start error" |tee -a ${log_file}
                exit 1
        fi

        if [ ${env} == "production" ];then
                echo "onlin resin........." |tee -a ${log_file}
                for proxy in ${proxys[@]};do
                        echo "proxy:${proxy}" | tee -a ${log_file}
                        ssh ${proxy} "sed -i '/^[ \t]*server[ ]*${host}:${port}.* down;.*$/s/ *down//g' ${nginx_conf}"
                        if [ $? -eq 0 ];then
                                ssh ${proxy} "grep -E \"^[ \t]*server[ \t]*${host}:${port};\" ${nginx_conf}"
                                if [ $? -eq 0 ];then 
                                    echo "${proxy} nginx change suceed" |tee -a ${log_file}
                                else
                                    echo "${proxy} nginx change error" |tee -a ${log_file}
                                    exit 1
                                fi
                        else
                            echo "${proxy} nginx change error" |tee -a ${log_file}
                            exit 1
                        fi

                        ssh ${proxy} "/data/web/nginx/sbin/nginx -s reload"
                        if [ $? -eq 0 ];then 
                            echo "${proxy} nginx reload suceed" |tee -a ${log_file}
                        else
                            echo "${proxy} nginx reload error" |tee -a ${log_file}
                        fi
                done
	else
		echo "非生产环境，跳过nginx上线resin"
        fi
done
}


if [ $3 == "download" ];then
	download
elif [ $3 == "increment_deploy" ];then
	deploy
	echo "`date +%Y-%m-%d-%H-%M-%S` ${proj_name} ${ver} ${env} ${hosts} increment" >> ${ver_log}
else
	echo "参数错误"
fi
echo "end time:`date`" |tee -a ${log_file}
