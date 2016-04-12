#!/bin/sh
#$1 project_name
#$2 ver
#$3 env
#$4 ip 
#$5 instance
#脚本使用例：sh coderelease.sh renren-licai-credit-manager 31614 test 10.2.54.240


export PATH="/usr/kerberos/bin:$PATH"
export KRB5CCNAME=/tmp/krb5cc_pub_$$
trap kdestroy 0 1 2 3 5 15
kinit -k -t /etc/krb5.keytab

#环境变量
export LANG="en_US.UTF-8"
export LC_ALL="en_US.utf8"
export LC_LANG="en_US.utf8"
export JAVA_HOME=/usr/java/jdk
export CLASS_PATH=.:$JAVA_HOME/lib
export PATH=$JAVA_HOME/bin:$PATH

export M2_HOME=/usr/local/maven-2.1.0
export M2=$M2_HOME/bin
export MAVEN_OPTS=-Dfile.encoding=utf-8
export PATH=$PATH:$M2


path="/data/staging/new_renren"
repos=""
static_path="/data/staging/new_renren/static"
static_repos="http://svn.fenqi.d.xiaonei.com/frontend/xn.static"
static_deploy_path="/data/static"
start_cmd=""
stop_cmd=""
port=""
need_inc=""

nginx_conf="/data/web/nginx/conf/nginx.conf"
script_path="`pwd`/release/release_scripts"
conf_dir="${script_path}/conf"
logs_dir="${script_path}/logs"
test ! -d ${logs_dir} && mkdir ${logs_dir}
jar_pkg="${script_path}/conf/xiaonei-split-version.jar"
script_name="`basename $0`"
log_file="${logs_dir}/${script_name}.log"
SVN="svn"
echo "------------------------------------------------------" |tee -a ${log_file}
echo "start time:`date`" |tee -a ${log_file}


proj_name=$1
ver="$2"
env="$3"

if [ `ps -ef |grep -v grep |grep "${script_name} ${proj_name}" |wc -l` -gt 3 ];then
	echo "${proj_name} running, Please try again later!"
	exit 1
fi

if echo ${proj_name} |grep "renren-fenqi-ams" &>/dev/null;then
	instance=`echo "${proj_name}" |awk -F. '{print $2}'`
	proj_name=`echo "${proj_name}" |awk -F. '{print $1}'`
	if [ -e "${conf_dir}/${proj_name}.config${instance}" ];then
		. ${conf_dir}/${proj_name}.config${instance}
	else
		echo "${conf_dir}/${proj_name} config file not exist"
		exit 1
	fi
else
	if [ -e "${conf_dir}/${proj_name}.config" ];then
		. ${conf_dir}/${proj_name}.config
	else
		echo "${conf_dir}/${proj_name} config file not exist"
		exit 1
	fi
fi

if [ ${env} != "production" ] && [ $4 == "all" ];then
	echo "not batch deploy"
	exit 1
fi

if [ $4 != "all" ];then
	hosts=($4)
fi
	
test_servers=(10.4.37.120 10.4.37.238 10.4.37.34 10.4.37.5 10.2.52.13)
staging_servers=(10.4.37.233)
production_servers=(10.4.30.145 10.4.30.146 10.4.30.147 10.4.30.148 10.4.16.95 10.4.20.52 10.4.20.54 10.4.25.31 10.4.37.13 10.2.52.13)

if [ ${env} == "test" ];then
	if  ! echo "${test_servers[@]}" | grep -wq "${hosts}";then
		echo "${env}项目不能发到${hosts}" 
		exit 1;
	fi
elif [ ${env} == "staging" ];then
	if  ! echo "${staging_servers[@]}" | grep -wq "${hosts}";then
		echo "${env}项目不能发到${hosts}" 
		exit 1;
	fi
elif [ ${env} == "production" ];then
	if  ! echo "${production_servers[@]}" | grep -wq "${hosts}";then
		echo "${env}项目不能发到${hosts}" 
		exit 1;
	fi
else
	echo "环境不存在"	
fi


