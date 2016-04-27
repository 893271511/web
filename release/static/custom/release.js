/**
 *  检查填写的信息及弹出确认框
 */

function checkReleaseInfo() {
    var svnVersion = document.getElementById('id_version').value;
    if (!svnVersion.match(/^\d+$/)) {
        alert("svn 版本号填写有误，请确认");
        document.getElementById('id_version').focus();

        return false;
    }
    if(document.getElementById("id_server")) {
        var answer = confirm(
            "环境：" + document.getElementById('id_env').value + "\n"
            + "项目：" + document.getElementById('id_project').value + "\n"
            + "版本号：" + svnVersion + "\n"
            + "服务器：" + document.getElementById("id_server").value + "\n"
            + "\n"
            + "确定发布？"
        );

    }else{
        var answer = confirm(
            "环境：" + document.getElementById('id_env').value + "\n"
            + "项目：" + document.getElementById('id_project').value + "\n"
            + "版本号：" + svnVersion + "\n"
            + "\n"
            + "确定发布？"
        );
    }

    if (answer) {
        //document.getElementById("id_release").submit();
        return true
    }
    else{
        return false
    }
}

/**
 * 点击多台发布按钮时触发
 */
function release2() {

            if(checkReleaseInfo()){

            }
            else{
                return false
            }
            $("#result").empty();
            var height = 500;
            $("#result").append("<div><textarea id='tx' style='width:100%;height:"+ height + "px'>执行结果</textarea></div>");
            var env = $("#id_env").val();
            var project =  $("#id_project").val();
            var version = $("#id_version").val();
            var server = $("#id_server").val();
            var csrfmiddlewaretoken = $('input[name=csrfmiddlewaretoken]').val();

            $.ajax({
                url: "/release/",
                type: "POST",
                dataType: "",
                data: {
                    "env": env,
                    "project": project,
                    "version": version,
                    "server":server,
                    "csrfmiddlewaretoken":csrfmiddlewaretoken
                },

                success: function (data){
                    alert(data);
                    console.log(data);
                    var area = $("#tx");
                    area.html(data);
                    if(autoScroll(area)) {
                        area.scrollTop(area[0].scrollHeight);
                    }
                },
                error: function(data){
                    console.log(data);
                }
            })
        };
        function autoScroll(obj){
            var viewH = obj.height();//可见高
            var contentH = obj[0].scrollHeight;//内容高度
            var scrollTop = obj.scrollTop();//滚动高度
            if(scrollTop == 0 || (contentH - viewH - scrollTop <= 100)) { //到达底部100px时,加载新内容
            //if(scrollTop/(contentH -viewH)>=0.95){ //到达底部100px时,加载新内容
                return true;
            }else{
                return false;
            }

        }
/**
 * 点击多台发布按钮时触发
 */
function oneRelease2() {
            if(document.getElementById('id_version').value.length==0){
                alert('请输入版本号！');
                document.getElementById('id_version').focus();
                return false;
            }
            $("#result").empty();
            var height = 500;
            $("#result").append("<div><textarea id='tx' style='width:100%;height:"+ height + "px'>执行结果</textarea></div>");
            var env = $("#id_env").val();
            var project =  $("#id_project").val();
            var version = $("#id_version").val();
            var server = $("#id_server").val();
            var csrfmiddlewaretoken = $('input[name=csrfmiddlewaretoken]').val();

            $.ajax({
                url: "/onerelease/",
                type: "POST",
                dataType: "",
                data: {
                    "env": env,
                    "project": project,
                    "version": version,
                    "server":server,
                    "csrfmiddlewaretoken":csrfmiddlewaretoken
                },
                success: function (data){

                    var area = $("#tx");
                    area.html(data);
                    if(autoScroll(area)) {
                        area.scrollTop(area[0].scrollHeight);
                    }
                },
                error: function(data){
                    console.log(data);
                }
            })

        };
        function autoScroll(obj){
            var viewH = obj.height();//可见高
            var contentH = obj[0].scrollHeight;//内容高度
            var scrollTop = obj.scrollTop();//滚动高度
            if(scrollTop == 0 || (contentH - viewH - scrollTop <= 100)) { //到达底部100px时,加载新内容
            //if(scrollTop/(contentH -viewH)>=0.95){ //到达底部100px时,加载新内容
                    return true;
            }else{
                return false;
            }

        }

/**
 * 选择项目时触发
 */
