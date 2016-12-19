var client = new XMLHttpRequest();
var user = {
    url: "http://"+config.host+":"+config.port+"/cloud/v0.1",
    username:"",
    email: "",
    api: "",
    session: "",
    query_result: {},
    login: function() {
        var email = document.getElementById("login-email").value;
        var password = document.getElementById("login-password").value;
        console.log(email+" -- "+password)
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("POST", this.url+"/public/user/login");
        var request = { 'email': email, 'password': password }
        xmlhttp.send(JSON.stringify(request));
        xmlhttp.onreadystatechange=function()
        {
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                if(xmlhttp.responseText == ""){
                    console.log("Cloud returned empty response!");
                }else{
                    var response = JSON.parse(xmlhttp.responseText);
                    this.session = response['session']
                    console.log(this.session);
                    
                    window.location.replace("./?session="+this.session);
                }
            } else {
                console.log(xmlhttp.responseText);
                Materialize.toast('<span>'+xmlhttp.responseText+'</span>', 3000);
            }
        }
    },
    register: function() {
        var username = document.getElementById("register-email").value;
        var email = document.getElementById("register-email").value;
        var password = document.getElementById("register-password").value;
        var password_again = document.getElementById("register-password-again").value;
        if(password == password_again){
            console.log(username+" -- "+email+" -- "+password);
            var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
            xmlhttp.open("POST", this.url+"/public/user/register");
            var request = { 'email': email, 'password': password, 'username':username };
            xmlhttp.send(JSON.stringify(request));
            xmlhttp.onreadystatechange=function()
            {
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                     if(xmlhttp.responseText == ""){
                        console.log("Cloud returned empty response!");
                    }else{
                        var response = JSON.parse(xmlhttp.responseText);
                        this.session = response['session'];
                        console.log(this.session);
                        window.location.replace("../?session="+this.session);
                    }
                } else {
                    var response = xmlhttp.responseText;
                    console.log(response);
                    console.log("Registration failed");
                    if(response == ""){
                        Materialize.toast('<span>Register failed: Unknown reason.</span>', 3000);
                    }else{
                        Materialize.toast('<span>Register failed: '+response+'</span>', 3000);
                    }
                }
            }
        }else{
            Materialize.toast('<span>Passwords mismatch.</span>', 3000);
        }  
    },
    add_app: function() {
        var name = document.getElementById("app-name").value;
        var about = document.getElementById("app-about").value;
        if(name != ""){
            console.log(name+" -- "+about);
            var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
            xmlhttp.open("POST", this.url+"/private/"+this.session+"/dashboard/developer/app/create");
            var request = { 'name': name, 'about': about};
            xmlhttp.send(JSON.stringify(request));
            xmlhttp.onreadystatechange=function()
            {
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    var response = xmlhttp.responseText;
                    console.log(response);
                    window.location.replace("../?session="+this.session);

                    // var file = document.getElementById("picture-input");
                    // if (file.files.length > 0) {
                    //     user.upload_file(file, 'picture', 'none');
                    // }else{
                    //     console.log("No picture to change");
                    //     // window.location.replace("../?session="+user.session);
                    //     window.location.reload(); 
                    // }
                    Materialize.toast('<span>Creation succeeded</span>', 3000);
                } else {
                    console.log("Update failed");
                    Materialize.toast('<span>Creation failed</span>', 3000);
                }
            }
        }else{
            Materialize.toast('<span>Name should not be empty.</span>', 3000);
        }  
    },
    logout: function(where) {
        var xmlhttp = new XMLHttpRequest();
        console.log(this.session);
        xmlhttp.open("GET", this.url+"/private/"+this.session+"/user/logout");
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                 if(xmlhttp.responseText == ""){
                    console.log("Cloud returned empty response!");
                }else{
                    if(where != "dashboard"){
                        window.location.replace("./");
                    }else{
                        window.location.replace("../");
                    }
                }
            } else {
                console.log("Logout failed");
                Materialize.toast('<span>Logout failed</span>', 3000);
            }
        }   
    },
    update: function() {
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("POST", this.url+"/private/"+this.session+"/user/update");
        var pwd = document.getElementById('edit-new-password').value;
        var pwd_2 = document.getElementById('edit-new-password-again').value;
        if(pwd != pwd_2){
            console.log("Passwords mismatch");
            Materialize.toast('<span>Passwords mismatch</span>', 3000);
        }else{
            var fname = document.getElementById('view-fname').value;
            var lname = document.getElementById('view-lname').value;
            var org = document.getElementById('view-org').value;
            var about = document.getElementById('view-about').value;
            if(fname == "None"){
                fname = ""
            }
            if(lname == "None"){
                lname = ""
            }
            if(org == "None"){
                org = ""
            }
            if(about == "None"){
                about = ""
            }
            console.log("Fname: "+fname);
            console.log("Lname: "+lname);
            var request = { 'pwd': pwd, 'fname': fname, 'lname': lname, 'org': org, 'about': about }
            xmlhttp.send(JSON.stringify(request));
            xmlhttp.onreadystatechange=function()
            {
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    var response = xmlhttp.responseText;
                    console.log(response);

                    var file = document.getElementById("picture-input");
                    if (file.files.length > 0) {
                        user.upload_file(file, 'picture', 'none');
                    }else{
                        console.log("No picture to change");
                        // window.location.replace("../?session="+user.session);
                        window.location.reload(); 
                    }
                    Materialize.toast('<span>Update succeeded</span>', 3000);
                } else {
                    console.log("Update failed");
                    Materialize.toast('<span>Update failed</span>', 3000);
                }
            }
        }
    },
    upload_file: function(file, group, item_id) {
        console.log("File: "+file.files[0].name);
        var formData = new FormData();
        formData.append("file", file.files[0], file.files[0].name);
        console.log(formData);
        $.ajax({
            url        : this.url+"/private/"+this.session+"/file/upload/"+group+"/"+item_id,
            type       : "POST",
            data       : formData, 
            async      : true,
            cache      : false,
            processData: false,
            contentType: false,
            success    : function(text){
                if(text == ""){
                    console.log("Cloud returned empty response!");
                }else{
                    window.location.replace("../?session="+user.session);
                }
            }
         });
         event.preventDefault();
    },
    recover: function() {
        var email = document.getElementById("recover-email").value;
        console.log(email+" -- recover")
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("POST", this.url+"/public/user/recover");
        var request = { 'email': email}
        xmlhttp.send(JSON.stringify(request));
        xmlhttp.onreadystatechange=function()
        {
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                if(xmlhttp.responseText == ""){
                    console.log("Cloud returned empty response!");
                }else{
                    console.log(xmlhttp.responseText);                
                    Materialize.toast('<span>'+xmlhttp.responseText+'</span>', 3000);
                }
            } else {
                console.log(xmlhttp.responseText);                
                Materialize.toast('<span>'+xmlhttp.responseText+'</span>', 3000);
            }
        }
    },
    trusted: function() {
        var xmlhttp = new XMLHttpRequest();
        console.log(this.session);
        xmlhttp.open("GET", this.url+"/private/"+this.session+"/user/trusted");
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                console.log(xmlhttp.responseText);
                if(xmlhttp.responseText != ""){
                    if(xmlhttp.responseText == ""){
                        console.log("Cloud returned empty response!");
                    }else{
                        var response = JSON.parse(xmlhttp.responseText);
                        var version = response["version"];
                        console.log("Version: "+version);
                        document.getElementById("footer-version").innerHTML = version;
                        // Materialize.toast('<span>Access trusted!</span>', 3000);
                    }
                }
                
            } else {
                window.location.replace("../error/?code=404");
            }
        } 
    },
    account: function() {
        var xmlhttp = new XMLHttpRequest();
        console.log(this.session);
        xmlhttp.open("GET", this.url+"/private/"+this.session+"/user/profile");
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                if(xmlhttp.responseText == ""){
                    console.log("Cloud returned empty response!");
                }else{
                    var response = JSON.parse(xmlhttp.responseText);
                    this.email = response['email'];
                    this.fname = response['fname']
                    this.lname = response['lname'];
                    this.organisation = response['organisation']
                    this.about = response['about']
                    this.api = response['api'];
                    $('#view-username-value').text(this.username);
                    document.getElementById('view-email').value = this.email;
                    document.getElementById('view-api').value = this.api;
                    document.getElementById('view-fname').value = this.fname;
                    document.getElementById('view-lname').value = this.lname;
                    document.getElementById('view-org').value = this.organisation;
                    document.getElementById('view-about').value = this.about;
                    console.log("Account Api: "+this.api);
                }
            } else {
                window.location.replace("../error/?code=404");
            }
        }
    },
    renew: function() {
        var xmlhttp = new XMLHttpRequest();
        console.log(this.session);
        xmlhttp.open("GET", this.url+"/private/"+this.session+"/user/renew");
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                if(xmlhttp.responseText == ""){
                    console.log("Cloud returned empty response!");
                }else{
                    var response = JSON.parse(xmlhttp.responseText);
                    this.api = response['api'];
                    if(this.api.length > 18){
                        $('#view-api-value').text(this.api.substring(0,15)+"...");
                    }else{
                        $('#view-api-value').text(this.api);
                    }
                    Materialize.toast('<span>API Token renewed!</span>', 3000);
                }
            } else {
                window.location.replace("../error/?code=404");
            }
        }
    },
    config: function() {
        window.location.replace(this.url+"/private/"+this.session+"/user/config");
    },
    copy_api: function() {
        console.log("Api: "+this.api);
        console.log("Email: "+this.email);
        console.log("Username: "+this.username);
        console.log("Session: "+this.session);
    }
};

