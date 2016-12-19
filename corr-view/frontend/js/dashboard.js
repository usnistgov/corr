var dashboard = {
	content: document.getElementById("dashboard-content"),
    coming_soon:function(){
        function succeed(xhttp){
            dashboard.content.innerHTML = xhttp.responseText;
            user.session = session;
            console.log(user.session);
            user.trusted();
        };
        function failed(){
            window.location.replace("/error/?code=404");
        };
        config.load_xml('coming_soon.xml', [], succeed, failed);
    },
	activity:function(session){
        function succeed(xhttp){
            dashboard.content.innerHTML = xhttp.responseText;
            user.session = session;
            console.log(user.session);
            user.trusted();

            var space = new Space(user.session);
            space.dashboard();

        };
        function failed(){
            console.log(window.location.host);
            window.location.replace("/error/?code=404");
        };
        config.load_xml('dashboard_activity.xml', [], succeed, failed);
	},
	apps:function(session){
        function succeed(xhttp){
            dashboard.content.innerHTML = xhttp.responseText;
            user.session = session;
            console.log(user.session);
            user.trusted();

            var space = new Space(user.session);
            space.apps();

        };
        function failed(){
            console.log(window.location.host);
            window.location.replace("/error/?code=404");
        };
        config.load_xml('dashboard_applications.xml', [], succeed, failed);
	},
	projects:function(session){
        function succeed(xhttp){
            dashboard.content.innerHTML = xhttp.responseText;
            user.session = session;
            console.log(user.session);
            user.trusted();

            var space = new Space(user.session);
            space.dashboard();
        };
        function failed(){
            window.location.replace("/error/?code=404");
        };
        config.load_xml('dashboard_projects.xml', [], succeed, failed);
	},
	records:function(session, options){
        function succeed(xhttp){
            dashboard.content.innerHTML = xhttp.responseText;
            user.session = session;
            console.log(user.session);
            user.trusted();

            var project = "all";
            for(var i=0;i<options.length;i++){
                var parts = options[i].split("=");
                if(parts[0] == "project"){
                    project = parts[1];
                }
            }
            var space = new Space(user.session);
            space.records(project);
        };
        function failed(){
            window.location.replace("/error/?code=404");
        };
        config.load_xml('dashboard_records.xml', [], succeed, failed);
	},
	diffs:function(session, options){
		this.coming_soon();
	},
	query:function(session, options){
        function succeed(xhttp){
		    dashboard.content.innerHTML = xhttp.responseText;
            user.session = session;
            console.log(user.session);
            user.trusted();

            var space = new Space(user.session);
            // space.search();

        };
        function failed(){
            console.log(window.location.host);
            window.location.replace("/error/?code=404");
        };
        config.load_xml('dashboard_query.xml', [], succeed, failed);
	}
}