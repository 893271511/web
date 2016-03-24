/**
 * Created by Administrator on 2016/3/24 0024.
 */
function getData() {
            $("#result").empty();
            var height = 500;
            $("#result").append("<div><textarea id='tx' style='width:100%;height:"+ height + "px'>执行结果</textarea></div>");
            var env = $("#env").val();
            var project =  $("#id_project").val();
            var version = $("#id_version").val();


            $.ajax({
                url: "/release/",
                type: "POST",
                dataType: "",
                data: {
                    "env": env,
                    "project": project,
                    "version": version
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

