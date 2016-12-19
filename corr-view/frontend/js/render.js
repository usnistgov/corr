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
    },
    application: function(object, ownership, layout){
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
    },
    project: function(object, ownership, layout){
        console.log("Hello from project.");
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
    },
    record: function(object, ownership, layout){
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