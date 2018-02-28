function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    $(".form-login").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }

     var req_data = {
            mobile : mobile,
            password : passwd
        }
        //这里需要将js对象, 转换成JSON字符串
        req_json = JSON.stringify(req_data)
        //$.get和$.post都是ajax的简写, 没法设置json.

        // CSRF_token的设置, 除了body里, 还还可以通过请求头设置
        // 我们可以再设置的时候, 从cookie中去读csrf_token设置到请求头中
        // 因为有同源策略, 别的是访问不到我们的cookie. 我们可以取
        $.ajax({
            url: "/api/v1_0/sessions", //请求路径URL
            type: "post", //请求方式
            data: req_json, //发送的请求数据
            contentType: "application/json", //指明给后端发送的是JSON格式的数据
            dataType: 'json', //指明从后端收到的数据是JSON格式的数据
            headers:{
                "X-CSRFToken": getCookie("csrf_token")//自定义请求头, 调用一个方法从cookie获取
            },
            success: function (resp) {
                if (resp.errno == 0) {
                //注册成功, 引导到首页
                location.href = "/";
                } else {
                    alert(resp.errmsg);
                }
            }
        })
    });
})