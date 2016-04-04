var client = new XMLHttpRequest();
var user = {
    url: "http://0.0.0.0:5200/cloud/v0.1",
    username:"",
    email: "",
    api: "",
    session: "",
    login: function() {
        // document.getElementById("myText").value
        var email = document.getElementById("login-email").value;
        var password = document.getElementById("login-password").value;
        console.log(email+" -- "+password)
        var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
        xmlhttp.open("POST", this.url+"/public/user/login");
        var request = { 'email': email, 'password': password }
        xmlhttp.send(JSON.stringify(request));
        xmlhttp.onreadystatechange=function()
        {
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                var response = JSON.parse(xmlhttp.responseText);
                this.session = response['session']
                console.log(this.session);
                
                window.location.replace("http://0.0.0.0:5000/?session="+this.session);
            } else {
                console.log(xmlhttp.responseText);
                Materialize.toast('<span>'+xmlhttp.responseText+'</span>', 3000);
                // console.log(xmlhttp.responseText);
                // window.location.replace("http://0.0.0.0:5000/error-500/");
            }
        }
        
    },
    register: function() {
        // document.getElementById("myText").value
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
                    var response = JSON.parse(xmlhttp.responseText);
                    this.session = response['session'];
                    console.log(this.session);
                    window.location.replace("http://0.0.0.0:5000/?session="+this.session);
                } else {
                    var response = xmlhttp.responseText;
                    console.log(response);
                    console.log("Registration failed");
                    if(response == ""){
                        Materialize.toast('<span>Register failed: Unknown reason.</span>', 3000);
                    }else{
                        Materialize.toast('<span>Register failed: '+response+'</span>', 3000);
                    }
                    // window.location.replace("http://0.0.0.0:5000/error-500/");
                }
            }
        }else{
            Materialize.toast('<span>Passwords mismatch.</span>', 3000);
        }
        
    },
    logout: function() {
        // document.getElementById("myText").value
        var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
        console.log(this.session);
        xmlhttp.open("GET", this.url+"/private/"+this.session+"/user/logout");
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            // console.log(xmlhttp.responseText);
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                window.location.replace("http://0.0.0.0:5000/");
            } else {
                console.log("Logout failed");
                Materialize.toast('<span>Logout failed</span>', 3000);
                // window.location.replace("http://0.0.0.0:5000/error-500/");
            }
        }
        
    },
    update: function() {
        // document.getElementById("myText").value
        var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
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
                        window.location.replace("http://0.0.0.0:5000/?session="+user.session);
                    }
                    Materialize.toast('<span>Update succeeded</span>', 3000);
                    // window.location.replace("http://0.0.0.0:5000/?session="+user.session);
                } else {
                    console.log("Update failed");
                    Materialize.toast('<span>Update failed</span>', 3000);
                    // window.location.replace("http://0.0.0.0:5000/page-500.html");
                }
            }
        }
    },

    upload_file: function(file, group, item_id) {
        // document.getElementById("myText").value
        // debugger;
        console.log("File: "+file.files[0].name);
        var formData = new FormData();
        formData.append("file", file.files[0], file.files[0].name);
        console.log(formData);
        // var xmlhttp = new XMLHttpRequest();
        // xmlhttp.open("POST", this.url+"/private/"+this.session+"/file/upload/"+group+"/"+item_id, true);
        // xmlhttp.setRequestHeader("Content-Type", "multipart/form-data");
        // xmlhttp.addEventListener("load", function (e) {
        //     // file upload is complete
        //     console.log(xmlhttp.responseText.toString);
        //     // window.location.replace("http://0.0.0.0:5000/?session="+user.session);
        // });
        // xmlhttp.send(formData);

        $.ajax({
            url        : this.url+"/private/"+this.session+"/file/upload/"+group+"/"+item_id,
            type       : "POST",
            data       : formData, 
            async      : true,
            cache      : false,
            processData: false,
            contentType: false,
            success    : function(callback){
               console.log(xmlhttp.responseText.toString);
               window.location.replace("http://0.0.0.0:5000/?session="+user.session);
            }
         });
         event.preventDefault();

        // xmlhttp.onreadystatechange=function()
        // {
        //     if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
        //         var response = xmlhttp.responseText;
        //         console.log(response)
        //         Materialize.toast('<span>Upload succeeded</span>', 3000);
        //         // window.location.replace("http://0.0.0.0:5000/?session="+user.session);
        //     } else {
        //         var response = xmlhttp.responseText;
        //         console.log(response)
        //         Materialize.toast('<span>Upload failed</span>', 3000);
        //     }
        // }
        
    },

    recover: function() {
        // document.getElementById("myText").value
        var email = document.getElementById("recover-email").value;
        console.log(email+" -- recover")
        var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
        xmlhttp.open("POST", this.url+"/public/user/recover");
        var request = { 'email': email}
        xmlhttp.send(JSON.stringify(request));
        xmlhttp.onreadystatechange=function()
        {
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                console.log(xmlhttp.responseText);                
                Materialize.toast('<span>'+xmlhttp.responseText+'</span>', 3000);
                // window.location.replace("http://0.0.0.0:5000/?action=message_sent");
            } else {
                console.log(xmlhttp.responseText);                
                Materialize.toast('<span>'+xmlhttp.responseText+'</span>', 3000);
                // window.location.replace("http://0.0.0.0:5000/page-500.html");
            }
        }
        
    },

    contactus: function() {
        // document.getElementById("myText").value
        var email = document.getElementById("contactus-email").value;
        var message = document.getElementById("contactus-message").value;
        console.log(email+" -- "+message)
        var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
        xmlhttp.open("POST", this.url+"/public/user/contactus");
        var request = { 'email': email, 'message': message }
        xmlhttp.send(JSON.stringify(request));
        xmlhttp.onreadystatechange=function()
        {
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                // console.log(xmlhttp.responseText)                
                // Materialize.toast('<span>Your message has been sent!</span>', 3000);
                window.location.replace("http://0.0.0.0:5000/?action=message_sent");
            } else {
                console.log("Contactus failed");
                Materialize.toast('<span class="yellow-text">Contact us failed</span>', 3000);
                // window.location.replace("http://0.0.0.0:5000/page-500.html");
            }
        }
        
    },
    trusted: function() {
        // document.getElementById("myText").value
        var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
        console.log(this.session);
        xmlhttp.open("GET", this.url+"/private/"+this.session+"/user/trusted");
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            // console.log(xmlhttp.responseText);
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                Materialize.toast('<span>Access trusted!</span>', 3000);
            } else {
                window.location.replace("http://0.0.0.0:5000/error-404/");
            }
        }
        
    },
    account: function() {
        // document.getElementById("myText").value
        var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
        console.log(this.session);
        xmlhttp.open("GET", this.url+"/private/"+this.session+"/user/profile");
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            // console.log(xmlhttp.responseText);
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                var response = JSON.parse(xmlhttp.responseText);
                // return fk.Response(json.dumps({'fname':profile_model.fname, 'lname':profile_model.lname, 'organisation':profile_model.organisation, 'about':profile_model.about, 'picture':profile_model.picture, 'email':user_model.email, 'session':user_model.session, 'api':user_model.api_token}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')

                this.email = response['email'];
                this.fname = response['fname']
                this.lname = response['lname'];
                this.organisation = response['organisation']
                this.about = response['about']
                this.api = response['api'];

                // document.getElementById("view-username-value").value = this.username;
                // document.getElementById("view-email-value").value = this.email;
                // document.getElementById("view-api-value").value = this.api;

                $('#view-username-value').text(this.username);
                document.getElementById('view-email').value = this.email;
                document.getElementById('view-api').value = this.api;

                document.getElementById('view-fname').value = this.fname;
                document.getElementById('view-lname').value = this.lname;
                document.getElementById('view-org').value = this.organisation;
                document.getElementById('view-about').value = this.about;


                // if(this.username.length > 18){
                //     $('#view-username-value').text(this.username.substring(0,15)+"...");
                // }else{
                //     $('#view-username-value').text(this.username);
                // }
                // if(this.email.length > 18){
                //     $('#view-email-value').text(this.email.substring(0,15)+"...");
                // }else{
                //     $('#view-email-value').text(this.email);
                // }
                // if(this.api.length > 18){
                //     $('#view-api-value').text(this.api.substring(0,15)+"...");
                // }else{
                //     $('#view-api-value').text(this.api);
                // }

                console.log("Account Api: "+this.api);
            } else {
                window.location.replace("http://0.0.0.0:5000/error-404/");
            }
        }
        
    },
    renew: function() {
        // document.getElementById("myText").value
        var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
        console.log(this.session);
        xmlhttp.open("GET", this.url+"/private/"+this.session+"/user/renew");
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            // console.log(xmlhttp.responseText);
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                var response = JSON.parse(xmlhttp.responseText);
                this.api = response['api'];
                if(this.api.length > 18){
                    $('#view-api-value').text(this.api.substring(0,15)+"...");
                }else{
                    $('#view-api-value').text(this.api);
                }
                Materialize.toast('<span>API Token renewed!</span>', 3000);
            } else {
                window.location.replace("http://0.0.0.0:5000/error-404/");
            }
        }
        
    },
    copy_api: function() {
        console.log("Api: "+this.api);
        console.log("Email: "+this.email);
        console.log("Username: "+this.username);
        console.log("Session: "+this.session);
        // window.prompt("Copy to clipboard: Ctrl+C, Enter", this.api);
        // window.clipboardData.setData('Text', this.api);
        // console.log(this.api);
    }

}