which mvn &>/dev/null || echo "mvn not foun" || exit 1
which java &>/dev/null || echo "java not foun" || exit 1 
which svn &>/dev/null || echo "svn not foun" || exit 1
test ! -e "/usr/local/maven-2.1.0/bin/mvn" && echo "mvn not found" && exit 1
test -z "$proj_name" && echo "variable proj_name is not null" && exit 1
test -z "$env" && echo "variable env is not null" && exit 1
test -z "$hosts" && echo "variable hosts is not null" && exit 1
test -z "$path" && echo "variable path is not null" && exit 1;
test -z "$repos" && echo "variable repos is not null" && exit 1
test -z "$static_path" && echo "variable static_path is not null" && exit 1
test -z "$static_repos" && echo "variable static_repos is not null" && exit 1
test -z "$static_deploy_path" && echo "variable static_deploy_path is not null" && exit 1
test -z "${start_cmd}" && echo "variable start cmd is not null" && exit 1
test -z "${stop_cmd}" && echo "variable stop cmd is not null" && exit 1
test -z "$port" && echo "variable port is not null" && exit 1
test -z "$proxys" && echo "variable proxys is not null" && exit 1

proj_target="${path}/${proj_name}/target/$proj_name"
project_bak="/data/project_bak"
timestamp=`date +%Y-%m-%d-%H-%M-%S`
test ! -d ${project_bak} && mkdir -pv ${project_bak}
ver_log="${logs_dir}/${proj_name}.version.log"

#echo "###########################上次发布信息,注意记录#######################" |tee -a ${log_file}
#curl "http://${hosts}:${port}/api/system/check" 2>/dev/null |tee -a ${log_file}
#echo ""
#if [ -f ${ver_log} ] && (cat ${ver_log} |grep ${hosts} |grep ${env} |grep "${proj_name}" &>>/dev/null);then
#		cat ${ver_log} |grep ${hosts} |grep ${env} |grep "${proj_name}" |tail -n 1 |tee -a ${log_file}	
#else
#		echo "版本号未获取到" |tee -a ${log_file}
#fi
#echo "##############################################################" |tee -a ${log_file}

svn_update()
{
	echo "####step 1:update project" |tee -a ${log_file}
	if [ ! -d ${path}/${proj_name}/.svn/ ] ;then
		${SVN} co $repos ${path}/${proj_name} &>> ${log_file}
		if [ $? -eq 0 ];then 
			echo "svn co suceed" |tee -a ${log_file}
		else
			echo "svn co error" |tee -a ${log_file}
			exit 1
		fi
	fi
	
	if [ ! -d "${path}/${proj_name}" ];then
		${SVN} co $repos ${path}/${proj_name} &>> ${log_file}
		if [ $? -eq 0 ];then 
			echo "svn co suceed" |tee -a ${log_file}
		else
			echo "svn co error" |tee -a ${log_file}
			exit 1
		fi
	fi

	#更新代码
	${SVN} up -r ${ver} ${path}/${proj_name}
	if [ $? -eq 0 ];then 
		echo "svn up suceed" |tee -a ${log_file}
	else
		echo "svn up error" |tee -a ${log_file} 
		exit 1
	fi
	
	if [ -n "$need_inc" ]; then
		echo "step additional: update common inc" |tee -a ${log_file}
		if [ ! -d ${path}/${proj_name}/src/main/webapp/inc/.svn/ ] ;then
		    echo "${SVN} co http://svn.fenqi.d.xiaonei.com/frontend/xn.inc $path/src/main/webapp/inc" &>> ${log_file}
		    ${SVN} co http://svn.fenqi.d.xiaonei.com/frontend/xn.inc $path/src/main/webapp/inc &>> ${log_file}
		    if [ $? -eq 0 ];then 
			echo "svn co suceed" |tee -a ${log_file}
	   	    else
			echo "svn co error" |tee -a ${log_file}
			exit 1
	            fi
		else
		    echo "${SVN} up ${path}/${proj_name}/src/main/webapp/inc" |tee -a ${log_file}
		    ${SVN} up ${path}/${proj_name}/src/main/webapp/inc &>> ${log_file}
		    if [ $? -eq 0 ];then 
			echo "svn up suceed" |tee -a ${log_file}
	   	    else
			echo "svn up error" |tee -a ${log_file}
			exit 1
	            fi
		fi
	
	fi
}

