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