var Space = function (session){
    var url = "http://0.0.0.0:5200/cloud/v0.1";
    this.session = session;
    this.dash_content = "";

    this.dashboard = function() {
        var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
        console.log(this.session);
        xmlhttp.open("GET", url+"/private/"+this.session+"/dashboard/projects");
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                var response = JSON.parse(xmlhttp.responseText);
                this.dash_content = response;
                // console.log(xmlhttp.responseText);

                document.getElementById("projects-list").innerHTML = "";

                for(var i = 0; i < response["projects"].length; i++){
                    project = response["projects"][i];
                    var disable_view = "";
                    if(project["project"]["total_records"] == 0){
                        disable_view = "disabled";
                    }
                    // console.log(project);
                    var content = "<div class=\"col s12 m6 l4\">";
                    content += "<div id=\"profile-card\" class=\"card\">";
                    content += "<div class=\"card-image waves-effect waves-block waves-light\"><img class=\"activator\" src=\"../images/user-bg.jpg\" alt=\"user background\"></div>";
                    content += "<div class=\"card-content\">";
                    content += "<img src=\"../images/project.png\" alt=\"\" class=\"circle responsive-img activator card-profile-image\"><a onclick=\"space.records('"+project["project"]["name"]+"')\" class=\"btn-floating activator btn-move-up waves-effect waves-light darken-2 right "+disable_view+"\"><i class=\"mdi-action-visibility\"></i></a><span class=\"card-title activator grey-text text-darken-4\"> "+project["project"]["name"]+"</span>";
                    content += "<p class=\"grey-text ultra-small\"><i class=\"mdi-device-access-time cyan-text text-darken-2\"></i> "+project["project"]["created"]+"</p>";
                    content += "<p><i class=\"mdi-device-access-alarm cyan-text text-darken-2\"></i> "+project["project"]["duration"]+"</p>";
                    content += "<p><i class=\"mdi-action-description cyan-text text-darken-2\"></i> "+project["project"]["description"]+"</p>";
                    content += "<p><i class=\"mdi-action-subject cyan-text text-darken-2\"></i> "+project["project"]["goals"]+"</p>";
                    content += "<div class=\"card-action center-align\">";
                    content += "<a href=\"#\" class=\"valign\"><i class=\"mdi-file-cloud-done cyan-text text-darken-2\"></i> <span class=\"records badge\">"+project["project"]["total_records"]+"</span></a>";
                    content += "<a href=\"#\" class=\"valign\"><i class=\"mdi-image-compare cyan-text text-darken-2\"></i> <span class=\"diffs badge\">"+project["project"]["total_diffs"]+"</span></a>";
                    content += "<a href=\"#\" class=\"valign\"><i class=\"mdi-editor-insert-chart cyan-text text-darken-2\"></i> <span class=\"containers badge\">"+project["project"]["history"]+"</span></a>";
                    content += "</div>";
                    content += "</div>";
                    content += "</div>";
                    content += "</div>";
                    document.getElementById("projects-list").innerHTML += content;
                }

                document.getElementById("temporal-slider").innerHTML = "<div class=\"slider-date\"><div class=\"lower\"></div><div class=\"upper\"></div></div><span id=\"event-start\" class=\"temporal-val\">Thursday, 30th December 2010</span><span id=\"event-end\" class=\"temporal-val date-right\">Thursday, 1st January 2015</span>";

                $('.slider-date').noUiSlider({
                    animate: true,
                    connect: true,
                    start: [ timestamp(response["projects"][0]["project"]["created"]), timestamp(response["projects"][response["projects"].length - 1]["project"]["created"]) ],
                    step: 1 * 24 * 60 * 60 * 1000,
                    format: wNumb({
                        decimals: 0
                        }),
                    range: {
                        min: timestamp(response["projects"][0]["project"]["created"]),
                        max: timestamp(response["projects"][response["projects"].length - 1]["project"]["created"])
                    }
                });

                $(".slider-date").Link('lower').to($("#event-start"), setDate);
                $(".slider-date").Link('upper').to($("#event-end"), setDate);
            } else {
                console.log("Dashboard failed");
                // Materialize.toast('<span>Dashboard failed</span>', 3000);
                // window.location.replace("http://0.0.0.0:5000/error-500/");
            }
        }
        
    }

    this.records = function(project_name) {
        document.getElementById("projects-list").innerHTML = "<div class=\"progress\"><div class=\"indeterminate\"></div></div>";
        document.getElementById("temporal-slider").innerHTML = "";
        var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
        console.log("Project name: "+project_name);
        xmlhttp.open("GET", url+"/private/"+this.session+"/project/record/"+project_name);
        console.log(this.session);
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                var response = JSON.parse(xmlhttp.responseText);
                this.dash_content = response;
                // console.log(xmlhttp.responseText);

                // {
                //     "created": "2015-06-18 17:05:03.477000",
                //     "dependencies": 3,
                //     "id": "55833be59f9d516e1a800779",
                //     "inputs": 2,
                //     "label": "Record Label - Procede_04152015",
                //     "outputs": 2,
                //     "project": "repro_lab",
                //     "status": "terminated",
                //     "updated": "2015-06-18 17:50:34.341000"
                // } <span class=\"new badge\">4</span></a>

                document.getElementById("projects-list").innerHTML = "";

                for(var i = 0; i < response["records"].length; i++){
                    record = response["records"][i];
                    // console.log(record);
                    var content = "<div class=\"col s12 m6 l4\" id=\"record-"+record["id"]+"\"> ";
                    content += "<div id=\"profile-card\" class=\"card\">";
                    content += "<div class=\"card-image waves-effect waves-block waves-light\"><img class=\"activator\" src=\"../images/user-bg.jpg\" alt=\"user background\"></div>";
                    content += "<div class=\"card-content\">";
                    // console.log(record);
                    var disable_download = "";
                    if(record["container"] == false){
                        disable_download = "disabled";
                    }
                    // console.log(record);
                    content += "<img src=\"../images/record.png\" alt=\"\" class=\"circle responsive-img activator card-profile-image\"><a onclick=\"space.pull('"+record["project"]+"','"+record["id"]+"')\" class=\"btn-floating activator btn-move-up waves-effect waves-light darken-2 right "+disable_download+"\"><i class=\"mdi-file-cloud-download\"></i></a><span class=\"card-title activator grey-text text-darken-4\"> "+record["label"]+"</span>";
                    content += "<p class=\"grey-text ultra-small\"><i class=\"mdi-device-access-time cyan-text text-darken-2\"></i> "+record["created"]+"</p>";
                    content += "<p><i class=\"mdi-device-access-alarm cyan-text text-darken-2\"></i> "+record["updated"]+"</p>";
                    content += "<p><i class=\"mdi-notification-event-note cyan-text text-darken-2\"></i> "+record["id"]+"</p>";
                    content += "<p><i class=\"mdi-notification-sync cyan-text text-darken-2\"></i> "+record["status"]+"</p>";
                    content += "<div class=\"card-action center-align\">";
                    content += "<a href=\"#\" class=\"valign\"><i class=\"mdi-action-input cyan-text text-darken-2\"></i> <span class=\"inputs badge\">"+record["inputs"]+"</span></a>";
                    content += "<a href=\"#\" class=\"valign\"><i class=\"mdi-action-launch cyan-text text-darken-2\"></i> <span class=\"outputs badge\">"+record["outputs"]+"</span></a>";
                    content += "<a href=\"#\" class=\"valign\"><i class=\"mdi-editor-insert-link cyan-text text-darken-2\"></i> <span class=\"dependencies badge\">"+record["dependencies"]+"</span></a>";
                    content += "</div>";
                    content += "</div>";                
                    content += "</div>";
                    content += "</div>";
                    document.getElementById("projects-list").innerHTML += content;
                }

                document.getElementById("temporal-slider").innerHTML = "<div class=\"slider-date\"><div class=\"lower\"></div><div class=\"upper\"></div></div><span id=\"event-start\" class=\"temporal-val\">Thursday, 30th December 2010</span><span id=\"event-end\" class=\"temporal-val date-right\">Thursday, 1st January 2015</span>";

                $('.slider-date').noUiSlider({
                    animate: true,
                    connect: true,
                    start: [ timestamp(response["records"][0]["created"]), timestamp(response["records"][response["records"].length-1]["created"]) ],
                    step: 1 * 24 * 60 * 60 * 1000,
                    format: wNumb({
                        decimals: 0
                        }),
                    range: {
                        min: timestamp(response["records"][0]["created"]),
                        max: timestamp(response["records"][response["records"].length-1]["created"])
                    }
                });

                $(".slider-date").Link('lower').to($("#event-start"), setDate);
                $(".slider-date").Link('upper').to($("#event-end"), setDate);
            } else {
                console.log("Dashboard failed");
                // Materialize.toast('<span>Dashboard failed</span>', 3000);
                // window.location.replace("http://0.0.0.0:5000/error-500/");
            }
        }
        
    }

    this.exportToJson = function () {
        var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
        console.log(this.session);
        xmlhttp.open("GET", url+"/private/"+this.session+"/dashboard/projects");
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                // var response = JSON.parse(xmlhttp.responseText);
                // window.open('data:text/json;charset=utf-8,' + escape(this.dash_content));
                if(xmlhttp.responseText != ""){
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
                    // var aFileParts = [xmlhttp.responseText;
                    // var oMyBlob = new Blob(aFileParts, {type : 'text/json'}); // the blob
                    // window.open(URL.createObjectURL(oMyBlob));
                }
            } else {
                console.log("Dashboard download failed");
                // Materialize.toast('<span>Dashboard download failed</span>', 3000);
                // window.location.replace("http://0.0.0.0:5000/error-500/");
            }
        }
    }

    this.pull = function(project_name, record_id) {
        // var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
        // console.log("Project name: "+project_name);
        // xmlhttp.open("GET", url+"/private/"+this.session+"/record/pull/"+project_name+"/"+record_id);
        // console.log(url+"/private/"+this.session+"/record/pull/"+project_name+"/"+record_id);
        // console.log(this.session);
        // xmlhttp.responseType = 'blob';
        window.location.replace(url+"/private/"+this.session+"/record/pull"+"/"+record_id);
        // xmlhttp.send();
        // xmlhttp.onreadystatechange=function()
        // {
        //     if (xmlhttp.status == 204 || xmlhttp.status == 401 || xmlhttp.status == 405) {
        //         // var response = JSON.parse(xmlhttp.responseText);
        //         Materialize.toast('<span>Dashboard failed</span>', 3000);
        //     }else{
        //         // var blob = new Blob([xmlhttp.response], { type: 'application/x-tar' });
        //     }
        // }

        // xmlhttp.xmlhttp = function(e) {
        //   window.requestFileSystem(TEMPORARY, 1024 * 1024, function(fs) {
        //     fs.root.getFile(project_name+'_'+record_id, {create: true}, function(fileEntry) {
        //       fileEntry.createWriter(function(writer) {

        //         writer.onwrite = function(e) {};
        //         writer.onerror = function(e) {};

        //         var blob = new Blob([xhr.response], {type: 'application/x-tar'});

        //         writer.write(blob);

        //       }, onError);
        //     }, onError);
        //   }, onError);
        // }
    }
};