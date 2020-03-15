function isEmptyObject(obj) {
    for (var i in obj) {
        if (obj.hasOwnProperty(i)) {
            return false;
        }
    }
    return true;
}

function register(){
{
        
        var username = document.getElementById("input-username").value;
        var password = document.getElementById("input-password").value;

          $.ajax({
    url: '/api/register',
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
            $(location).attr('href', '/')
        //alertify.success(json['User']['username']);
        }

    },
    error: function( jqXhr, textStatus, errorThrown ){
        console.log( errorThrown );
    }


});
}
}