maven_project()
{	
	echo "####step 2. maven project" |tee -a ${log_file}
	cd $path/${proj_name}
	if [ ${proj_name} == "renren-fenqi-ams" ];then
		rm -rf ${path}/${proj_name}/target
		test ! -d ${path}/${proj_name}/target && mvn -e -f pom.xml -U clean package -Dmaven.test.skip=true
	    	if [ $? -eq 0 ];then 
	    	    echo "maven build suceed" |tee -a ${log_file}
	    	else
	    	    echo "maven build error" |tee -a ${log_file}
	    	    exit 1
	    	fi
		unzip ${path}/${proj_name}/target/ams.war -d ${path}/${proj_name}/target/ams_${ver} >/dev/null
		echo ${ver} > ${path}/${proj_name}/target/ams_${ver}/WEB-INF/classes/version.txt
	else
		rm -rf ${path}/${proj_name}/target
		test ! -d ${path}/${proj_name}/target && mvn -e -f pom.xml -U clean package -Dmaven.test.skip=true
	    	if [ $? -eq 0 ];then 
	    	    echo "maven build suceed" |tee -a ${log_file}
		    echo ${ver} > ${path}/${proj_name}/target/${proj_name}/WEB-INF/classes/version.txt
		    update_static
	    	else
	    	    echo "maven build error" |tee -a ${log_file}
	    	    exit 1
	    	fi
	fi
}
	
update_static()
{
	echo "####step 3. update static..." |tee -a ${log_file}
	if [ ! -d $static_path/.svn/ ] ;then
		${SVN} co $static_repos $static_path  |tee -a ${log_file}
	else
		${SVN} up $static_path  |tee -a ${log_file}
	fi
	
	echo "####step 4. replace static compress js css html..."  |tee -a ${log_file}
	test -d $static_deploy_path || mkdir -p $static_deploy_path
	
	if [ ${proj_name} == "renren-licai" ] || [ ${proj_name} == "renren-licai-mobile-server" ];then
		java -cp ${script_path}/jar/renren-split-version-licai2.jar -Ddebug=true com/xiaonei/deploy/tools/Worker $static_path $static_deploy_path $proj_target
		if [ $? -eq 0 ];then 
		    echo "replace static suceed" |tee -a ${log_file}
	   	else
		    echo "replace static error" |tee -a ${log_file}
		    exit 1
	        fi
	else
		java -cp ${script_path}/jar/xiaonei-split-version.jar com/xiaonei/deploy/tools/Worker $static_path $static_deploy_path $proj_target
		if [ $? -eq 0 ];then 
		    echo "replace static suceed" |tee -a ${log_file}
	   	else
		    echo "replace static error" |tee -a ${log_file}
		    exit 1
	        fi
	fi
	#rsync -rtzl /data/deploy/static/ /opt/static/ |tee -a ${log_file}
}