function selectProject() {

            $("#result").empty();
            var env = $("#id_env").val();
            var project = $("#id_project").val();
            var csrfmiddlewaretoken = $('input[name=csrfmiddlewaretoken]').val();

            $.ajax({
                url: "/select_project/",
                type: "POST",
                dataType: "json",
                data: {
                    "env": env,
                    "project": project,
                    "csrfmiddlewaretoken":csrfmiddlewaretoken
                },
                success: function (data){
                    var optionstring = "";
                    $.each(data,function(i,item){
                        optionstring += "<option value=\"" + item + "\" >" + item + "</option>";
                    })
                    $("#id_server").html(optionstring)
                },
                error: function(data){
                    console.log(data);
                }
            })

        };

/**
 * 点击切换环境时触发
 */
    function switchEnv(release_type) {
            $("#result").empty();
            var env = $("#id_env").val();
            var csrfmiddlewaretoken = $('input[name=csrfmiddlewaretoken]').val();

            $.ajax({
                url: "/switch/",
                type: "POST",
                dataType: "json",
                data: {
                    "env": env,
                    "csrfmiddlewaretoken":csrfmiddlewaretoken
                },
                success: function (data){
                    $('#switch').html(data['env_cn'])
                    $("#id_env").val(data.env_en);
                    if (release_type == "onerelease"){
                        selectProject();
                    };

                },
                error: function(data){
                    console.log(data);
                }
            })
        };

/**
 * 发布项目请求
 */

        function release() // 创建xmlhttprequest,ajax开始
        {
            if(checkReleaseInfo()){

            }
            else{
                return false
            }
            var req; //定义变量，用来创建xmlhttprequest对象
            $("#result").empty();
            var height = 500;
            $("#result").append("<div><textarea id='tx' style='width:100%;height:"+ height + "px'></textarea></div>");
            var env = $("#id_env").val();
            var project =  $("#id_project").val();
            var version = $("#id_version").val();
            var server = $("#id_server").val();
            var csrfmiddlewaretoken = $('input[name=csrfmiddlewaretoken]').val();


            if(window.XMLHttpRequest) //非IE浏览器及IE7(7.0及以上版本)，用xmlhttprequest对象创建
            {
                req=new XMLHttpRequest();
            }
            else if(window.ActiveXObject) //IE(6.0及以下版本)浏览器用activexobject对象创建,如果用户浏览器禁用了ActiveX,可能会失败.
            {
                req=new ActiveXObject("Microsoft.XMLHttp");
            }

            if(req) //成功创建xmlhttprequest
            {

                if (server == null || server == undefined || server == '') {
                    var url="/release/"; //要请求的服务端地址
                    req.open("POST",url,true); //与服务端建立连接(请求方式post或get，地址,true表示异步)
                    req.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
                    req.onreadystatechange = callback; //指定回调函数
                    req.send("env=" +env+"&project="+project +"&version="+version+"&csrfmiddlewaretoken="+csrfmiddlewaretoken); //发送请求
                } else {
                    var url="/onerelease/"; //要请求的服务端地址
                    req.open("POST",url,true); //与服务端建立连接(请求方式post或get，地址,true表示异步)
                    req.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
                    req.onreadystatechange = callback; //指定回调函数
                    req.send("env=" +env+"&server="+server+"&project="+project +"&version="+version+"&csrfmiddlewaretoken="+csrfmiddlewaretoken); //发送请求
                }





            }

            function callback() //回调函数，对服务端的响应处理，监视response状态
            {
                var area = $("#tx");
                if(req.readyState==4) //请求状态为4表示成功
                {
                    if(req.status==200) //http状态200表示OK
                    {

                        area.append("\n运行结束");
                        if(autoScroll(area)) {
                            area.scrollTop(area[0].scrollHeight);
                        }
                        alert("运行结束"); //所有状态成功，执行此函数，显示数据
                    }
                    else //http返回状态失败
                    {
                        alert("失败" + req.readyState);

                    }
                }
                else //请求状态还没有成功，页面等待
                {
                    //$("#id_btn1").val(req.readyState);
                    //alert("服务端返回状态3 " + req.readyState + req.responseText);
                    area.html(req.responseText);
                    //$("#result").append("<img src='/static/loading.gif'>")
                    $("#result1").html("<img src='/static/loading.gif'>")
                    if(autoScroll(area)) {
                        area.scrollTop(area[0].scrollHeight);
                    }
                }
            }

            function autoScroll(obj){
                var viewH = obj.height();//可见高
                var contentH = obj[0].scrollHeight;//内容高度
                var scrollTop = obj.scrollTop();//滚动高度
                if(scrollTop == 0 || (contentH - viewH - scrollTop <= 100)) { //到达底部100px时,加载新内容
                //if(scrollTop/(contentH -viewH)>=0.95){ //到达底部100px时,加载新内容
                    return true;
                }else{
                    return false;
                }

            }
        }