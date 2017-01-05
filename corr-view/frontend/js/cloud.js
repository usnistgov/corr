var client = new XMLHttpRequest();
var user = {
    url: "https://"+config.host+":"+config.port+"/cloud/v0.1",
    username:"",
    email: "",
    api: "",
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
                        var response = JSON.parse(xmlhttp.responseText);
                        // this.session = response['session'];
                        // console.log(this.session);
                        Cookies.set('session', response['session'], { path: '' });
                        console.log('Cookie session value: '+ Cookies.get('session'));
                        // window.location.replace("../?session="+this.session);
                        window.location.reload();
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
        xmlhttp.open("GET", this.url+"/private/"+Cookies.get('session')+"/user/logout");
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                 if(xmlhttp.responseText == ""){
                    console.log("Cloud returned empty response!");
                }else{
                    if(where != "dashboard"){
                        Cookies.set('session', 'none', { path: '' });
                        window.location.replace("./");
                    }else{
                        Cookies.set('session', 'none', { path: '/' });
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
        xmlhttp.open("POST", this.url+"/private/"+Cookies.get('session')+"/user/update");
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
                        window.location.reload(); 
                    }
                    // Materialize.toast('<span>Update succeeded</span>', 3000);
                } else {
                    console.log("Update failed");
                    config.error_modal('Update failed', response);
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
        $.ajax({
            url        : this.url+"/private/"+Cookies.get('session')+"/file/upload/"+group+"/"+item_id,
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
                    // window.location.replace("../?session="+user.session);
                    window.location.reload();
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
        xmlhttp.open("GET", this.url+"/private/"+Cookies.get('session')+"/user/trusted");
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
                
            } else {
                window.location.replace("../error/?code=404");
            }
        } 
    },
    account: function() {
        var xmlhttp = new XMLHttpRequest();
        console.log('Cookie session value: '+ Cookies.get('session'));
        // console.log(this.session);
        xmlhttp.open("GET", this.url+"/private/"+Cookies.get('session')+"/user/profile");
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
        xmlhttp.open("GET", this.url+"/private/"+Cookies.get('session')+"/user/renew");
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
            xmlhttp.open("POST", this.url+"/private/"+Cookies.get('session')+"/dashboard/developer/app/create");
            var request = { 'name': name, 'about': about, 'access': access};
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
            xmlhttp.open("POST", this.url+"/private/"+Cookies.get('session')+"/project/create");
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
                            console.log(response);

                            // Materialize.toast('<span>'+response['title']+'</span>', 3000);
                            window.location.reload();
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
    add_record: function() {
        var project_id = document.getElementById("project-id").value;
        var tags = document.getElementById("record-tags").value;
        var rationels = document.getElementById("record-rationels").value;
        var status = document.getElementById("record-status").value;
        if(project_id != ""){
            console.log(project_id+" -- "+status);
            var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
            console.log('Cookie session value: '+ Cookies.get('session'));
            xmlhttp.open("POST", this.url+"/private/"+Cookies.get('session')+"/record/create/"+project_id);
            var request = {'tags': tags, 'rationels':rationels, 'status':status};
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
                                request = JSON.parse(file_content);
                                console.log("Json Content: "+request);
                            }else if(uplpad_type == "xml"){
                                var x2js = new X2JS();
                                request = x2js.xml_str2json(file_content);
                                console.log("Xml Content: "+request);
                            }else if(uplpad_type == "yaml"){
                                request = YAML.parse(file_content);
                                console.log("Yaml Content: "+request);
                            }else{
                                config.error_modal('Upload record failed', 'Upload supports only json, yaml and xml.');
                                // Materialize.toast('<span>Upload supports only json, xml or yaml.</span>', 3000);
                            }
                            if(request != null){
                                var xmlhttp = new XMLHttpRequest();
                                var url = "https://"+config.host+":"+config.port+"/cloud/v0.1";
                                xmlhttp.open("POST", url+"/private/"+Cookies.get('session')+"/record/edit/"+record_id);
                                xmlhttp.send(JSON.stringify(request));
                                xmlhttp.onreadystatechange=function()
                                {
                                    if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                                        if(xmlhttp.responseText == ""){
                                            console.log("Cloud returned empty response!");
                                        }else{
                                            var response = xmlhttp.responseText;
                                            console.log(response);

                                            // Materialize.toast('<span>Upload succeeded</span>', 3000);
                                            window.location.reload();
                                        }
                                    } else {
                                        console.log(xmlhttp.responseText);
                                        config.error_modal('Upload record failed', xmlhttp.responseText);
                                        // Materialize.toast('<span>'+xmlhttp.responseText+'</span>', 3000);
                                    }
                                }
                            }
                        }
                    }
                    reader.readAsText(file2upload.files[0]);
                }else{
                    console.log("There is no file to upload!");
                    Materialize.toast('<span>There is no file to upload</span>', 3000);
                }
            }else{
                var file2upload = document.getElementById("upload-file");
                if (upload_group != "bundle"){
                    if (file2upload.files.length > 0) {
                        console.log("file not empty");
                        user.upload_file(file2upload, upload_group, record_id);
                    }else{
                        config.error_modal('Upload record failed', 'File should not be empty.');
                        // Materialize.toast('<span>File should not be empty.</span>', 3000);
                    }
                }else{
                    // Materialize.toast('<span>Env bundle upload not implemented yet.</span>', 3000);
                    config.error_modal('Upload record failed', 'Env bundle upload not implemnted yet.');
                }
            }
            
        }else{
            config.error_modal('Upload record failed', 'Record id should not be empty.');
            // Materialize.toast('<span>Record id should not be empty.</span>', 3000);
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
            xmlhttp.open("POST", this.url+"/private/"+Cookies.get('session')+"/diff/create");
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
                        window.location.reload();
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
            xmlhttp.open("POST", this.url+"/private/"+Cookies.get('session')+"/env/create/"+record);
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