config_project()
{
        echo "#####step 5 config project" |tee -a ${log_file}
        if [ ${proj_name} == "renren-fenqi-ams" ];then
		echo ""
                cp -Rf ${path}/${proj_name}/target/ams_${ver} ${project_bak}/ams_${ver}_test_28080
		test $? != 0 && echo "cp error" && rm -rf ${project_bak}/ams_${ver}* && exit 1
		sed -r -i 's/(<param-value>)(development|test|production)(<\/param-value>)/\1test\3/g' ${project_bak}/ams_${ver}_test_28080/WEB-INF/web.xml
                grep -E "<param-value>test</param-value>" ${project_bak}/ams_${ver}_test_28080/WEB-INF/web.xml
		test $? != 0 && echo "config error" && rm -rf ${project_bak}/ams_${ver}* && exit 1
		sed -i -r 's/(property name="port" value=")29080/\128080/g' ${project_bak}/ams_${ver}_test_28080/WEB-INF/classes/applicationContext.xml
		grep -E "name=\"port\" *value=\"28080\"" ${project_bak}/ams_${ver}_test_28080/WEB-INF/classes/applicationContext.xml
		test $? != 0 && echo "config error" && rm -rf ${project_bak}/ams_${ver}* && exit 1

		echo ""
                cp -Rf ${path}/${proj_name}/target/ams_${ver} ${project_bak}/ams_${ver}_staging_28080
		test $? != 0 && echo "cp error" && rm -rf ${project_bak}/ams_${ver}* && exit 1
		sed -r -i 's/(<param-value>)(development|test|production)(<\/param-value>)/\1production\3/g' ${project_bak}/ams_${ver}_staging_28080/WEB-INF/web.xml
                grep -E "<param-value>production</param-value>" ${project_bak}/ams_${ver}_staging_28080/WEB-INF/web.xml
		test $? != 0 && echo "config error" && rm -rf ${project_bak}/ams_${ver}* && exit 1
		sed -i -r 's/(property name="port" value=")29080/\128080/g' ${project_bak}/ams_${ver}_staging_28080/WEB-INF/classes/applicationContext.xml
		grep -E "name=\"port\" *value=\"28080\"" ${project_bak}/ams_${ver}_staging_28080/WEB-INF/classes/applicationContext.xml
		test $? != 0 && echo "config error" && rm -rf ${project_bak}/ams_${ver}* && exit 1

		echo ""
                cp -Rf ${path}/${proj_name}/target/ams_${ver} ${project_bak}/ams_${ver}_production_28080
		test $? != 0 && echo "cp error" && rm -rf ${project_bak}/ams_${ver}* && exit 1
		sed -r -i 's/(<param-value>)(development|test|production)(<\/param-value>)/\1production\3/g' ${project_bak}/ams_${ver}_production_28080/WEB-INF/web.xml
                grep -E "<param-value>production</param-value>" ${project_bak}/ams_${ver}_production_28080/WEB-INF/web.xml
		test $? != 0 && echo "config error" && rm -rf ${project_bak}/ams_${ver}* && exit 1
		sed -i -r 's/(property name="port" value=")29080/\128080/g' ${project_bak}/ams_${ver}_production_28080/WEB-INF/classes/applicationContext.xml
		grep -E "name=\"port\" *value=\"28080\"" ${project_bak}/ams_${ver}_production_28080/WEB-INF/classes/applicationContext.xml
		test $? != 0 && echo "config error" && rm -rf ${project_bak}/ams_${ver}* && exit 1

		echo ""
                cp -Rf ${path}/${proj_name}/target/ams_${ver} ${project_bak}/ams_${ver}_test_29080
		test $? != 0 && echo "cp error" && rm -rf ${project_bak}/ams_${ver}* && exit 1
		sed -r -i 's/(<param-value>)(development|test|production)(<\/param-value>)/\1test\3/g' ${project_bak}/ams_${ver}_test_29080/WEB-INF/web.xml
                grep -E "<param-value>test</param-value>" ${project_bak}/ams_${ver}_test_29080/WEB-INF/web.xml
		test $? != 0 && echo "config error" && rm -rf ${project_bak}/ams_${ver}* && exit 1
		sed -i 's/ams\./ams2./g' ${project_bak}/ams_${ver}_test_29080/WEB-INF/classes/logback.xml
		sed -i -r 's/(property name="port" value=")28080/\129080/g' ${project_bak}/ams_${ver}_test_29080/WEB-INF/classes/applicationContext.xml
		grep -E "name=\"port\" *value=\"29080\"" ${project_bak}/ams_${ver}_test_29080/WEB-INF/classes/applicationContext.xml
		test $? != 0 && echo "config error" && rm -rf ${project_bak}/ams_${ver}* && exit 1

		echo ""
                cp -Rf ${path}/${proj_name}/target/ams_${ver} ${project_bak}/ams_${ver}_staging_29080
		test $? != 0 && echo "cp error" && rm -rf ${project_bak}/ams_${ver}* && exit 1
		sed -r -i 's/(<param-value>)(development|test|production)(<\/param-value>)/\1production\3/g' ${project_bak}/ams_${ver}_staging_29080/WEB-INF/web.xml
                grep -E "<param-value>production</param-value>" ${project_bak}/ams_${ver}_staging_29080/WEB-INF/web.xml
		test $? != 0 && echo "config error" && rm -rf ${project_bak}/ams_${ver}* && exit 1
		sed -i 's/ams\./ams2./g' ${project_bak}/ams_${ver}_staging_29080/WEB-INF/classes/logback.xml
		sed -i -r 's/(property name="port" value=")28080/\129080/g' ${project_bak}/ams_${ver}_staging_29080/WEB-INF/classes/applicationContext.xml
		grep -E "name=\"port\" *value=\"29080\"" ${project_bak}/ams_${ver}_staging_29080/WEB-INF/classes/applicationContext.xml
		test $? != 0 && echo "config error" && rm -rf ${project_bak}/ams_${ver}* && exit 1

		echo ""
                cp -Rf ${path}/${proj_name}/target/ams_${ver} ${project_bak}/ams_${ver}_production_29080
		test $? != 0 && echo "cp error" && rm -rf ${project_bak}/ams_${ver}* && exit 1
		sed -r -i 's/(<param-value>)(development|test|production)(<\/param-value>)/\1production\3/g' ${project_bak}/ams_${ver}_production_29080/WEB-INF/web.xml
                grep -E "<param-value>production</param-value>" ${project_bak}/ams_${ver}_production_29080/WEB-INF/web.xml
		test $? != 0 && echo "config error" && rm -rf ${project_bak}/ams_${ver}* && exit 1
		sed -i 's/ams\./ams2./g' ${project_bak}/ams_${ver}_production_29080/WEB-INF/classes/logback.xml
		sed -i -r 's/(property name="port" value=")28080/\129080/g' ${project_bak}/ams_${ver}_production_29080/WEB-INF/classes/applicationContext.xml
		grep -E "name=\"port\" *value=\"29080\"" ${project_bak}/ams_${ver}_production_29080/WEB-INF/classes/applicationContext.xml
		test $? != 0 && echo "config error" && rm -rf ${project_bak}/ams_${ver}* && exit 1
		echo "检查项目配置"
		if [ ${env} == "test" ];then
        	        grep -E "<param-value>${env}</param-value>" ${project_bak}/ams_${ver}_${env}_${instance}/WEB-INF/web.xml
			test $? != 0 && echo "config error" && rm -rf ${project_bak}/ams_${ver}* && exit 1
			grep -E "name=\"port\" *value=\"${instance}\"" ${project_bak}/ams_${ver}_${env}_${instance}/WEB-INF/classes/applicationContext.xml 
			test $? != 0 && echo "config error" && rm -rf ${project_bak}/ams_${ver}* && exit 1
		else
        	        grep -E "<param-value>production</param-value>" ${project_bak}/ams_${ver}_${env}_${instance}/WEB-INF/web.xml 
			test $? != 0 && echo "config error" && rm -rf ${project_bak}/ams_${ver}* && exit 1
			grep -E "name=\"port\" *value=\"${instance}\"" ${project_bak}/ams_${ver}_${env}_${instance}/WEB-INF/classes/applicationContext.xml 
			test $? != 0 && echo "config error" && rm -rf ${project_bak}/ams_${ver}* && exit 1
		fi
	elif [ ${proj_name} == "renren-licai-credit-manager" ];then
		echo ""
		rm -rf ${proj_target}_${ver}
		test ! -d ${proj_target}_${ver} && cp -Rf $proj_target ${proj_target}_${ver}
		test $? != 0 && echo "cp error" && rm -rf ${proj_target}_${ver} && exit 1

		echo ""
		rm -rf ${project_bak}/${proj_name}_${ver}_test 
		test ! -d ${project_bak}/${proj_name}_${ver}_test && cp -Rf ${proj_target}_${ver} ${project_bak}/${proj_name}_${ver}_test
		test $? != 0 && echo "cp error" && rm -rf ${project_bak}/${proj_name}_${ver}* && exit 1
		sed -r -i 's/(<param-value>)(test|production)(<\/param-value>)/\1test\3/g' ${project_bak}/${proj_name}_${ver}_test/WEB-INF/web.xml
                grep -E "<param-value>test</param-value>" ${project_bak}/${proj_name}_${ver}_test/WEB-INF/web.xml
		test $? != 0 && echo "config error" && rm -rf ${project_bak}/${proj_name}_${ver}* && exit 1

		echo ""
		rm -rf ${project_bak}/${proj_name}_${ver}_staging
		test ! -d ${project_bak}/${proj_name}_${ver}_staging && cp -Rf ${proj_target}_${ver} ${project_bak}/${proj_name}_${ver}_staging
		test $? != 0 && echo "cp error" && rm -rf ${project_bak}/${proj_name}_${ver}* && exit 1
		sed -r -i 's/(<param-value>)(test|production)(<\/param-value>)/\1production\3/g' ${project_bak}/${proj_name}_${ver}_staging/WEB-INF/web.xml
                grep -E "<param-value>production</param-value>" ${project_bak}/${proj_name}_${ver}_staging/WEB-INF/web.xml
		test $? != 0 && echo "config error" && rm -rf ${project_bak}/${proj_name}_${ver}* && exit 1

		echo ""
		rm -rf ${project_bak}/${proj_name}_${ver}_production
		test ! -d ${project_bak}/${proj_name}_${ver}_production && cp -Rf ${proj_target}_${ver} ${project_bak}/${proj_name}_${ver}_production
		test $? != 0 && echo "cp error" && rm -rf ${project_bak}/${proj_name}_${ver}* && exit 1
		sed -r -i 's/(<param-value>)(test|production)(<\/param-value>)/\1production\3/g' ${project_bak}/${proj_name}_${ver}_production/WEB-INF/web.xml
                grep -E "<param-value>production</param-value>" ${project_bak}/${proj_name}_${ver}_production/WEB-INF/web.xml
		test $? != 0 && echo "config error" && rm -rf ${project_bak}/${proj_name}_${ver}* && exit 1

		echo "检查项目配置"
		if [ ${env} == "test" ];then
        	        grep -E "<param-value>${env}</param-value>" ${project_bak}/${proj_name}_${ver}_${env}/WEB-INF/web.xml
			test $? != 0 && echo "config error" && rm -rf ${project_bak}/${proj_name}_${ver}* && exit 1
		else
        	        grep -E "<param-value>production</param-value>" ${project_bak}/${proj_name}_${ver}_${env}/WEB-INF/web.xml 
			test $? != 0 && echo "config error" && rm -rf ${project_bak}/${proj_name}_${ver}* && exit 1
		fi
	else
		echo ""
		rm -rf ${proj_target}_${ver}
		if [ ! -f $proj_target/WEB-INF/classes/applicationContext_test.xml ];then
			echo "project not find applicationContext_test.xml file"
			exit 1
		fi
		test ! -d ${proj_target}_${ver} && cp -Rf $proj_target ${proj_target}_${ver}
		test $? != 0 && echo "cp error" && rm -rf ${proj_target}_${ver} && exit 1
                project_xml="${project_bak}/${proj_name}_${ver}_${env}/WEB-INF/classes/applicationContext_test.xml"

		echo ""
		rm -rf ${project_bak}/${proj_name}_${ver}_test 
		test ! -d ${project_bak}/${proj_name}_${ver}_test && cp -Rf ${proj_target}_${ver} ${project_bak}/${proj_name}_${ver}_test
		test $? != 0 && echo "cp error" && rm -rf ${project_bak}/${proj_name}_${ver}* && exit 1
		test ! -f ${project_bak}/${proj_name}_${ver}_test/WEB-INF/classes/applicationContext_test.xml && echo "config error" && exit 1

		echo ""
		rm -rf ${project_bak}/${proj_name}_${ver}_staging 
		test ! -d ${project_bak}/${proj_name}_${ver}_staging && cp -Rf ${proj_target}_${ver} ${project_bak}/${proj_name}_${ver}_staging
		test $? != 0 && echo "cp error" && rm -rf ${project_bak}/${proj_name}_${ver}* && exit 1
		rm -rf ${project_bak}/${proj_name}_${ver}_staging/WEB-INF/classes/applicationContext_test.xml
		test -f ${project_bak}/${proj_name}_${ver}_staging/WEB-INF/classes/applicationContext_test.xml && echo "config error" && exit 1

		echo ""
		rm -rf ${project_bak}/${proj_name}_${ver}_production 
		test ! -d ${project_bak}/${proj_name}_${ver}_production && cp -Rf ${proj_target}_${ver} ${project_bak}/${proj_name}_${ver}_production
		test $? != 0 && echo "cp error" && rm -rf ${project_bak}/${proj_name}_${ver}* && exit 1
		rm -rf ${project_bak}/${proj_name}_${ver}_production/WEB-INF/classes/applicationContext_test.xml
		test -f ${project_bak}/${proj_name}_${ver}_production/WEB-INF/classes/applicationContext_test.xml && echo "config error" && exit 1
		
		echo "检查项目配置"
                if [ $env == "production" ] || [ $env == "staging" ];then
                        if [ -e ${project_xml} ];then
                                echo "${project_xml} exist" |tee -a ${log_file}
				exit 1
                        else
                                echo "${project_xml} not exist" |tee -a ${log_file}
                        fi
		
                else
                        if [ -e ${project_xml} ];then
                               echo "${project_xml} exist" |tee -a ${log_file}
                        else
                                echo "${project_xml} not exist" |tee -a ${log_file}
                                exit 1
                        fi
                fi
        fi
}


