var renderer = {
    user: function(object, ownership, layout){
        $.ajax({
            url : "/xml/"+xml_location,
            type: 'GET',
            success: function(result,status,xhr) {
                succeed(xhr, params);
            },
            error: function(xhr,status,error) {
                failed();
            }
        });
    }
}