var Space = function (session){
    var url = "http://"+config.host+":"+config.port+"/cloud/v0.1";
    this.session = session;
    this.dash_content = "";
    this.query_result = "";
    this.dashboard = function() {
        var xmlhttp = new XMLHttpRequest();
        console.log(this.session);
        xmlhttp.open("GET", url+"/private/"+this.session+"/dashboard/projects");
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                if(xmlhttp.responseText != ""){
                    var response = JSON.parse(xmlhttp.responseText);
                    this.dash_content = response;
                    document.getElementById("projects-list").innerHTML = "";
                    var version = response["version"];
                    console.log("Version: "+version);
                    for(var i = 0; i < response["projects"].length; i++){
                        project = response["projects"][i];
                        console.log(project);
                        var disable_view = "";
                        if(project["project"]["records"] == 0){
                            disable_view = "disabled";
                        }
                        // add tooltip
                        // update to inputs
                        // Make records clickable
                        // Remove the view button since bottom info will be clickage.
                        // Change the order to: View | Edit | Upload | Remove

                        function succeed(xhttp, params){
                            var content = xhttp.responseText;
                            if(document.getElementById("update-project"+params[1]) == null){
                                // console.log(content);
                                content = content.replace(/session/g, params[0]); 
                                content = content.replace(/project_id/g, params[1]);
                                content = content.replace(/project_name/g, params[2]);
                                content = content.replace(/project_created/g, params[3]);
                                content = content.replace(/project_duration/g, params[4]);
                                content = content.replace(/project_description/g, params[5]);
                                content = content.replace(/project_goals/g, params[6]);
                                content = content.replace(/project_records/g, params[7]);
                                content = content.replace(/project_diffs/g, params[8]);
                                content = content.replace(/project_envs/g, params[9]);
                                // document.getElementById("projects-list").innerHTML += content;
                                // console.log(content);
                            }
                        };
                        function failed(){
                            window.location.replace("/error/?code=404");
                        };

                        var params = [session, project["project"]["id"], project["project"]["name"], project["project"]["created"], project["project"]["duration"], project["project"]["description"], project["project"]["goals"], project["project"]["records"], project["project"]["diffs"], project["project"]["environments"]];
                        config.load_xml('project_content.xml', params, succeed, failed);

                        var content = "<div class='col s12 m6 l4'>";
                        content += "<div id='profile-card' class='card'>";
                        content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
                        content += "<div class='card-content'>";
                        content += "<img src='../images/project.png' alt='' class='circle responsive-img activator card-profile-image'>";
                        content += "<a onclick='projectRemove(\""+project["project"]["name"]+"\",\""+project["project"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-action-delete'></i></a>";
                        content += "<a onclick='Materialize.toast(\"<span>Project record upload not implemented yet!</span>\", 3000);' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled'><i class='mdi-file-cloud-upload'></i></a>";
                        content += "<a onclick='Materialize.toast(\"<span>Project environment upload not implemented yet!</span>\", 3000);' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled'><i class='mdi-maps-layers'></i></a>";
                        content += "<div id='update-project-"+project["project"]["id"]+"'><a id='update-action' onclick='projectEdit(\""+project["project"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-editor-mode-edit'></i></a></div>";
                        // content += "<a href='./?session="+session+"&view=records&project="+project["project"]["id"]+"' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right "+disable_view+"'><i class='mdi-action-visibility'></i></a>";
                        content += "<span class='card-title activator black-text text-darken-4'> "+project["project"]["name"]+"</span>";
                        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+project["project"]["created"]+"</p>";
                        content += "<p><i class='mdi-device-access-alarm cyan-text text-darken-2'></i> "+project["project"]["duration"]+"</p>";
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-turned-in prefix cyan-text text-darken-2'></i><input readonly id='project-tags-"+project["project"]["id"]+"' type='text' value='"+project["project"]["tags"]+"'></div></div>";
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='description'><div class='input-field col s12'><i class='mdi-action-description prefix cyan-text text-darken-2'></i><input readonly id='project-desc-"+project["project"]["id"]+"' type='text' value='"+project["project"]["description"]+"'></div></div>";
                        // content += "<p><i class='mdi-action-description cyan-text text-darken-2'></i> "+project["project"]["description"]+"</p>";
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='goals'><div class='input-field col s12'><i class='mdi-action-subject prefix cyan-text text-darken-2'></i><input readonly id='project-goals-"+project["project"]["id"]+"' type='text' value='"+project["project"]["goals"]+"'></div></div>";
                        // content += "<p><i class='mdi-action-subject cyan-text text-darken-2'></i> "+project["project"]["goals"]+"</p>";
                        content += "<div class='card-action center-align'>";
                        content += "<a href='./?session="+session+"&view=records&project="+project["project"]["id"]+"' class='valign left tooltipped' data-position='bottom' data-delay='50' data-tooltip='records'><i class='mdi-file-cloud-done cyan-text text-darken-2'></i> <span class='records badge'>"+project["project"]["records"]+"</span></a>";
                        content += "<a onclick='Materialize.toast(\"<span>Project diffs view not implemented yet!</span>\", 3000);' class='valign tooltipped' data-position='bottom' data-delay='50' data-tooltip='diffs'><i class='mdi-image-compare cyan-text text-darken-2'></i> <span class='diffs badge'>"+project["project"]["diffs"]+"</span></a>";
                        content += "<a onclick='Materialize.toast(\"<span> Project environments view not implemented yet!</span>\", 3000);' class='valign right tooltipped' data-position='bottom' data-delay='50' data-tooltip='environments'><i class='mdi-maps-layers cyan-text text-darken-2'></i> <span class='containers badge'>"+project["project"]["environments"]+"</span></a>";
                        content += "</div>";
                        content += "</div>";
                        content += "</div>";
                        content += "<div id='project-"+project["project"]["id"]+"-confirm' class='modal'></div>";
                        content += "</div>";
                        document.getElementById("projects-list").innerHTML += content;
                    }
                    document.getElementById("footer-version").innerHTML = version;
                }else{
                    console.log("Cloud returned empty response!");
                }
            } else {
                console.log("Dashboard failed");
            }
        }
    },
    this.apps = function() {
        var xmlhttp = new XMLHttpRequest();
        console.log(this.session);
        xmlhttp.open("GET", url+"/private/"+this.session+"/dashboard/developer/apps");
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                if(xmlhttp.responseText != ""){
                    var response = JSON.parse(xmlhttp.responseText);
                    this.dash_content = response;
                    document.getElementById("apps-list").innerHTML = "";
                    var version = response["version"];
                    console.log("Version: "+version);
                    for(var i = 0; i < response["content"]["apps"].length; i++){
                        app = response["content"]["apps"][i];
                        console.log(app);
                        var disable_view = "";
                        function succeed(xhttp, params){
                            var content = xhttp.responseText;
                            if(document.getElementById("update-app"+params[1]) == null){
                                // console.log(content);
                                content = content.replace(/session/g, params[0]); 
                                content = content.replace(/app_id/g, params[1]);
                                content = content.replace(/app_name/g, params[2]);
                                content = content.replace(/app_created/g, params[3]);
                                content = content.replace(/app_network/g, params[4]);
                                content = content.replace(/app_access/g, params[5]);
                                content = content.replace(/app_storage/g, params[6]);
                                content = content.replace(/app_token/g, params[7]);
                                content = content.replace(/app_about/g, params[8]);
                                // document.getElementById("apps-list").innerHTML += content;
                            }
                        };
                        function failed(){
                            window.location.replace("/error/?code=404");
                        };

                        var params = [session, app["id"], app["name"], app["created"], app["network"], app["access"], app["storage"], app["token"], app["about"]];
                        config.load_xml('app_content.xml', params, succeed, failed);

                        var content = "<div class='col s12 m6 l4'>";
                        content += "<div id='profile-card' class='card'>";
                        content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
                        content += "<div class='card-content'>";
                        content += "<img src='../images/gearsIcon.png' alt='' class='circle responsive-img activator card-profile-image'>";
                        content += "<a onclick='appRemove(\""+app["name"]+"\",\""+app["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-action-delete'></i></a>";
                        content += "<a onclick='Materialize.toast(\"<span>Application upload not implemented yet!</span>\", 3000);' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled'><i class='mdi-file-cloud-upload'></i></a>";
                        content += "<a onclick='Materialize.toast(\"<span>Application download not implemented yet!</span>\", 3000);' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled'><i class='mdi-file-cloud-download'></i></a>";
                        content += "<div id='update-app-"+app["id"]+"'><a id='update-action' onclick='appEdit(\""+app["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-editor-mode-edit'></i></a></div>";
                        // content += "<a href='./?session="+session+"&view=records&project="+project["project"]["id"]+"' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right "+disable_view+"'><i class='mdi-action-visibility'></i></a>";
                        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+app["created"]+"</p>";
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-turned-in prefix cyan-text text-darken-2'></i><input readonly id='app-name-"+app["id"]+"' type='text' value='"+app["name"]+"'></div></div>";
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-settings-ethernet prefix cyan-text text-darken-2'></i><input readonly id='app-network-"+app["id"]+"' type='text' value='"+app["network"]+"'></div></div>";
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-lock prefix cyan-text text-darken-2'></i><input readonly id='app-access-"+app["id"]+"' type='text' value='"+app["access"]+"'></div></div>";
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='description'><div class='input-field col s12'><i class='mdi-communication-vpn-key prefix cyan-text text-darken-2'></i><input readonly id='app-token-"+app["id"]+"' type='text' value='"+app["token"]+"'></div></div>";
                        // content += "<p><i class='mdi-action-description cyan-text text-darken-2'></i> "+project["project"]["description"]+"</p>";
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='goals'><div class='input-field col s12'><i class='mdi-action-subject prefix cyan-text text-darken-2'></i><textarea readonly class='materialize-textarea' id='app-about-"+app["id"]+"' type='text' value='"+app["about"]+"'>"+app["about"]+"</textarea></div></div>";
                        // content += "<p><i class='mdi-action-subject cyan-text text-darken-2'></i> "+project["project"]["goals"]+"</p>";
                        content += "<div class='card-action center-align'>";
                        content += "<a href='./?session="+session+"&view=users&app="+app["id"]+"' class='valign left tooltipped' data-position='bottom' data-delay='50' data-tooltip='users'><i class='mdi-social-group-add cyan-text text-darken-2'></i> <span class='users badge'>"+app["users"]+"</span></a>";
                        content += "<a onclick='Materialize.toast(\"<span>Application projects view not implemented yet!</span>\", 3000);' class='valign tooltipped' data-position='bottom' data-delay='50' data-tooltip='projects'><i class='mdi-file-folder cyan-text text-darken-2'></i> <span class='projects badge'>"+app["projects"]+"</span></a>";
                        content += "<a onclick='Materialize.toast(\"<span> Application records view not implemented yet!</span>\", 3000);' class='valign right tooltipped' data-position='bottom' data-delay='50' data-tooltip='records'><i class='mdi-file-cloud-upload cyan-text text-darken-2'></i> <span class='records badge'>"+app["records"]+"</span></a>";
                        content += "</div>";
                        content += "</div>";
                        content += "</div>";
                        content += "<div id='app-"+app["id"]+"-confirm' class='modal'></div>";
                        content += "</div>";
                        document.getElementById("apps-list").innerHTML += content;
                    }
                    document.getElementById("footer-version").innerHTML = version;
                }else{
                    console.log("Cloud returned empty response!");
                }
            } else {
                console.log("Dashboard failed");
            }
        }
    },
    this.records = function(project_id) {
        document.getElementById("records-list").innerHTML = "<div class='progress'><div class='indeterminate'></div></div>";
        document.getElementById("temporal-slider").innerHTML = "";
        var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
        console.log("Project id: "+project_id);
        if(project_id == "all"){
            xmlhttp.open("GET", url+"/private/"+this.session+"/dashboard/records/all");
        }else{
            xmlhttp.open("GET", url+"/private/"+this.session+"/dashboard/records/"+project_id);
        }
        console.log(this.session);
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                if(xmlhttp.responseText == ""){
                    console.log("Cloud returned empty response!");
                }else{
                    var response = JSON.parse(xmlhttp.responseText);
                    document.getElementById("records-list").innerHTML = "";
                    this.dash_content = response;
                    
                    for(var i = 0; i < response["records"].length; i++){
                        record = response["records"][i];
                        console.log(record);
                        var content = "<div class='col s12 m6 l4' id='"+record["head"]["id"]+"'> ";
                        content += "<div id='profile-card' class='card'>";
                        content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
                        content += "<div class='card-content'>";
                        var disable_download = "";
                        if(record["container"] == false){
                            disable_download = "disabled";
                        }
                        content += "<img src='../images/record.png' alt='' class='circle responsive-img activator card-profile-image'>";
                        content += "<a onclick='recordRemove(\""+record["head"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-action-delete'></i></a>";
                        content += "<a onclick=\"space.pull('"+record["head"]["project"]+"','"+record["head"]["id"]+"')\" class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right "+disable_download+"'><i class='mdi-file-cloud-download tooltipped' data-position='top' data-delay='50' data-tooltip='download'></i></a>";
                        content += "<div id='update-record-"+record["head"]["id"]+"'><a id='update-action' onclick='recordEdit(\""+record["head"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-editor-mode-edit'></i></a></div>";
                        content += "<span class='card-title activator grey-text text-darken-4'>"+record["head"]["id"]+"</span>";
                        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+record["head"]["created"]+"</p>";
                        if(project_id == "all"){
                            content += "<p class='grey-text ultra-small'><i class='mdi-file-folder cyan-text text-darken-2'></i> "+record["head"]["project-name"]+"</p>";
                        }
                        content += "<p><i class='mdi-device-access-alarm cyan-text text-darken-2'></i> "+record["head"]["updated"]+"</p>";
                        content += "<div class='row margin'><div class='input-field col s12'><i class='mdi-action-turned-in prefix cyan-text text-darken-2'></i><input readonly id='record-tags-"+record["head"]["id"]+"' type='text' value='"+record["head"]["tags"]+"'></div></div>";
                        content += "<div class='row margin'><div class='input-field col s12'><i class='mdi-notification-event-note prefix cyan-text text-darken-2'></i><input readonly id='record-rationels-"+record["head"]["id"]+"' type='text' value='"+record["head"]["rationels"]+"'></div></div>";
                        content += "<p><i class='mdi-notification-sync cyan-text text-darken-2'></i> "+record["head"]["status"]+"</p>";
                        content += "<div class='card-action center-align'>";
                        content += "<a onclick='Materialize.toast(\"<span>Record inputs view not implemented yet!</span>\", 3000);' class='valign left'><i class='mdi-communication-call-received cyan-text text-darken-2'></i> <span class='inputs badge'>"+record["head"]["inputs"]+"</span></a>";
                        content += "<a onclick='Materialize.toast(\"<span>Record outputs view not implemented yet!</span>\", 3000);' class='valign'><i class='mdi-communication-call-made cyan-text text-darken-2'></i> <span class='outputs badge'>"+record["head"]["outputs"]+"</span></a>";
                        content += "<a onclick='Materialize.toast(\"<span>Record dependencies view not implemented yet!</span>\", 3000);' class='valign right'><i class='mdi-editor-insert-link cyan-text text-darken-2'></i> <span class='dependencies badge'>"+record["head"]["dependencies"]+"</span></a>";
                        content += "</div>";
                        content += "</div>";                
                        content += "</div>";
                        content += "</div>";
                        document.getElementById("records-list").innerHTML += content;
                    }
                }
            } else {
                console.log("Dashboard failed");
            }
        }
    },
    this.query = function(search, exUser, exApp, exProject, exRecord) {
        var xmlhttp = new XMLHttpRequest();
        var query_result = document.getElementById('query-result');
        query_result.innerHTML = "<div class='progress'><div class='indeterminate'></div></div>";
        console.log(this.session);
        xmlhttp.open("GET", url+"/private/"+this.session+"/dashboard/search?query="+search);
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            var query_result = document.getElementById('query-result');
            query_result.innerHTML = "";
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                if(xmlhttp.responseText == ""){
                    console.log("Cloud returned empty response!");
                }else{
                    var response = JSON.parse(xmlhttp.responseText);
                    this.query_result = response;
                    console.log(this.query_result);
                    var hits = 0;
                    if(!exUser == true){
                        for(var i = 0; i < this.query_result["users"]["count"]; i++){
                            var user_content = renderer.user(this.query_result["users"]["result"][i], false);
                            query_result.innerHTML += user_content;
                        }
                        hits += this.query_result["users"]["count"];
                    }
                    if(!exApp == true){
                        for(var i = 0; i < this.query_result["applications"]["count"]; i++){
                            var app_content = renderer.application(this.query_result["applications"]["result"][i], false);
                            query_result.innerHTML += app_content;
                        }
                        hits += this.query_result["applications"]["count"];
                    }
                    if(!exProject == true){
                        for(var i = 0; i < this.query_result["projects"]["count"]; i++){
                            var project_content = renderer.project(this.query_result["projects"]["result"][i], false);
                            query_result.innerHTML += project_content;
                        }
                        hits += this.query_result["projects"]["count"];
                    }
                    if(!exRecord == true){
                        for(var i = 0; i < this.query_result["records"]["count"]; i++){
                            var record_content = renderer.record(this.query_result["records"]["result"][i], false);
                            query_result.innerHTML += record_content;
                        }
                        hits += this.query_result["records"]["count"];
                    }
                    var display = document.getElementById('results-display');
                    display.innerHTML = hits;
                }
            } else {
                console.log("query failed");
                Materialize.toast('<span>Query failed</span>', 3000);
            }
        }   
    },
    this.exportToJson = function () {
        var xmlhttp = new XMLHttpRequest();
        console.log(this.session);
        xmlhttp.open("GET", url+"/private/"+this.session+"/dashboard/projects");
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                if(xmlhttp.responseText == ""){
                    console.log("Cloud returned empty response!");
                }else{
                    var pom = document.createElement('a');
                    pom.setAttribute('href', 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(JSON.parse(xmlhttp.responseText), null, 2)));
                    pom.setAttribute('download', 'dashboard.json');

                    if (document.createEvent) {
                        var event = document.createEvent('MouseEvents');
                        event.initEvent('click', true, true);
                        pom.dispatchEvent(event);
                    }
                    else {
                        pom.click();
                    }
                }
            } else {
                console.log("Dashboard download failed");
            }
        }
    },
    this.pull = function(project_name, record_id) {
        console.log("Before...");
        window.location.replace(url+"/private/"+this.session+"/record/pull"+"/"+record_id);
        console.log("...After");
    }
};