deploy()
{
echo "#####step 6 deploy"
echo "同步包到各服务器"
count=${#hosts[@]}
i=0
for host in ${hosts[@]};do
        i=$(($i+1))
	echo "共${count}台，第${i}台:${host}"
	if [ ${proj_name} != "renren-fenqi-ams" ];then 
                ssh $host "test ! -e ${project_bak} && mkdir -pv ${project_bak}; rm -rf ${project_bak}/${proj_name}_${ver}_${env}"
                test $? -ne 0 && echo "ssh error" && exit 1
                rsync -ztrvl ${project_bak}/${proj_name}_${ver}_${env} $host:${project_bak}/ &>>${log_file}
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

			#haproxy real_server下线
			if [ ${proj_name} == "renren-fenqi-ams" ];then
			  NUMBER=`echo "${target}" |awk -F"/" '{print $3}' |awk -F"-" '{print $NF}'`
			  if echo ${NUMBER}|grep "[1-2]" &>/dev/null;then
			    ssh ${proxy} "echo \"disable server proxy/real_server_${NUMBER}\" | socat stdio /var/run/haproxy.sock"
			    ssh ${proxy} "echo \"show stat \" | socat stdio /var/run/haproxy.sock |grep real_server_${NUMBER} |grep MAINT"
			    if [ $? == 0 ];then
			      echo "haproxy offline succeed"
			    else
			      echo "haproxy offline fail"
			      exit
			    fi
			  else
			    echo "haproxy real_server id error"
			    exit 1
			  fi
			fi

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
		sleep 3
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
	    else
		if [ ${proj_name} == "renren-fenqi-ams" ];then
			DIR=`echo "${target}" |awk -F"/" '{print $3}'`
			if ssh $host "/usr/java/jdk/bin/jps -v |grep ${DIR}";then
				PROCESS=`ssh $host "/usr/java/jdk/bin/jps -v |grep ${DIR}"`
				PID2=`echo "$PROCESS" |awk '{print $1}'`
				ssh $host "/bin/kill -9 $PID2"
				ssh $host "/usr/java/jdk/bin/jps -v |grep ${DIR}" && echo "${host} resin stop error" && exit 1
			fi
		fi
	    fi
	    echo "${host} resin stop suceed" |tee -a ${log_file}
	else
		if [ ${proj_name} == "renren-fenqi-ams" ];then
			DIR=`echo "${target}" |awk -F"/" '{print $3}'`
			if ssh $host "/usr/java/jdk/bin/jps -v |grep ${DIR}";then
				PROCESS=`ssh $host "/usr/java/jdk/bin/jps -v |grep ${DIR}"`
				PID2=`echo "$PROCESS" |awk '{print $1}'`
				ssh $host "/bin/kill -9 $PID2"
				ssh $host "/usr/java/jdk/bin/jps -v |grep ${DIR}" && echo "${host} resin stop error" && exit 1
			fi
	    		echo "${host} resin stop suceed" |tee -a ${log_file}
		else
	    		echo "${host} resin stop suceed" |tee -a ${log_file}
		fi
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
		ssh $host "cp -Rf ${project_bak}/${proj_name}_${ver}_${env} ${target}/${proj_name}"
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
			if (echo ${response} |grep -E '"flag" *: *true') && (echo ${response} |grep -E "\"comment\" *: *\"${ver}\"");then
	    			echo "${host} resin start suceed" |tee -a ${log_file}
			else
	    			echo "${host} resin start error" |tee -a ${log_file}
				exit 1
			fi
		else
			echo "curl http://${host}:${port}/api/system/check" 
			response=`curl http://${host}:${port}/api/system/check 2>/dev/null`
			if [ ${env} == "test" ];then
				if (echo ${response} |grep -E '"flag" *: *false') && (echo ${response} |grep -E "\"comment\" *: *\"${ver}\"");then
	    				echo "${host} resin start suceed" |tee -a ${log_file}
				else
	    				echo "${host} resin start error" |tee -a ${log_file}
					exit 1
				fi
			else
				if (echo ${response} |grep -E '"flag" *: *true') && (echo ${response} |grep -E "\"comment\" *: *\"${ver}\"");then
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

			#haproxy real_server上线
			if [ ${proj_name} == "renren-fenqi-ams" ];then
			  if echo ${NUMBER}|grep "[1-2]" &>/dev/null;then
			    ssh ${proxy} "echo \"enable server proxy/real_server_${NUMBER}\" | socat stdio /var/run/haproxy.sock"
			    ssh ${proxy} "echo \"show stat \" | socat stdio /var/run/haproxy.sock |grep real_server_${NUMBER} |grep UP"
			    if [ $? == 0 ];then
			      echo "haproxy offline succeed"
			    else
			      echo "haproxy offline fail"
			      exit
			    fi
			  else
			    echo "haproxy real_server id error"
			    exit 1
			  fi
			fi

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

#main
if [ ${proj_name} == "renren-fenqi-ams" ];then
	if find ${project_bak} -name ams_${ver}_${env}_${instance} |grep ams_${ver}_${env}_${instance};then
		echo "项目包已存，直接发布"
		echo "检查项目配置"
		if [ ${env} == "test" ];then
        	        grep -E "<param-value>${env}</param-value>" ${project_bak}/ams_${ver}_${env}_${instance}/WEB-INF/web.xml |tee -a ${log_file}
			test $? != 0 && echo "config error" && rm -rf ${project_bak}/ams_${ver}* && exit 1
			grep -E "name=\"port\" *value=\"${instance}\"" ${project_bak}/ams_${ver}_${env}_${instance}/WEB-INF/classes/applicationContext.xml |tee -a ${log_file}
			test $? != 0 && echo "config error" && rm -rf ${project_bak}/ams_${ver}* && exit 1
		else
        	        grep -E "<param-value>production</param-value>" ${project_bak}/ams_${ver}_${env}_${instance}/WEB-INF/web.xml |tee -a ${log_file}
			test $? != 0 && echo "config error" && rm -rf ${project_bak}/ams_${ver}* && exit 1
			grep -E "name=\"port\" *value=\"${instance}\"" ${project_bak}/ams_${ver}_${env}_${instance}/WEB-INF/classes/applicationContext.xml |tee -a ${log_file}
			test $? != 0 && echo "config error" && rm -rf ${project_bak}/ams_${ver}* && exit 1
		fi
	else
		if [ $env == "production" ];then
			if [ -d "${project_bak}/ams_${ver}_staging_28080" ] || [ -d "${project_bak}/ams_${ver}_staging_29080" ];then
				echo "${project_bak}/ams_${ver}_staging_${instance}存在，无需再次打包，直接发布。" |tee -a ${log_file}
			else
				echo "${project_bak}/ams_${ver}_staging_${instance} not fount, please staging" |tee -a ${log_file}
				exit 1
			fi
		else
			svn_update
			maven_project
		fi
		config_project
	fi
else
	if find ${project_bak} -name ${proj_name}_${ver}_${env} |grep ${proj_name}_${ver}_${env};then
		echo "项目包已存，直接发布"
		echo "检查项目配置"
		if [ ${proj_name} == "renren-licai-credit-manager" ];then
			if [ ${env} == "test" ];then
        		        grep -E "<param-value>${env}</param-value>" ${project_bak}/${proj_name}_${ver}_${env}/WEB-INF/web.xml
				test $? != 0 && echo "config error" && rm -rf ${project_bak}/${proj_name}_${ver}* && exit 1
			else
        		        grep -E "<param-value>production</param-value>" ${project_bak}/${proj_name}_${ver}_${env}/WEB-INF/web.xml 
				test $? != 0 && echo "config error" && rm -rf ${project_bak}/${proj_name}_${ver}* && exit 1
			fi
		else
                	project_xml="${project_bak}/${proj_name}_${ver}_${env}/WEB-INF/classes/applicationContext_test.xml"
                	if [ $env == "production" ] || [ $env == "staging" ];then
                	        if [ -e ${project_xml} ];then
                	                echo "${project_xml} exist" |tee -a ${log_file}
					exit 1
                	        else
                	                echo "${project_xml} not exist" |tee -a ${log_file}
                	        fi
			
                	else
                	        if [ -e ${project_xml} ];then
                	               echo "${project_xml} exist" |tee -a ${log_file}
                	        else
                	                echo "${project_xml} not exist" |tee -a ${log_file}
                	                exit 1
                	        fi
                	fi
		fi
	else
		if [ $env == "production" ];then
			if [ -d "${project_bak}/${proj_name}_${ver}_staging" ];then
				echo "${project_bak}/${proj_name}_${ver}_staging存在，无需再次打包，直接发布。" |tee -a ${log_file}
			else
				echo "${project_bak}/${proj_name}_${ver}_staging not fount, please staging"  |tee -a ${log_file}
				exit 1
			fi
		else
			svn_update
			maven_project
		fi
		config_project
		
	fi
fi
deploy
if [ ${proj_name} == "renren-fenqi-ams" ];then
	echo "`date +%Y-%m-%d-%H-%M-%S` ${proj_name} ${ver} ${env} ${hosts}" >> ${ver_log}
else
	echo "`date +%Y-%m-%d-%H-%M-%S` ${proj_name} ${ver} ${env} ${hosts}" >> ${ver_log}
fi
echo "deploy succeed" |tee -a ${log_file}
echo "end time:`date`" |tee -a ${log_file}
