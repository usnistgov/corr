var client = new XMLHttpRequest();
var user = {
    url: config.mode+"://"+config.host+":"+config.port+"/cloud/v0.1",
    username:"",
    email: "",
    api: "",
    group:"unknown",
    // session: "",
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
                    // this.session = response['session']
                    // console.log(this.session);
                    Cookies.set('session', response['session'], { path: '' });
                    console.log('Cookie session value: '+ Cookies.get('session'));
                    Cookies.set('group', response['group'], { path: '' });
                    console.log('Cookie group value: '+ Cookies.get('grup'));
                    
                    // window.location.replace("./?session="+this.session);
                    window.location.reload();
                }
            } else {
                console.log(xmlhttp.responseText);
                config.error_modal('An error occured during login.', xmlhttp.responseText);
                // Materialize.toast('<span>'+xmlhttp.responseText+'</span>', 3000);
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
                        // var response = JSON.parse(xmlhttp.responseText);
                        // this.session = response['session'];
                        // console.log(this.session);
                        // Cookies.set('session', response['session'], { path: '' });
                        // console.log('Cookie session value: '+ Cookies.get('session'));
                        // window.location.replace("../?session="+this.session);
                        config.error_modal('Register successfull', xmlhttp.responseText);
                        // window.location.reload();
                    }
                } else {
                    var response = xmlhttp.responseText;
                    console.log(response);
                    console.log("Registration failed");
                    if(response == ""){
                        config.error_modal('Register failed', 'Unknown reason');
                        // Materialize.toast('<span>Register failed: Unknown reason.</span>', 3000);
                    }else{
                        config.error_modal('Register failed', response);
                        // Materialize.toast('<span>Register failed: '+response+'</span>', 3000);
                    }
                }
            }
        }else{
            config.error_modal('Register failed', 'Passwords mismatch');
            // Materialize.toast('<span>Passwords mismatch.</span>', 3000);
        }  
    },
    logout: function(where) {
        var xmlhttp = new XMLHttpRequest();
        console.log('Cookie session value: '+ Cookies.get('session'));
        // console.log(this.session);
        xmlhttp.open("GET", this.url+"/private/user/logout");
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                 if(xmlhttp.responseText == ""){
                    console.log("Cloud returned empty response!");
                }else{
                    if(where != "dashboard"){
                        // Cookies.set('session', 'undefined', { path: '' });
                        Cookies.remove('session');
                        Cookies.remove('group');
                        window.location.replace("./");
                    }else{
                        Cookies.remove('session');
                        Cookies.remove('group');
                        // Cookies.set('session', 'undefined', { path: '/' });
                        window.location.replace("../");
                    }
                }
            } else {
                console.log("Logout failed");
                config.error_modal('Logout failed', xmlhttp.responseText);
                // Materialize.toast('<span>Logout failed</span>', 3000);
            }
        }   
    },
    update: function() {
        var xmlhttp = new XMLHttpRequest();
        console.log('Cookie session value: '+ Cookies.get('session'));
        xmlhttp.open("POST", this.url+"/private/user/update");
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        var pwd = document.getElementById('edit-new-password').value;
        var pwd_2 = document.getElementById('edit-new-password-again').value;
        if(pwd != pwd_2){
            console.log("Passwords mismatch");
            // Materialize.toast('<span>Passwords mismatch</span>', 3000);
            config.error_modal('Passwords mismatch','Must provide identical passwords.');
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
            $('#account-update-modal').closeModal();
            $('#loading-modal').openModal();
            var request = { 'pwd': pwd, 'fname': fname, 'lname': lname, 'org': org, 'about': about }
            xmlhttp.send(JSON.stringify(request));
            xmlhttp.onreadystatechange=function()
            {
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    var response = xmlhttp.responseText;
                    console.log(response);

                    var file = document.getElementById("picture-input");
                    console.log(file);
                    if (file.files.length > 0) {
                        user.upload_file(file, 'picture', 'none');
                    }else{
                        console.log("No picture to change");
                        // window.location.reload(); 
                        $('#loading-modal').closeModal();
                    }
                    // Materialize.toast('<span>Update succeeded</span>', 3000);
                } else {
                    console.log("Update failed");
                    config.error_modal('Update failed', response);
                    $('#loading-modal').closeModal();
                    // Materialize.toast('<span>Update failed</span>', 3000);
                }
            }
        }
    },
    upload_file: function(file, group, item_id) {
        console.log("File: "+file.files[0].name);
        var formData = new FormData();
        formData.append("file", file.files[0], file.files[0].name);
        console.log(formData);
        console.log('Cookie session value: '+ Cookies.get('session'));
        var url_temp = this.url;
        
        
        var blobSlice = File.prototype.slice || File.prototype.mozSlice || File.prototype.webkitSlice,
            _file = file.files[0],
            chunkSize = 2097152,                             // Read in chunks of 2MB
            chunks = Math.ceil(_file.size / chunkSize),
            currentChunk = 0,
            spark = new SparkMD5.ArrayBuffer(),
            fileReader = new FileReader();

        fileReader.onload = function (e) {
            console.log('read chunk nr', currentChunk + 1, 'of', chunks);
            spark.append(e.target.result);                   // Append array buffer
            currentChunk++;

            if (currentChunk < chunks) {
                loadNext();
            } else {
                console.log('finished loading');
                $.ajax({
                    url        : url_temp+"/private/file/upload/"+group+"/"+item_id+"?checksum="+spark.end(),
                    type       : "POST",
                    data       : formData, 
                    async      : true,
                    cache      : false,
                    processData: false,
                    contentType: false,
                    beforeSend: function (xhr) {
                        xhr.setRequestHeader ("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
                    },
                    success    : function(text){
                        if(text == ""){
                            console.log("Cloud returned empty response!");
                        }else{
                            // window.location.replace("../?session="+user.session);
                            // window.location.reload();
                            if(group=="picture"){
                                document.getElementById('account-user-picture').src = config.mode+"://"+config.host+":"+config.port+"/cloud/v0.1/private/"+Cookies.get('session')+"/user/picture?t=" + new Date().getTime();
                                document.getElementById('update-user-picture').src = config.mode+"://"+config.host+":"+config.port+"/cloud/v0.1/private/"+Cookies.get('session')+"/user/picture?t=" + new Date().getTime();
                                document.getElementById('profile-user-picture').src = config.mode+"://"+config.host+":"+config.port+"/cloud/v0.1/private/"+Cookies.get('session')+"/user/picture?t=" + new Date().getTime();
                            }
                            $('#loading-modal').closeModal();
                        }
                    }
                 });
            }
        };

        fileReader.onerror = function () {
            config.error_modal('oops', 'something went wrong.');
        };

        function loadNext() {
            var start = currentChunk * chunkSize,
                end = ((start + chunkSize) >= _file.size) ? _file.size : start + chunkSize;

            fileReader.readAsArrayBuffer(blobSlice.call(_file, start, end));
        }

        loadNext();
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
                    // Materialize.toast('<span>'+xmlhttp.responseText+'</span>', 3000);
                }
            } else {
                console.log(xmlhttp.responseText);     
                config.error_modal('Recover failed', xmlhttp.responseText);           
                // Materialize.toast('<span>'+xmlhttp.responseText+'</span>', 3000);
            }
        }
    },
    trusted: function() {
        var xmlhttp = new XMLHttpRequest();
        console.log('Cookie session value: '+ Cookies.get('session'));
        // console.log(this.session);
        xmlhttp.open("GET", this.url+"/private/user/trusted");
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
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
                    }
                }
                
            } else if(xmlhttp.status == 401){
                console.log(xmlhttp.responseText);
                Cookies.remove('session');
                Cookies.remove('group');
                // Cookies.set('session', 'none', { path: '' });
                // Cookies.set('session', 'none', { path: '/' });
            }else {
                window.location.replace("../error/?code=404");
            }
        } 
    },
    account: function() {
        var xmlhttp = new XMLHttpRequest();
        console.log('Cookie session value: '+ Cookies.get('session'));
        // console.log(this.session);
        xmlhttp.open("GET", this.url+"/private/user/profile");
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
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
        console.log('Cookie session value: '+ Cookies.get('session'));
        // console.log(this.session);
        xmlhttp.open("GET", this.url+"/private/user/renew");
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
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
                    // Materialize.toast('<span>API Token renewed!</span>', 3000);
                }
            } else {
                config.error_modal('Revew API token failed', xmlhttp.responseText);
                // window.location.replace("../error/?code=404");
            }
        }
    },
    config: function() {
        console.log('Cookie session value: '+ Cookies.get('session'));
        window.location.replace(this.url+"/private/"+Cookies.get('session')+"/user/config");
    },
    copy_api: function() {
        console.log('Cookie session value: '+ Cookies.get('session'));
        console.log("Api: "+this.api);
        console.log("Email: "+this.email);
        console.log("Username: "+this.username);
        console.log("Session: "+Cookies.get('session'));
    },
    add_app: function() {
        var name = document.getElementById("app-name").value;
        var about = document.getElementById("app-about").value;
        var access = document.getElementById("app-access").value;
        if(name != ""){
            console.log(name+" -- "+about);
            var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
            console.log('Cookie session value: '+ Cookies.get('session'));
            xmlhttp.open("POST", this.url+"/private/dashboard/developer/app/create");
            xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
            var request = { 'name': name, 'about': about, 'access': access};
            xmlhttp.send(JSON.stringify(request));
            xmlhttp.onreadystatechange=function()
            {
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    if(xmlhttp.responseText == ""){
                        console.log("Cloud returned empty response!");
                    }else{
                        var response = JSON.parse(xmlhttp.responseText);
                        console.log(response);

                        // Materialize.toast('<span>Creation succeeded</span>', 3000);
                        // window.location.reload();
                        var app = response['content'];
                        var app_block_check = document.getElementById("app-block-"+app["id"]);
                        if(app_block_check == undefined || app_block_check == null){
                            var content = "<div class='col s12 m6 l4' id='app-block-"+app["id"]+"'>";
                            content += "<div id='profile-card' class='card'>";
                            content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
                            content += "<div class='card-content'>";
                            content += "<img src='../images/gearsIcon.png' alt='' class='circle responsive-img activator card-profile-image'>";
                            if(Cookies.get('group') == "admin"){
                                content += "<a onclick='appRemove(\""+app["name"]+"\",\""+app["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='delete'><i class='mdi-action-delete'></i></a>";
                            }
                            content += "<a onclick='config.error_modal(\"Application downoload failed\", \"Application download not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='download'><i class='mdi-file-cloud-download'></i></a>";
                            if(Cookies.get('group') == "admin"){
                                content += "<div id='update-app-"+app["id"]+"'><a id='update-action' onclick='appEdit(\""+app["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='edit'><i class='mdi-editor-mode-edit'></i></a></div>";
                            }
                            content += "<a onclick='config.error_modal(\"Application details failed\", \"Application details not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='details'><i class='mdi-action-visibility'></i></a>";

                            content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+app["created"]+"</p>";
                            content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-turned-in prefix cyan-text text-darken-2'></i><input readonly id='app-name-"+app["id"]+"' type='text' value='"+app["name"]+"'></div></div>";
                            // content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-settings-ethernet prefix cyan-text text-darken-2'></i><input readonly id='app-network-"+app["id"]+"' type='text' value='"+app["network"]+"'></div></div>";
                            var access_select = [];
                            access_select.push("<div class='row margin'><div class='input-field col s12'><i class='mdi-action-lock prefix cyan-text text-darken-2'></i><select id='app-access-"+app["id"]+"'>");
                            access_select.push("<option value='activated' disabled>Choose access</option>");
                            access_select.push("<option value='blocked'>Blocked</option>");
                            access_select.push("<option value='deactivated'>Deactivated</option>");
                            access_select.push("</select></div></div>");
                            if(app["access"] == "activated"){
                                access_select[1] = "<option value='activated' disabled selected>Choose access</option>";
                            }else if(app["access"] == "blocked"){
                                access_select[2] = "<option value='blocked' selected>Blocked</option>";
                            }else if(app["access"] == "deactivated"){
                                access_select[3] = "<option value='deactivated' selected>Deactivated</option>";
                            }
                            
                            for(var j = 0; j < access_select.length; j++){
                                // content += access_select[j];
                            }

                            content += "<div class='row margin'><div class='input-field col s12'><i class='mdi-action-lock prefix cyan-text text-darken-2'></i><input readonly placeholder='activated,blocked,deactivated' id='app-access-"+app["id"]+"' type='text' value='"+app["access"]+"'></div></div>";
                            // if(Cookies.get('group') == "admin"){
                            content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='description'><div class='input-field col s12'><i class='mdi-communication-vpn-key prefix cyan-text text-darken-2'></i><input readonly id='app-token-"+app["id"]+"' type='text' value='"+app["token"]+"'></div></div>";
                            // }
                            content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='goals'><div class='input-field col s12'><i class='mdi-action-subject prefix cyan-text text-darken-2'></i><textarea readonly class='materialize-textarea' id='app-about-"+app["id"]+"' type='text' value='"+app["about"]+"'>"+app["about"]+"</textarea></div></div>";
                            content += "<div class='card-action center-align'>";
                            content += "<a onclick='config.error_modal(\"Application users view failed\", \"Application users view not implemented yet!\", 3000);' class='valign left tooltipped' data-position='bottom' data-delay='50' data-tooltip='users'><i class='mdi-social-group-add cyan-text text-darken-2'></i> <span class='users badge'>"+app["users"]+"</span></a>";
                            content += "<a onclick='config.error_modal(\"Application projects view failed\", \"Application projects view not implemented yet!\", 3000);' class='valign tooltipped' data-position='bottom' data-delay='50' data-tooltip='projects'><i class='mdi-file-folder cyan-text text-darken-2'></i> <span class='projects badge'>"+app["projects"]+"</span></a>";
                            content += "<a onclick='config.error_modal(\"Application records view failed\", \"Application records view not implemented yet!\", 3000);' class='valign right tooltipped' data-position='bottom' data-delay='50' data-tooltip='records'><i class='mdi-file-cloud-upload cyan-text text-darken-2'></i> <span class='records badge'>"+app["records"]+"</span></a>";
                            content += "</div>";
                            content += "</div>";
                            content += "</div>";
                            content += "<div id='app-"+app["id"]+"-confirm' class='modal'></div>";
                            content += "</div>";
                            document.getElementById("apps-list").innerHTML += content;
                        }
                    }
                } else {
                    console.log(xmlhttp.responseText);
                    config.error_modal('Add app failed', xmlhttp.responseText);
                    // Materialize.toast('<span>'+xmlhttp.responseText+'</span>', 3000);
                }
            }
        }else{
            config.error_modal('Add app failed', 'Name should not be empty.');
            // Materialize.toast('<span>Name should not be empty.</span>', 3000);
        }
    },
    add_project: function() {
        var name = document.getElementById("project-name").value;
        var tags = document.getElementById("project-tags").value;
        var description = document.getElementById("project-description").value;
        var goals = document.getElementById("project-goals").value;
        if(name != ""){
            console.log(name+" -- "+tags);
            var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
            console.log('Cookie session value: '+ Cookies.get('session'));
            xmlhttp.open("POST", this.url+"/private/project/create");
            xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
            var request = { 'name': name, 'tags': tags, 'description':description, 'goals':goals};
            xmlhttp.send(JSON.stringify(request));
            xmlhttp.onreadystatechange=function()
            {

                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    if(xmlhttp.responseText == ""){
                        console.log("Cloud returned empty response!");
                    }else{
                        if(xmlhttp.responseText == ""){
                            console.log("Cloud returned empty response!");
                        }else{
                            var response = JSON.parse(xmlhttp.responseText);
                            var project = response['content'];
                            console.log(response);
                            var accessible = false;
                            if(project["access"] == "public"){
                                accessible = true;
                            }
                            var project_block_check = document.getElementById("project-block-"+project["id"]);
                            if(project_block_check == undefined || project_block_check == null){
                                // Materialize.toast('<span>'+response['title']+'</span>', 3000);
                                // window.location.reload();
                                var content = "<div class='col s12 m6 l4' id='project-block-"+project["id"]+"'>";
                                content += "<div id='profile-card' class='card'>";
                                content += "<div class='card-image waves-effect waves-block waves-light'><img disabled class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
                                content += "<div class='card-content'>";

                                content += "<img src='../images/project.png' alt='' class='circle responsive-img activator card-profile-image'>";
                                content += "<a onclick='projectRemove(\""+project["name"]+"\",\""+project["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='delete'><i class='mdi-action-delete'></i></a>";
                                content += "<a onclick='launchRecordModal(\""+project["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='download'><i class='mdi-file-cloud-upload'></i></a>";
                                content += "<div id='update-project-"+project["id"]+"'><a id='update-action' onclick='projectEdit(\""+project["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='edit and save'><i class='mdi-editor-mode-edit'></i></a></div>";
                                content += "<a onclick='config.error_modal(\"Project details failed\", \"Project details not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='details'><i class='mdi-action-visibility'></i></a>";

                                if(Cookies.get("group") == "admin"){
                                    content += "<a onclick='userViewModal(\""+project["owner"]["id"]+"\",\""+project["owner"]["profile"]["fname"]+"\""+",\""+project["owner"]["profile"]["lname"]+"\",\""+project["owner"]["profile"]["organisation"]+"\",\""+project["owner"]["profile"]["about"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='"+project["owner"]["profile"]["fname"]+"'><i class='mdi-social-person'></i></a>";
                                }

                                content += "<span class='card-title activator black-text text-darken-4'> "+project["name"]+"</span>";
                                content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+project["created"]+"</p>";
                                // content += "<p><i class='mdi-device-access-alarm cyan-text text-darken-2'></i> "+project["project"]["duration"].split(",")[0].split(".")[0]+"</p>";
                                if(accessible){
                                    content += "<div class='row margin'><div class='switch col s12'><i class='mdi-social-public prefix cyan-text text-darken-2'></i> <label>Private <input id='project-access-"+project["id"]+"' onclick='projectAccess(\""+project["id"]+"\");' type='checkbox' checked><span class='lever'></span> Public</label></div></div>";
                                }else{
                                    content += "<div class='row margin'><div class='switch col s12'><i class='mdi-social-public prefix cyan-text text-darken-2'></i> <label>Private <input id='project-access-"+project["id"]+"' onclick='projectAccess(\""+project["id"]+"\");' type='checkbox'><span class='lever'></span></label> Public</div></div>";
                                }
                                content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-turned-in prefix cyan-text text-darken-2'></i><input readonly id='project-tags-"+project["id"]+"' type='text' value='"+project["tags"]+"'></div></div>";
                                content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='description'><div class='input-field col s12'><i class='mdi-action-description prefix cyan-text text-darken-2'></i><input readonly id='project-desc-"+project["id"]+"' type='text' value='"+project["description"]+"'></div></div>";
                                content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='goals'><div class='input-field col s12'><i class='mdi-action-subject prefix cyan-text text-darken-2'></i><input readonly id='project-goals-"+project["id"]+"' type='text' value='"+project["goals"]+"'></div></div>";
                                content += "<div class='card-action center-align'>";
                                content += "<a href='./?view=records&project="+project["id"]+"' class='valign left tooltipped' data-position='bottom' data-delay='50' data-tooltip='records'><i class='mdi-file-cloud-upload cyan-text text-darken-2'></i> <span class='records badge'>"+project["records"]+"</span></a>";
                                content += "<a href='./?view=diffs&project="+project["id"]+"' class='valign tooltipped' data-position='bottom' data-delay='50' data-tooltip='diffs'><i class='mdi-image-compare cyan-text text-darken-2'></i> <span class='diffs badge'>"+project["diffs"]+"</span></a>";
                                content += "<a href='./?view=envs&project="+project["id"]+"' class='valign right tooltipped' data-position='bottom' data-delay='50' data-tooltip='environments'><i class='mdi-maps-layers cyan-text text-darken-2'></i> <span class='containers badge'>"+project["environments"]+"</span></a>";
                                content += "</div>";
                                content += "</div>";
                                content += "</div>";
                                content += "<div id='project-"+project["id"]+"-confirm' class='modal'></div>";
                                content += "</div>";
                                document.getElementById("projects-list").innerHTML += content;
                            }
                        }
                    }
                } else {
                    console.log(xmlhttp.responseText);
                    config.error_modal('Add project failed', xmlhttp.responseText);
                    // Materialize.toast('<span>'+xmlhttp.responseText+'</span>', 3000);
                }
            }
        }else{
            config.error_modal('Add project failed', 'Project name should not be empty.');
            // Materialize.toast('<span>Project name should not be empty.</span>', 3000);
        }  
    },
    add_user: function() {
        var email = document.getElementById("user-email").value;
        var password = document.getElementById("user-password").value;
        var group = document.getElementById("user-group").value;
        if(email != "" && password != "" && group != ""){
            console.log(email+" -- "+group);
            var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
            console.log('Cookie session value: '+ Cookies.get('session'));
            xmlhttp.open("POST", this.url+"/public/user/register");
            var request = { 'email': email, 'password': password, 'group':group, 'admin':Cookies.get("session")};
            xmlhttp.send(JSON.stringify(request));
            var url_temp = this.url;
            xmlhttp.onreadystatechange=function()
            {

                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    if(xmlhttp.responseText == ""){
                        console.log("Cloud returned empty response!");
                    }else{
                        if(xmlhttp.responseText == ""){
                            console.log("Cloud returned empty response!");
                        }else{
                            var response = JSON.parse(xmlhttp.responseText);
                            var account = response['content'];
                            console.log(account);

                            var picture_uri = url_temp+"/public/user/picture/"+account["id"];
                            var user_block_check = document.getElementById("user-block-"+account["id"]);
                            if(user_block_check == undefined || user_block_check == null){
                                var content = "<div class='col s12 m6 l4 id='user-block-"+account["id"]+"'>";
                                content += "<div id='profile-card' class='card'>";
                                content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
                                content += "<div class='card-content'>";
                                content += "<img src='"+picture_uri+"' alt='' class='circle responsive-img activator card-profile-image'>";
                                content += "<div id='update-user-"+account["id"]+"'><a id='update-action' onclick='userEdit(\""+account["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='edit'><i class='mdi-editor-mode-edit'></i></a></div>";
                                content += "<a onclick='config.error_modal(\"User details failed.\", \"User details not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='details'><i class='mdi-action-visibility'></i></a>";

                                content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+account["created"]+"</p>";
                                content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-perm-identity prefix cyan-text text-darken-2'></i><input readonly id='user-fname-"+account["id"]+"' type='text' value='"+account["fname"]+"'></div></div>";
                                content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-assignment-ind prefix cyan-text text-darken-2'></i><input readonly id='user-lname-"+account["id"]+"' type='text' value='"+account["lname"]+"'></div></div>";
                                content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-picture-in-picture prefix cyan-text text-darken-2'></i><input readonly placeholder='unregistered,blocked,approved,signup' id='user-auth-"+account["id"]+"' type='text' value='"+account["auth"]+"'></div></div>";
                                content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-group-work prefix cyan-text text-darken-2'></i><input readonly placeholder='admin,user,developer,public' id='user-group-"+account["id"]+"' type='text' value='"+account["group"]+"'></div></div>";
                                content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-home prefix cyan-text text-darken-2'></i><input readonly id='user-org-"+account["id"]+"' type='text' value='"+account["org"]+"'></div></div>";
                                content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='description'><div class='input-field col s12'><i class='mdi-communication-email prefix cyan-text text-darken-2'></i><input readonly id='user-email-"+account["id"]+"' type='text' value='"+account["email"]+"'></div></div>";
                                content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='goals'><div class='input-field col s12'><i class='mdi-action-assignment prefix cyan-text text-darken-2'></i><textarea readonly class='materialize-textarea' id='user-about-"+account["id"]+"' type='text'>"+account["about"]+"</textarea></div></div>";
                                content += "<div class='card-action center-align'>";
                                content += "<a onclick='config.error_modal(\"User apps view failed.\", \"User apps view not implemented yet!\");' class='valign left tooltipped' data-position='bottom' data-delay='50' data-tooltip='applications'><i class='mdi-navigation-apps cyan-text text-darken-2 tooltipped' data-position='bottom' data-delay='50' data-tooltip='applications'></i> <span class='applications badge'>"+account["apps"]+"</span></a>";
                                content += "<a onclick='config.error_modal(\"User projects view failed.\", \"User projects view not implemented yet!\");' class='valign tooltipped' data-position='bottom' data-delay='50' data-tooltip='projects'><i class='mdi-file-folder cyan-text text-darken-2 tooltipped' data-position='bottom' data-delay='50' data-tooltip='projects'></i> <span class='projects badge'>"+account["projects"]+"</span></a>";
                                content += "<a onclick='config.error_modal(\"User records view failed.\", \"User records view not implemented yet!\");' class='valign right tooltipped' data-position='bottom' data-delay='50' data-tooltip='records'><i class='mdi-file-cloud-upload cyan-text text-darken-2 tooltipped' data-position='bottom' data-delay='50' data-tooltip='records'></i> <span class='records badge'>"+account["records"]+"</span></a>";
                                content += "</div>";
                                content += "</div>";
                                content += "</div>";
                                content += "<div id='project-"+account["id"]+"-confirm' class='modal'></div>";
                                content += "</div>";
                                document.getElementById("users-list").innerHTML += content;
                                config.error_modal('user add successfull', xmlhttp.responseText);
                            }
                        }
                    }
                } else {
                    console.log(xmlhttp.responseText);
                    config.error_modal('Add user failed', xmlhttp.responseText);
                    // Materialize.toast('<span>'+xmlhttp.responseText+'</span>', 3000);
                }
            }
        }else{
            config.error_modal('Add user failed', 'User email, password and group should not be empty.');
            // Materialize.toast('<span>Project name should not be empty.</span>', 3000);
        }
    },
    add_record: function() {
        var project_id = document.getElementById("project-id").value;
        var tags = document.getElementById("record-tags").value;
        var rationels = document.getElementById("record-rationels").value;
        var status = document.getElementById("record-status").value;
        if(project_id != ""){
            console.log(project_id+" -- "+status);
            var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
            console.log('Cookie session value: '+ Cookies.get('session'));
            xmlhttp.open("POST", this.url+"/private/record/create/"+project_id);
            xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
            var request = {'tags': tags, 'rationels':rationels, 'status':status};
            $('#loading-modal').openModal();
            xmlhttp.send(JSON.stringify(request));
            xmlhttp.onreadystatechange=function()
            {
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    if(xmlhttp.responseText == ""){
                        console.log("Cloud returned empty response!");
                    }else{
                        try{
                            var project = JSON.parse(xmlhttp.responseText)['content'];
                            var project_content = document.getElementById("project-block-"+project_id);
                            var content = "<div id='profile-card' class='card'>";
                            var accessible = false;
                            if(project["access"] == "public"){
                                accessible = true;
                            }
                            // Materialize.toast('<span>'+response['title']+'</span>', 3000);
                            // window.location.reload();
                            content += "<div class='card-image waves-effect waves-block waves-light'><img disabled class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
                            content += "<div class='card-content'>";

                            content += "<img src='../images/project.png' alt='' class='circle responsive-img activator card-profile-image'>";
                            content += "<a onclick='projectRemove(\""+project["name"]+"\",\""+project["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='delete'><i class='mdi-action-delete'></i></a>";
                            content += "<a onclick='launchRecordModal(\""+project["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='download'><i class='mdi-file-cloud-upload'></i></a>";
                            content += "<div id='update-project-"+project["id"]+"'><a id='update-action' onclick='projectEdit(\""+project["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='edit and save'><i class='mdi-editor-mode-edit'></i></a></div>";
                            content += "<a onclick='config.error_modal(\"Project details failed\", \"Project details not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='details'><i class='mdi-action-visibility'></i></a>";

                            if(Cookies.get("group") == "admin"){
                                content += "<a onclick='userViewModal(\""+project["owner"]["id"]+"\",\""+project["owner"]["profile"]["fname"]+"\""+",\""+project["owner"]["profile"]["lname"]+"\",\""+project["owner"]["profile"]["organisation"]+"\",\""+project["owner"]["profile"]["about"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='"+project["owner"]["profile"]["fname"]+"'><i class='mdi-social-person'></i></a>";
                            }

                            content += "<span class='card-title activator black-text text-darken-4'> "+project["name"]+"</span>";
                            content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+project["created"]+"</p>";
                            // content += "<p><i class='mdi-device-access-alarm cyan-text text-darken-2'></i> "+project["project"]["duration"].split(",")[0].split(".")[0]+"</p>";
                            if(accessible){
                                content += "<div class='row margin'><div class='switch col s12'><i class='mdi-social-public prefix cyan-text text-darken-2'></i> <label>Private <input id='project-access-"+project["id"]+"' onclick='projectAccess(\""+project["id"]+"\");' type='checkbox' checked><span class='lever'></span> Public</label></div></div>";
                            }else{
                                content += "<div class='row margin'><div class='switch col s12'><i class='mdi-social-public prefix cyan-text text-darken-2'></i> <label>Private <input id='project-access-"+project["id"]+"' onclick='projectAccess(\""+project["id"]+"\");' type='checkbox'><span class='lever'></span></label> Public</div></div>";
                            }
                            content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-turned-in prefix cyan-text text-darken-2'></i><input readonly id='project-tags-"+project["id"]+"' type='text' value='"+project["tags"]+"'></div></div>";
                            content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='description'><div class='input-field col s12'><i class='mdi-action-description prefix cyan-text text-darken-2'></i><input readonly id='project-desc-"+project["id"]+"' type='text' value='"+project["description"]+"'></div></div>";
                            content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='goals'><div class='input-field col s12'><i class='mdi-action-subject prefix cyan-text text-darken-2'></i><input readonly id='project-goals-"+project["id"]+"' type='text' value='"+project["goals"]+"'></div></div>";
                            content += "<div class='card-action center-align'>";
                            content += "<a href='./?view=records&project="+project["id"]+"' class='valign left tooltipped' data-position='bottom' data-delay='50' data-tooltip='records'><i class='mdi-file-cloud-upload cyan-text text-darken-2'></i> <span class='records badge'>"+project["records"]+"</span></a>";
                            content += "<a href='./?view=diffs&project="+project["id"]+"' class='valign tooltipped' data-position='bottom' data-delay='50' data-tooltip='diffs'><i class='mdi-image-compare cyan-text text-darken-2'></i> <span class='diffs badge'>"+project["diffs"]+"</span></a>";
                            content += "<a href='./?view=envs&project="+project["id"]+"' class='valign right tooltipped' data-position='bottom' data-delay='50' data-tooltip='environments'><i class='mdi-maps-layers cyan-text text-darken-2'></i> <span class='containers badge'>"+project["environments"]+"</span></a>";
                            content += "</div>";
                            content += "</div>";
                            content += "</div>";
                            content += "<div id='project-"+project["id"]+"-confirm' class='modal'></div>";
                        
                            project_content.innerHTML = content;
                            $('#loading-modal').closeModal();
                            config.error_modal('Add record successfull', 'Your changes to the project were accepted.');
                        }catch(err){
                            $('#loading-modal').closeModal();
                            config.error_modal('Add record failed', err);
                        }
                    }
                } else {
                    console.log(xmlhttp.responseText);
                    $('#loading-modal').closeModal();
                    config.error_modal('Add record failed', xmlhttp.responseText);
                    // Materialize.toast('<span>'+xmlhttp.responseText+'</span>', 3000);
                }
            }
        }else{
            config.error_modal('Add project failed', 'Project name should not be empty.');
            // Materialize.toast('<span>Project id should not be empty.</span>', 3000);
        }
    },
    upload_record: function() {
        var record_id = document.getElementById("record-id").value;
        var upload_group = document.getElementById("upload-group").value;
        var uplpad_type = document.getElementById("upload-type").value;
        var file2upload = document.getElementById("upload-file");

        if(record_id != ""){
            $('#loading-modal').openModal();
            console.log(record_id+" -- "+upload_group);
            console.log(uplpad_type+" -- "+file2upload);
            if(upload_group == "body"){
                if (file2upload.files.length > 0) {
                    var reader = new FileReader();
                    reader.onload = function() {
                        var file_content = this.result;
                        console.log(file_content);
                        if(file_content == ""){
                            console.log("Upload file is empty!");
                            config.error_modal('Upload record failed', 'The file to upload cannot be empty.');
                            // Materialize.toast('<span>The file to upload is empty</span>', 3000);
                        }else{
                            console.log('Cookie session value: '+ Cookies.get('session'));
                            var request = null;
                            if(uplpad_type == "json"){
                                try {
                                    request = JSON.parse(file_content);
                                    console.log("Json Content: "+request);
                                }
                                catch(err){
                                    config.error_modal('Upload record failed', err.message);
                                    $('#loading-modal').closeModal();
                                }
                            }else if(uplpad_type == "xml"){
                                var x2js = new X2JS();
                                try {
                                    request = x2js.xml_str2json(file_content);
                                    console.log("Xml Content: "+request);
                                }
                                catch(err){
                                    config.error_modal('Upload record failed', err.message);
                                    $('#loading-modal').closeModal();
                                }
                            }else if(uplpad_type == "yaml"){
                                try {
                                    // request = YAML.parse(file_content);
                                    request = jsyaml.safeLoad(file_content);
                                    console.log("Yaml Content: "+request);
                                }
                                catch(err){
                                    config.error_modal('Upload record failed', err.message);
                                    $('#loading-modal').closeModal();
                                }
                            }else{
                                config.error_modal('Upload record failed', 'Upload supports only json, yaml and xml.');
                                // Materialize.toast('<span>Upload supports only json, xml or yaml.</span>', 3000);
                                $('#loading-modal').closeModal();
                            }
                            if(request != null && request != undefined){
                                var xmlhttp = new XMLHttpRequest();
                                var url = config.mode+"://"+config.host+":"+config.port+"/cloud/v0.1";
                                xmlhttp.open("POST", url+"/private/record/edit/"+record_id);
                                xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
                                xmlhttp.send(JSON.stringify(request));
                                xmlhttp.onreadystatechange=function()
                                {
                                    if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                                        if(xmlhttp.responseText == ""){
                                            console.log("Cloud returned empty response!");
                                        }else{
                                            try{
                                                var record = JSON.parse(xmlhttp.responseText);
                                                var record_content = document.getElementById("record-block-"+record_id);
                                                var content = "<div id='profile-card' class='card'>";
                                                content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
                                                content += "<div class='card-content'>";
                                                var disable_download = "";
                                                if(record["container"] == false){
                                                    disable_download = "disabled";
                                                }
                                                var accessible = false;
                                                if(record["head"]["access"] == "public"){
                                                    accessible = true;
                                                }
                                                content += "<img src='../images/record.png' alt='' class='circle responsive-img activator card-profile-image'>";
                                                content += "<a onclick='recordRemove(\""+record["head"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='delete'><i class='mdi-action-delete'></i></a>";
                                                content += "<a onclick='recordUploadModal(\""+record["head"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='details'><i class='mdi-file-cloud-upload'></i></a>";

                                                content += "<a onclick=\"space.pull('"+record["head"]["project"]["id"]+"','"+record["head"]["id"]+"');\" class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right "+disable_download+" tooltipped' data-position='bottom' data-delay='50' data-tooltip='download'><i class='mdi-file-cloud-download'></i></a>";
                                                content += "<a onclick='launchEnvModal(\""+record["head"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='environment'><i class='mdi-maps-layers'></i></a>";

                                                content += "<div id='update-record-"+record["head"]["id"]+"'><a id='update-action' onclick='recordEdit(\""+record["head"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='edit'><i class='mdi-editor-mode-edit'></i></a></div>";
                                                content += "<a onclick='config.error_modal(\"Record details failed\", \"Record details not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='details'><i class='mdi-action-visibility'></i></a>";

                                                if(Cookies.get("group") == "admin"){
                                                    content += "<a onclick='projectViewModal(\""+record["head"]["project"]["name"]+"\",\""+record["head"]["project"]["tags"]+"\",\""+record["head"]["project"]["description"]+"\",\""+record["head"]["project"]["goals"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='"+record["head"]["project"]["name"]+"'><i class='mdi-file-folder'></i></a>";                        
                                                    content += "<a onclick='userViewModal(\""+record["head"]["project"]["owner"]["id"]+"\",\""+record["head"]["project"]["owner"]["profile"]["fname"]+"\""+",\""+record["head"]["project"]["owner"]["profile"]["lname"]+"\",\""+record["head"]["project"]["owner"]["profile"]["organisation"]+"\",\""+record["head"]["project"]["owner"]["profile"]["about"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='"+record["head"]["project"]["owner"]["profile"]["fname"]+"'><i class='mdi-social-person'></i></a>";
                                                }

                                                content += "<div id='select-record-"+record["head"]["id"]+"'><a id='select-action' onclick='recordSelect(\""+record["head"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='select'><i class='mdi-toggle-check-box-outline-blank'></i></a></div>";

                                                content += "<span class='card-title activator grey-text text-darken-4'>"+record["head"]["id"]+"</span>";
                                                content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+record["head"]["created"]+"</p>";
                                                content += "<p><i class='mdi-action-restore cyan-text text-darken-2'></i> "+record["head"]["duration"].split(",")[0].split(".")[0]+" ago.</p>";
                                                
                                                if(accessible){
                                                    content += "<div class='row margin'><div class='switch col s12'><i class='mdi-social-public prefix cyan-text text-darken-2'></i> <label>Private <input id='record-access-"+record["head"]["id"]+"' onclick='recordAccess(\""+record["head"]["id"]+"\");' type='checkbox' checked><span class='lever'></span> Public</label></div></div>";
                                                }else{
                                                    content += "<div class='row margin'><div class='switch col s12'><i class='mdi-social-public prefix cyan-text text-darken-2'></i> <label>Private <input id='record-access-"+record["head"]["id"]+"' onclick='recordAccess(\""+record["head"]["id"]+"\");' type='checkbox'><span class='lever'></span> Public</label></div></div>";
                                                }

                                                if(record_id == "all"){
                                                    content += "<p class='grey-text ultra-small'><i class='mdi-file-folder cyan-text text-darken-2'></i> "+record["head"]["project"]["name"]+"</p>";
                                                }
                                                content += "<div class='row margin'><div class='input-field col s12'><i class='mdi-action-turned-in prefix cyan-text text-darken-2'></i><input readonly id='record-tags-"+record["head"]["id"]+"' type='text' value='"+record["head"]["tags"]+"'></div></div>";
                                                content += "<div class='row margin'><div class='input-field col s12'><i class='mdi-notification-event-note prefix cyan-text text-darken-2'></i><input readonly id='record-rationels-"+record["head"]["id"]+"' type='text' value='"+record["head"]["rationels"]+"'></div></div>";
                                                
                                                var status_select = [];
                                                status_select.push("<div class='row margin'><div class='input-field col s12'><i class='mdi-notification-sync prefix cyan-text text-darken-2'></i><select id='record-status-"+record["head"]["id"]+"'>");
                                                status_select.push("<option value='unknown' disabled>Choose status</option>");
                                                status_select.push("<option value='finished'>Finished</option>");
                                                status_select.push("<option value='crashed'>Crashed</option>");
                                                status_select.push("<option value='terminated'>Terminated</option>");
                                                status_select.push("<option value='started'>Started</option>");
                                                status_select.push("<option value='starting'>Starting</option>");
                                                status_select.push("<option value='paused'>Paused</option>");
                                                status_select.push("<option value='sleeping'>Sleeping</option>");
                                                status_select.push("<option value='resumed'>Resumed</option>");
                                                status_select.push("<option value='running'>Running</option>");
                                                status_select.push("</select></div></div>");
                                                if(record["head"]["status"] == "unknown"){
                                                    status_select[1] = "<option value='unknown' disabled selected>Choose status</option>";
                                                }else if(record["head"]["status"] == "finished"){
                                                    status_select[2] = "<option value='finished' selected>Finished</option>";
                                                }else if(record["head"]["status"] == "crashed"){
                                                    status_select[3] = "<option value='crashed' selected>Crashed</option>>";
                                                }else if(record["head"]["status"] == "terminated"){
                                                    status_select[4] = "<option value='terminated' selected>Terminated</option>";
                                                }else if(record["head"]["status"] == "starting"){
                                                    status_select[5] = "<option value='starting' selected>Started</option>";
                                                }else if(record["head"]["status"] == "started"){
                                                    status_select[6] = "<option value='started' selected>Starting</option>";
                                                }else if(record["head"]["status"] == "paused"){
                                                    status_select[7] = "<option value='paused' selected>Paused</option>";
                                                }else if(record["head"]["status"] == "sleeping"){
                                                    status_select[8] = "<option value='sleeping' selected>Sleeping</option>";
                                                }else if(record["head"]["status"] == "resumed"){
                                                    status_select[9] = "<option value='resumed' selected>Resumed</option>";
                                                }else if(record["head"]["status"] == "running"){
                                                    status_select[10] = "<option value='running' selected>Running</option>";
                                                }
                                                
                                                for(var j = 0; j < status_select.length; j++){
                                                    // content += status_select[j];
                                                }

                                                content += "<div class='row margin'><div class='input-field col s12'><i class='mdi-notification-sync prefix cyan-text text-darken-2'></i><input readonly placeholder='finished,crashed,terminated,running' id='record-status-"+record["head"]["id"]+"' type='text' value='"+record["head"]["status"]+"'></div></div>";
                                                
                                                content += "<div class='card-action center-align'>";
                                                content += "<a onclick='config.error_modal(\"Record inputs view failed\", \"Record inputs view not implemented yet!\");' class='valign left tooltipped' data-position='bottom' data-delay='50' data-tooltip='inputs'><i class='mdi-communication-call-received cyan-text text-darken-2'></i> <span class='inputs badge'>"+record["head"]["inputs"]+"</span></a>";
                                                content += "<a onclick='config.error_modal(\"Record outputs view failed\", \"Record outputs view not implemented yet!\");' class='valign tooltipped' data-position='bottom' data-delay='50' data-tooltip='outputs'><i class='mdi-communication-call-made cyan-text text-darken-2'></i> <span class='outputs badge'>"+record["head"]["outputs"]+"</span></a>";
                                                content += "<a onclick='config.error_modal(\"Record dependencies view failed\", \"Record dependencies view not implemented yet!\");' class='valign right tooltipped' data-position='bottom' data-delay='50' data-tooltip='dependencies'><i class='mdi-editor-insert-link cyan-text text-darken-2'></i> <span class='dependencies badge'>"+record["head"]["dependencies"]+"</span></a>";
                                                content += "</div>";
                                                content += "</div>";                
                                                content += "</div>";
                                                record_content.innerHTML = content;

                                                // Materialize.toast('<span>Upload succeeded</span>', 3000);
                                                // window.location.reload();
                                                $('#loading-modal').closeModal();
                                                config.error_modal('Update succeeded', 'Your changes to this record were pushed.');
                                            }catch(err) {
                                                console.log(xmlhttp.responseText);
                                                console.log(err);
                                                config.error_modal('Upload record failed', err);
                                            }
                                        }
                                    } else {
                                        console.log(xmlhttp.responseText);
                                        config.error_modal('Upload record failed', xmlhttp.responseText);
                                        $('#loading-modal').closeModal();
                                        // Materialize.toast('<span>'+xmlhttp.responseText+'</span>', 3000);
                                    }
                                }
                            }
                        }
                    }
                    reader.readAsText(file2upload.files[0]);
                }else{
                    console.log("There is no file to upload!");
                    config.error_modal('Upload record failed', 'There is no file to upload');
                }
            }else{
                var file2upload = document.getElementById("upload-file");
                if (upload_group != "bundle"){
                    if (file2upload.files.length > 0) {
                        console.log("file not empty");
                        user.upload_file(file2upload, upload_group, record_id);
                    }else{
                        config.error_modal('Upload record failed', 'File should not be empty.');
                        $('#loading-modal').closeModal();
                        // Materialize.toast('<span>File should not be empty.</span>', 3000);
                    }
                }else{
                    // Materialize.toast('<span>Env bundle upload not implemented yet.</span>', 3000);
                    config.error_modal('Upload record failed', 'Env bundle upload not implemented yet.');
                    $('#loading-modal').closeModal();
                }
            }
            
        }else{
            config.error_modal('Upload record failed', 'Record id should not be empty.');
            // Materialize.toast('<span>Record id should not be empty.</span>', 3000);
            $('#loading-modal').closeModal();
        }
    },
    add_diff: function() {
        var record_1 = "";
        var record_2 = "";
        var from = document.getElementById("diff-from").value;
        var to = document.getElementById("diff-to").value;
        var method = document.getElementById("diff-method").value;
        var proposition = document.getElementById("diff-proposition").value;
        var status = document.getElementById("diff-status").value;
        if(from != "" && to != ""){
            console.log(from+" -- "+to);
            var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
            console.log('Cookie session value: '+ Cookies.get('session'));
            xmlhttp.open("POST", this.url+"/private/diff/create");
            xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
            var request = { 'record_from': from, 'record_to': to, 'method':method, 'proposition':proposition, 'status':status};
            xmlhttp.send(JSON.stringify(request));
            xmlhttp.onreadystatechange=function()
            {
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    if(xmlhttp.responseText == ""){
                        console.log("Cloud returned empty response!");
                    }else{
                        var response = xmlhttp.responseText;
                        console.log(response);

                        // Materialize.toast('<span>Creation succeeded</span>', 3000);
                        // window.location.reload();
                        window.location.replace("./?view=diffs");
                    }
                } else {
                    console.log(xmlhttp.responseText);
                    config.error_modal('Add diff failed', xmlhttp.responseText);
                    // Materialize.toast('<span>'+xmlhttp.responseText+'</span>', 3000);
                }
            }
        }else{
            config.error_modal('Add diff failed', 'Records from and to should be provided.');
            // Materialize.toast('<span>Record from and to should not be empty.</span>', 3000);
        }
    },
    add_env: function() {
        var record = document.getElementById("env-record").value;
        var application = document.getElementById("env-app").value;
        var group = document.getElementById("env-group").value;
        var system = document.getElementById("env-system").value;
        if(record != ""){
            console.log(record);
            var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
            console.log('Cookie session value: '+ Cookies.get('session'));
            xmlhttp.open("POST", this.url+"/private/env/create/"+record);
            xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
            var request = { 'app': application, 'group': group, 'system':system};
            xmlhttp.send(JSON.stringify(request));
            xmlhttp.onreadystatechange=function()
            {
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    if(xmlhttp.responseText == ""){
                        console.log("Cloud returned empty response!");
                    }else{
                        var response = xmlhttp.responseText;
                        console.log(response);

                        // Materialize.toast('<span>Creation succeeded</span>', 3000);
                        window.location.reload();
                    }
                } else {
                    console.log(xmlhttp.responseText);
                    config.error_modal('Add event failed', xmlhttp.responseText);
                    // Materialize.toast('<span>'+xmlhttp.responseText+'</span>', 3000);
                }
            }
        }else{
            config.error_modal('Add event failed', 'Record should be provided.');
            // Materialize.toast('<span>Record should not be empty.</span>', 3000);
        }
    }
};