var Record = function (session, _id){
    var url = "http://"+config.host+":"+config.port+"/cloud/v0.1";
    this.session = session;
    self._id = _id;
    // This way of doing is not optimal as we do not atomically update a record and change its content we reload the whole page.
    this.save = function(tags, rationels) {
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("POST", url+"/private/"+this.session+"/record/edit/"+self._id);
        // console.log("Tags: "+cache['tags']);
        // console.log("Rationels: "+cache['rationels']);
        var request = { 'tags': tags, 'rationels': rationels};
        xmlhttp.send(JSON.stringify(request));
        xmlhttp.onreadystatechange=function()
        {
            if(xmlhttp.responseText == ""){
                console.log("Cloud returned empty response!");
            }else{
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    Materialize.toast('<span>Update succeeded</span>', 3000);
                } else {
                    // tags.value = cache['tags'];
                    // rationels.value = cache['rationels'];
                    Materialize.toast('<span>Update failed</span>', 5000);
                }
                window.location.reload();
            }
        }
    },
    // Half way optimal. We could have just removed the record div instead of reloading the whole page. TODO
    this.trash = function () {
        var xmlhttp = new XMLHttpRequest();
        console.log(this.session);
        xmlhttp.open("DELETE", url+"/private/"+this.session+"/record/remove/"+self._id);
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if(xmlhttp.responseText == ""){
                console.log("Cloud returned empty response!");
            }else{
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    Materialize.toast('<span>Record removal succeeded</span>', 3000);
                    window.location.reload();
                } else {
                    Materialize.toast('<span>Record removal failed</span>', 3000);
                    console.log("Dashboard download failed");
                }
            }
        }
    }
};

