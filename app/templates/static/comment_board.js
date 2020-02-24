function isEmptyObject(obj) {
    for (var i in obj) {
        if (obj.hasOwnProperty(i)) {
            return false;
        }
    }
    return true;
}



function join(){
{
        
        var username = document.getElementById("input-username").value;
        var password = document.getElementById("input-password").value;

          $.ajax({
    url: '/api/login',
    dataType: 'json',
    type: 'post',
    contentType: 'application/json',
    data: JSON.stringify( { "username": username, "password": password} ),
    processData: false,
    success: function( data, textStatus, jQxhr ){
        myObjStr = JSON.stringify(data);
        json = JSON.parse(myObjStr)
        error = json['Error']

        if(! isEmptyObject(error)){
        alertify.error(json['Error']);
        }
        else{
            $(location).attr('href', '/lk')
        //alertify.success(json['User']['username']);
        }

    },
    error: function( jqXhr, textStatus, errorThrown ){
        console.log( errorThrown );
    }


});


}
}


function send_comment(){
  var username = document.getElementById("input-nickname").value;
  var comment = document.getElementById("input-comment").value;

  var ip = location.host;
  console.log(ip);

  var socket= new WebSocket("ws://" + ip + "/api/ws");
  if (document.getElementById('private-checkbox').checked) {
            var sendJson = {
    action: "send_comment",
    data: {'username' : username, 'comment': comment, 'private': 'TRUE'}
  }
  }
  else {
            var sendJson = {
    action: "send_comment",
    data: {'username' : username, 'comment': comment, 'private': 'FALSE'}
  }
  }

  

  x = ""


  socket.onmessage = function (e) {
  json = JSON.parse(e.data);
  
    if(json.action == 'connect'){
      socket.send(JSON.stringify(sendJson));
    }

    if(json.Response.ok == 'comment sended'){

      if (document.getElementById('private-checkbox').checked) {
            $('#comments_table tbody').append(
                        '<tr><td>' + 'anonymous'+
                        '</td><td>' + 'private comment' +
                        '</td></tr>'
                    );
      }
      else {
            $('#comments_table tbody').append(
                        '<tr><td>' + username+
                        '</td><td>' + comment +
                        '</td></tr>'
                    );
      }
        
      alertify.success(json.Response.ok);
    }
    else{
      alertify.error(json.Response);
    }


    
};


}


$.ajax({

                  url: '/api/get_user',
                  method: "get",
                  dataType: "json",

                  success: function (jdata) {
                    if(! isEmptyObject(jdata.Error)){
                      $("#auth").html('<span class="auth-text">Sign In</span><p><input type="text" class="login-field" style="width:100%" id="input-username" placeholder="Your login"></p><p><input type="text" class="password-field" style="width:100%" id="input-password" placeholder="Your password"></p><input class="submit-button" onClick="join()" type="submit" value="Join"><a href="register"><span class="register-button">Register >></span></a>');
                    } 
                    else{

                      $("#auth").html('<span class="auth-text" id="username"></span><p><span class="money" id="coins">$</span></p><p><a href="add_page" class="lk-links">Add merchandise</a></p><p><a href="orders" class="lk-links">My orders</a></p>  <p><a href="send_page" class="lk-links">Send money</a></p><p class="logout"><a href="" onClick="logout()">Logout</a></p>');

                    var username = jdata.User.username;
                    var coins = jdata.User.coins;
                    $("#username").html(username);
                    $("#coins").html(coins);
                    }

                   },

                    error: function(errorThrown){
                       console.log(errorThrown);
                    }

});  



var ip = location.host;
console.log(ip);

var socket= new WebSocket("ws://" + ip + "/api/ws");

var sendJson = {
    action: "get_comments",
    data: '*'
}

x = ""


socket.onmessage = function (e) {
  json = JSON.parse(e.data);
  
    if(json.action == 'connect'){
      socket.send(JSON.stringify(sendJson));
    }

    if(json.Response){
      //$("comments_table").html(e.data);
      $(json.Response).each(function (index, item) {
                    $('#comments_table tbody').append(
                        '<tr><td>' + item[0]+
                        '</td><td>' + item[1] +
                        '</td></tr>'
                    )
                });


    }
    
};






function logout(){

$.ajax({

                  url: '/api/logout',
                  method: "get",
                  dataType: "json",

                  success: function (jdata) {
                    $(location).attr('href', '/')
                   },

                    error: function(errorThrown){
                       $(location).attr('href', '/lk')
                       console.log(errorThrown);
                    }

});

}


function my_comments(){
  $("#comments_table tbody").html("");
  var username = document.getElementById("input-nickname").value;

  var ip = location.host;
  var socket= new WebSocket("ws://" + ip + "/api/ws");
  var sendJson = {
    action: "get_my_comments",
    data: username
  }

  if(isEmptyObject(username)){
     alertify.error('Nickname is required');
  }else{

  socket.onmessage = function (e) {
  json = JSON.parse(e.data);
  
    if(json.action == 'connect'){
      socket.send(JSON.stringify(sendJson));
    }


    if(!isEmptyObject(json.Response[0])){
      $(json.Response).each(function (index, item) {
                    $('#comments_table tbody').append(
                        '<tr><td>' + username +
                        '</td><td>' + item[0] +
                        '</td></tr>'
                    )
                });


    }
    else{
      alertify.error('User does not exists!');
    }
    
};
}

}


function all_comments(){
  var ip = location.host;
console.log(ip);

var socket= new WebSocket("ws://" + ip + "/api/ws");

var sendJson = {
    action: "get_comments",
    data: '*'
}

x = ""


socket.onmessage = function (e) {
  json = JSON.parse(e.data);
  
    if(json.action == 'connect'){
      socket.send(JSON.stringify(sendJson));
    }

    if(json.Response){
      $('#comments_table tbody').html("");
      $(json.Response).each(function (index, item) {
                    $('#comments_table tbody').append(
                        '<tr><td>' + item[0]+
                        '</td><td>' + item[1] +
                        '</td></tr>'
                    )
                });


    }
    
};
}