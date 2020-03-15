
var ip = location.host;
console.log(ip);

var socket= new WebSocket("ws://" + ip + "/api/ws");

var sendJson = {
    action: "get_cookies",
    data: '*'
}

x = ""

socket.onmessage = function (e) {
	json = JSON.parse(e.data);
	
    if(json.action == 'connect'){
    	socket.send(JSON.stringify(sendJson));
    }

    if(json.Response){
    	for (i in json.Response.cookies) {
 			session = json.Response.cookies[i];
 			sendJson = {
    			action: "get_cookie",
    			data: session
			}
			socket.send(JSON.stringify(sendJson));
		}
    }

    if(json.Response.session){
    	$("#redis-session").html(e.data);
    }
    
};