var Project = function (session, _id){
    var url = "http://"+config.host+":"+config.port+"/cloud/v0.1";
    this.session = session;
    self._id = _id;
    // This way of doing is not optimal as we do not atomically update a record and change its content we reload the whole page.
    this.save = function(tags, description, goals) {
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("POST", url+"/private/"+this.session+"/project/edit/"+self._id);
        // console.log("Tags: "+cache['tags']);
        // console.log("Rationels: "+cache['rationels']);
        var request = { 'tags':tags, 'description': description, 'goals': goals};
        xmlhttp.send(JSON.stringify(request));
        xmlhttp.onreadystatechange=function()
        {
            if(xmlhttp.responseText == ""){
                console.log("Cloud returned empty response!");
            }else{
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    Materialize.toast('<span>Update succeeded</span>', 3000);
                } else {
                    // tags.value = cache['tags'];
                    // rationels.value = cache['rationels'];
                    Materialize.toast('<span>Update failed</span>', 5000);
                }
                window.location.reload();
            }
        }
    },
    // Half way optimal. We could have just removed the record div instead of reloading the whole page. TODO
    this.trash = function () {
        var xmlhttp = new XMLHttpRequest();
        console.log(this.session);
        
        xmlhttp.open("DELETE", url+"/private/"+this.session+"/project/remove/"+self._id);
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if(xmlhttp.responseText == ""){
                console.log("Cloud returned empty response!");
            }else{
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    Materialize.toast('<span>Record removal succeeded</span>', 3000);
                    window.location.reload();
                } else {
                    Materialize.toast('<span>Record removal failed</span>', 3000);
                    console.log("Dashboard download failed");
                }
            }
        }
    }
};