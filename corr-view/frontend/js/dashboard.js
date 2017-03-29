var dashboard = {
	content: document.getElementById("dashboard-content"),
    coming_soon:function(){
        function succeed(xhttp){
            dashboard.content.innerHTML = xhttp.responseText;
            console.log('Cookie session value: '+ Cookies.get('session'));
            // user.session = session;
            // console.log(user.session);
            user.trusted();
            console.log("group:" + user.group);
        };
        function failed(){
            window.location.replace("/error/?code=404");
        };
        config.load_xml('coming_soon.xml', [], succeed, failed);
    },
	activity:function(){
        function succeed(xhttp){
            dashboard.content.innerHTML = xhttp.responseText;
            console.log('Cookie session value: '+ Cookies.get('session'));
            // user.session = session;
            // console.log(user.session);
            user.trusted();
            console.log("group:" + user.group);

            var space = new Space();
            space.dashboard();

        };
        function failed(){
            console.log(window.location.host);
            window.location.replace("/error/?code=404");
        };
        config.load_xml('dashboard_activity.xml', [], succeed, failed);
    },
	apps:function(){
        function succeed(xhttp){
            dashboard.content.innerHTML = xhttp.responseText;
            console.log('Cookie session value: '+ Cookies.get('session'));
            // user.session = session;
            // console.log(user.session);
            user.trusted();

            var space = new Space();
            space.apps();

        };
        function failed(){
            console.log(window.location.host);
            window.location.replace("/error/?code=404");
        };
        config.load_xml('dashboard_applications.xml', [], succeed, failed);
    },
	projects:function(){
        function succeed(xhttp){
            dashboard.content.innerHTML = xhttp.responseText;
            console.log('Cookie session value: '+ Cookies.get('session'));
            // user.session = session;
            // console.log(user.session);
            user.trusted();

            var space = new Space();
            space.dashboard();
        };
        function failed(){
            window.location.replace("/error/?code=404");
        };
        config.load_xml('dashboard_projects.xml', [], succeed, failed);
    },
	records:function(options){
        function succeed(xhttp){
            dashboard.content.innerHTML = xhttp.responseText;
            console.log('Cookie session value: '+ Cookies.get('session'));
            // user.session = session;
            // console.log(user.session);
            user.trusted();

            var project = "all";
            for(var i=0;i<options.length;i++){
                var parts = options[i].split("=");
                if(parts[0] == "project"){
                    project = parts[1];
                }
            }
            var space = new Space();
            space.records(project);
        };
        function failed(){
            window.location.replace("/error/?code=404");
        };
        config.load_xml('dashboard_records.xml', [], succeed, failed);
    },
	diffs:function(options){
		function succeed(xhttp){
            dashboard.content.innerHTML = xhttp.responseText;
            console.log('Cookie session value: '+ Cookies.get('session'));
            // user.session = session;
            // console.log(user.session);
            user.trusted();

            var project = "all";
            for(var i=0;i<options.length;i++){
                var parts = options[i].split("=");
                if(parts[0] == "project"){
                    project = parts[1];
                }
            }

            var space = new Space();
            space.diffs(project);
        };
        function failed(){
            window.location.replace("/error/?code=404");
        };
        config.load_xml('dashboard_diffs.xml', [], succeed, failed);
    },
    envs:function(options){
        function succeed(xhttp){
            dashboard.content.innerHTML = xhttp.responseText;
            console.log('Cookie session value: '+ Cookies.get('session'));
            // user.session = session;
            // console.log(user.session);
            user.trusted();

            var project = "all";
            for(var i=0;i<options.length;i++){
                var parts = options[i].split("=");
                if(parts[0] == "project"){
                    project = parts[1];
                }
            }

            var space = new Space();
            space.envs(project);
        };
        function failed(){
            window.location.replace("/error/?code=404");
        };
        config.load_xml('dashboard_envs.xml', [], succeed, failed);
    },
	query:function(options){
        function succeed(xhttp){
            dashboard.content.innerHTML = xhttp.responseText;
            console.log('Cookie session value: '+ Cookies.get('session'));
            // user.session = session;
            // console.log(user.session);
            user.trusted();

            var space = new Space();
            // space.search();

        };
        function failed(){
            console.log(window.location.host);
            window.location.replace("/error/?code=404");
        };
        config.load_xml('dashboard_query.xml', [], succeed, failed);
    }
}