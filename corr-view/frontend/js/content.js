var Space = function (){
    var url = config.mode+"://"+config.host+":"+config.port+"/cloud/v0.1";
    // this.session = session;
    this.dash_content = "";
    this.query_result = "";
    this.dashboard = function() {
        var xmlhttp = new XMLHttpRequest();
        console.log('Cookie session value: '+ Cookies.get('session'));
        // console.log(this.session);
        xmlhttp.open("GET", url+"/private/"+Cookies.get('session')+"/dashboard/projects");
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
                                // content = content.replace(/session/g, params[0]); 
                                content = content.replace(/project_id/g, params[1]);
                                content = content.replace(/project_name/g, params[2]);
                                content = content.replace(/project_created/g, params[3]);
                                content = content.replace(/project_duration/g, params[4]);
                                content = content.replace(/project_description/g, params[5]);
                                content = content.replace(/project_goals/g, params[6]);
                                content = content.replace(/project_records/g, params[7]);
                                content = content.replace(/project_diffs/g, params[8]);
                                content = content.replace(/project_envs/g, params[9]);
                            }
                        };
                        function failed(){
                            window.location.replace("/error/?code=404");
                        };

                        var params = [project["project"]["id"], project["project"]["name"], project["project"]["created"], project["project"]["duration"], project["project"]["description"], project["project"]["goals"], project["project"]["records"], project["project"]["diffs"], project["project"]["environments"]];
                        config.load_xml('project_content.xml', params, succeed, failed);

                        var content = "<div class='col s12 m6 l4'>";
                        content += "<div id='profile-card' class='card'>";
                        content += "<div class='card-image waves-effect waves-block waves-light'><img disabled class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
                        content += "<div class='card-content'>";

                        content += "<img src='../images/project.png' alt='' class='circle responsive-img activator card-profile-image'>";
                        content += "<a onclick='projectRemove(\""+project["project"]["name"]+"\",\""+project["project"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='delete'><i class='mdi-action-delete'></i></a>";
                        content += "<a onclick='launchRecordModal(\""+project["project"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='download'><i class='mdi-file-cloud-upload'></i></a>";
                        content += "<div id='update-project-"+project["project"]["id"]+"'><a id='update-action' onclick='projectEdit(\""+project["project"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='edit and save'><i class='mdi-editor-mode-edit'></i></a></div>";
                        content += "<a onclick='config.error_modal(\"Project details failed\", \"Project details not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='details'><i class='mdi-action-visibility'></i></a>";

                        content += "<span class='card-title activator black-text text-darken-4'> "+project["project"]["name"]+"</span>";
                        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+project["project"]["created"]+"</p>";
                        // content += "<p><i class='mdi-device-access-alarm cyan-text text-darken-2'></i> "+project["project"]["duration"].split(",")[0].split(".")[0]+"</p>";
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-turned-in prefix cyan-text text-darken-2'></i><input readonly id='project-tags-"+project["project"]["id"]+"' type='text' value='"+project["project"]["tags"]+"'></div></div>";
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='description'><div class='input-field col s12'><i class='mdi-action-description prefix cyan-text text-darken-2'></i><input readonly id='project-desc-"+project["project"]["id"]+"' type='text' value='"+project["project"]["description"]+"'></div></div>";
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='goals'><div class='input-field col s12'><i class='mdi-action-subject prefix cyan-text text-darken-2'></i><input readonly id='project-goals-"+project["project"]["id"]+"' type='text' value='"+project["project"]["goals"]+"'></div></div>";
                        content += "<div class='card-action center-align'>";
                        content += "<a href='./?view=records&project="+project["project"]["id"]+"' class='valign left tooltipped' data-position='bottom' data-delay='50' data-tooltip='records'><i class='mdi-file-cloud-done cyan-text text-darken-2'></i> <span class='records badge'>"+project["project"]["records"]+"</span></a>";
                        content += "<a href='./?view=diffs&project="+project["project"]["id"]+"' class='valign tooltipped' data-position='bottom' data-delay='50' data-tooltip='diffs'><i class='mdi-image-compare cyan-text text-darken-2'></i> <span class='diffs badge'>"+project["project"]["diffs"]+"</span></a>";
                        content += "<a href='./?view=envs&project="+project["project"]["id"]+"' class='valign right tooltipped' data-position='bottom' data-delay='50' data-tooltip='environments'><i class='mdi-maps-layers cyan-text text-darken-2'></i> <span class='containers badge'>"+project["project"]["environments"]+"</span></a>";
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
        console.log('Cookie session value: '+ Cookies.get('session'));
        // console.log(this.session);
        xmlhttp.open("GET", url+"/private/"+Cookies.get('session')+"/dashboard/developer/apps");
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
                                // content = content.replace(/session/g, params[0]);
                                content = content.replace(/app_id/g, params[1]);
                                content = content.replace(/app_name/g, params[2]);
                                content = content.replace(/app_created/g, params[3]);
                                content = content.replace(/app_network/g, params[4]);
                                content = content.replace(/app_access/g, params[5]);
                                content = content.replace(/app_storage/g, params[6]);
                                content = content.replace(/app_token/g, params[7]);
                                content = content.replace(/app_about/g, params[8]);
                            }
                        };
                        function failed(){
                            window.location.replace("/error/?code=404");
                        };

                        var params = [app["id"], app["name"], app["created"], app["network"], app["access"], app["storage"], app["token"], app["about"]];
                        config.load_xml('app_content.xml', params, succeed, failed);

                        var content = "<div class='col s12 m6 l4'>";
                        content += "<div id='profile-card' class='card'>";
                        content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
                        content += "<div class='card-content'>";
                        content += "<img src='../images/gearsIcon.png' alt='' class='circle responsive-img activator card-profile-image'>";
                        content += "<a onclick='appRemove(\""+app["name"]+"\",\""+app["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='delete'><i class='mdi-action-delete'></i></a>";
                        content += "<a onclick='config.error_modal(\"Application downoload failed\", \"Application download not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='download'><i class='mdi-file-cloud-download'></i></a>";
                        content += "<div id='update-app-"+app["id"]+"'><a id='update-action' onclick='appEdit(\""+app["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='edit'><i class='mdi-editor-mode-edit'></i></a></div>";
                        content += "<a onclick='config.error_modal(\"Application details failed\", \"Application details not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='details'><i class='mdi-action-visibility'></i></a>";

                        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+app["created"]+"</p>";
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-turned-in prefix cyan-text text-darken-2'></i><input readonly id='app-name-"+app["id"]+"' type='text' value='"+app["name"]+"'></div></div>";
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-settings-ethernet prefix cyan-text text-darken-2'></i><input readonly id='app-network-"+app["id"]+"' type='text' value='"+app["network"]+"'></div></div>";
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

                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='description'><div class='input-field col s12'><i class='mdi-communication-vpn-key prefix cyan-text text-darken-2'></i><input readonly id='app-token-"+app["id"]+"' type='text' value='"+app["token"]+"'></div></div>";
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
        console.log('Cookie session value: '+ Cookies.get('session'));
        if(project_id == "all"){
            xmlhttp.open("GET", url+"/private/"+Cookies.get('session')+"/dashboard/records/all");
        }else{
            xmlhttp.open("GET", url+"/private/"+Cookies.get('session')+"/dashboard/records/"+project_id);
        }
        // console.log(this.session);
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
                    var records = response["records"];
                    var selected_records = [];
                    
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
                        content += "<a onclick='recordRemove(\""+record["head"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='delete'><i class='mdi-action-delete'></i></a>";
                        content += "<a onclick='recordUploadModal(\""+record["head"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='details'><i class='mdi-file-cloud-upload'></i></a>";

                        content += "<a onclick=\"space.pull('"+record["head"]["project"]["id"]+"','"+record["head"]["id"]+"');\" class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right "+disable_download+" tooltipped' data-position='bottom' data-delay='50' data-tooltip='download'><i class='mdi-file-cloud-download'></i></a>";
                        content += "<a onclick='launchEnvModal(\""+record["head"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='environment'><i class='mdi-maps-layers'></i></a>";

                        content += "<div id='update-record-"+record["head"]["id"]+"'><a id='update-action' onclick='recordEdit(\""+record["head"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='edit'><i class='mdi-editor-mode-edit'></i></a></div>";
                        content += "<a onclick='config.error_modal(\"Record details failed\", \"Record details not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='details'><i class='mdi-action-visibility'></i></a>";

                        content += "<div id='select-record-"+record["head"]["id"]+"'><a id='select-action' onclick='recordSelect(\""+record["head"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='select'><i class='mdi-toggle-check-box-outline-blank'></i></a></div>";

                        content += "<span class='card-title activator grey-text text-darken-4'>"+record["head"]["id"]+"</span>";
                        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+record["head"]["created"]+"</p>";
                        content += "<p><i class='mdi-action-restore cyan-text text-darken-2'></i> "+record["head"]["duration"].split(",")[0].split(".")[0]+" ago.</p>";

                        if(project_id == "all"){
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
                        content += "</div>";
                        document.getElementById("records-list").innerHTML += content;
                    }
                }
            } else {
                console.log("Dashboard failed");
            }
        }
    },
    this.diffs = function(project_id) {
        document.getElementById("diffs-list").innerHTML = "<div class='progress'><div class='indeterminate'></div></div>";
        document.getElementById("temporal-slider").innerHTML = "";
        var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
        console.log("Project id: "+project_id);
        console.log('Cookie session value: '+ Cookies.get('session'));
        if(project_id == "all"){
            xmlhttp.open("GET", url+"/private/"+Cookies.get('session')+"/dashboard/diffs/all");
        }else{
            xmlhttp.open("GET", url+"/private/"+Cookies.get('session')+"/dashboard/diffs/"+project_id);
        }
        // console.log(this.session);
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                if(xmlhttp.responseText == ""){
                    console.log("Cloud returned empty response!");
                }else{
                    var response = JSON.parse(xmlhttp.responseText);
                    document.getElementById("diffs-list").innerHTML = "";
                    this.dash_content = response;
                    
                    for(var i = 0; i < response["number"]; i++){
                        diff = response["diffs"][i];
                        console.log(diff);
                        var content = "<div class='col s12 m6 l4' id='"+diff["id"]+"'> ";
                        content += "<div id='profile-card' class='card'>";
                        content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
                        content += "<div class='card-content'>";
                        content += "<img src='../images/diff.png' alt='' class='circle responsive-img activator card-profile-image'>";
                        content += "<a onclick='diffRemove(\""+diff["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-action-delete'></i></a>";
                        content += "<a onclick='config.error_modal(\"Diff comment failed\", \"Diff comment not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='comment'><i class='mdi-editor-insert-comment'></i></a>";
                        content += "<a onclick='config.error_modal(\"Diff download failed\", \"Diff download not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='download'><i class='mdi-file-cloud-download'></i></a>";
                        content += "<div id='update-diff-"+diff["id"]+"'><a id='update-action' onclick='diffEdit(\""+diff["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='edit'><i class='mdi-editor-mode-edit'></i></a></div>";
                        content += "<a onclick='config.error_modal(\"Diff details failed\", \"Diff details not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='details'><i class='mdi-action-visibility'></i></a>";

                        content += "<span class='card-title activator grey-text text-darken-4'>"+diff["id"]+"</span>";
                        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+diff["created"]+"</p>";

                        var method_select = [];
                        method_select.push("<div class='row margin'><div class='input-field col s12'><i class='mdi-action-book prefix cyan-text text-darken-2'></i><select id='diff-method-"+diff["id"]+"'>");
                        method_select.push("<option value='undefined' disabled>Choose method</option>");
                        method_select.push("<option value='default'>Default</option>");
                        method_select.push("<option value='visual'>Visual</option>");
                        method_select.push("<option value='custom'>Custom</option>");
                        method_select.push("</select></div></div>");
                        if(diff["method"] == "undefined"){
                            method_select[1] = "<option value='undefined' disabled selected>Choose method</option>";
                        }else if(diff["method"] == "default"){
                            method_select[2] = "<option value='default' selected>Default</option>";
                        }else if(diff["method"] == "visual"){
                            method_select[3] = "<option value='visual' selected>Visual</option>>";
                        }else if(diff["method"] == "custom"){
                            method_select[4] = "<option value='custom' selected>Custom</option>";
                        }
                        
                        for(var j = 0; j < method_select.length; j++){
                            // content += method_select[j];
                        }

                        content += "<div class='row margin'><div class='input-field col s12'><i class='mdi-action-book prefix cyan-text text-darken-2'></i><input readonly placeholder='default,visual,custom' id='diff-method-"+diff["id"]+"' type='text' value='"+diff["method"]+"'></div></div>";

                        var propos_select = [];
                        propos_select.push("<div class='row margin'><div class='input-field col s12'><i class='mdi-action-assignment prefix cyan-text text-darken-2'></i><select id='diff-proposition-"+diff["id"]+"'>");
                        propos_select.push("<option value='undefined' disabled>Choose proposition</option>");
                        propos_select.push("<option value='repeated'>Repeated</option>");
                        propos_select.push("<option value='reproduced'>Reproduced</option>");
                        propos_select.push("<option value='replicated'>Replicated</option>");
                        propos_select.push("<option value='non-replicated'>Non-replicated</option>");
                        propos_select.push("<option value='non-repeated'>Non-repeated</option>");
                        propos_select.push("<option value='non-reproduced'>Non-reproduced</option>");
                        propos_select.push("</select></div></div>");
                        if(diff["proposition"] == "undefined"){
                            propos_select[1] = "<option value='undefined' disabled selected>Choose proposition</option>";
                        }else if(diff["proposition"] == "repeated"){
                            propos_select[2] = "<option value='repeated' selected>Repeated</option>";
                        }else if(diff["proposition"] == "reproduced"){
                            propos_select[3] = "<option value='reproduced' selected>Reproduced</option>>";
                        }else if(diff["proposition"] == "replicated"){
                            propos_select[4] = "<option value='replicated' selected>Replicated</option>";
                        }else if(diff["proposition"] == "non-replicated"){
                            propos_select[5] = "<option value='non-replicated' selected>Non-replicated</option>";
                        }else if(diff["proposition"] == "non-repeated"){
                            propos_select[6] = "<option value='non-repeated' selected>Non-repeated</option>";
                        }else if(diff["proposition"] == "non-reproduced"){
                            propos_select[7] = "<option value='non-reproduced' selected>Non-reproduced</option>";
                        }
                        
                        for(var j = 0; j < propos_select.length; j++){
                            // content += propos_select[j];
                        }

                        content += "<div class='row margin'><div class='input-field col s12'><i class='mdi-action-assignment prefix cyan-text text-darken-2'></i><input readonly placeholder='repeated,reproduced,replicated,non-replicated,non-repeated,non-reproduced' class='autocomplete' id='diff-proposition-"+diff["id"]+"' type='text' value='"+diff["proposition"]+"'></div></div>";
                        
                        var status_select = [];
                        status_select.push("<div class='row margin'><div class='input-field col s12'><i class='mdi-notification-sync prefix cyan-text text-darken-2'></i><select id='diff-status-"+diff["id"]+"'>");
                        status_select.push("<option value='undefined' disabled>Choose status</option>");
                        status_select.push("<option value='agreed'>Agreed</option>");
                        status_select.push("<option value='denied'>Denied</option>");
                        status_select.push("<option value='altered'>Altered</option>");
                        status_select.push("</select></div></div>");
                        if(diff["status"] == "undefined"){
                            status_select[1] = "<option value='undefined' disabled selected>Choose status</option>";
                        }else if(diff["status"] == "agreed"){
                            status_select[2] = "<option value='agreed' selected>Agreed</option>";
                        }else if(diff["status"] == "denied"){
                            status_select[3] = "<option value='denied' selected>Denied</option>>";
                        }else if(diff["status"] == "altered"){
                            status_select[4] = "<option value='altered' selected>Altered</option>";
                        }
                        
                        for(var j = 0; j < status_select.length; j++){
                            // content += status_select[j];
                        }

                        content += "<div class='row margin'><div class='input-field col s12'><i class='mdi-notification-sync prefix cyan-text text-darken-2'></i><input readonly placeholder='agreed,denied' id='diff-status-"+diff["id"]+"' type='text' value='"+diff["status"]+"'></div></div>";

                        content += "<div class='card-action center-align'>";
                        var record_from = diff["from"];
                        var record_to = diff["to"];

                        content += "<a onclick='recordViewModal(\""+record_from["head"]["id"]+"\",\""+record_from["head"]["project"]["name"]+"\",\""+record_from["head"]["tags"]+"\",\""+record_from["head"]["rationels"]+"\",\""+record_from["head"]["status"]+"\");' class='valign left tooltipped' data-position='bottom' data-delay='50' data-tooltip='record from'><i class='mdi-file-cloud-download cyan-text text-darken-2'></i><span class='from badge'>"+record_from["head"]["id"].substring(0,4)+"..."+record_from["head"]["id"].substring(19,23)+"</span></a>";
                        content += "<a onclick='recordViewModal(\""+record_to["head"]["id"]+"\",\""+record_to["head"]["project"]["name"]+"\",\""+record_to["head"]["tags"]+"\",\""+record_to["head"]["rationels"]+"\",\""+record_to["head"]["status"]+"\");' class='valign'><i class='mdi-file-cloud-upload cyan-text text-darken-2 tooltipped' data-position='bottom' data-delay='50' data-tooltip='record to'></i><span class='to badge'>"+record_to["head"]["id"].substring(0,4)+"..."+record_to["head"]["id"].substring(19,23)+"</span></a>";
                        content += "<a onclick='config.error_modal(\"Diff comments view failed\", \"Diff comments view not implemented yet!\");' class='valign right'><i class='mdi-editor-insert-comment cyan-text text-darken-2 tooltipped' data-position='bottom' data-delay='50' data-tooltip='comments'></i> <span class='comments badge'>"+diff["comments"]+"</span></a>";
                        content += "</div>";
                        content += "</div>";                
                        content += "</div>";
                        content += "</div>";
                        document.getElementById("diffs-list").innerHTML += content;
                    }
                }
            } else {
                console.log("Dashboard failed");
            }
        }
    },
    this.envs = function(project_id) {
        document.getElementById("envs-list").innerHTML = "<div class='progress'><div class='indeterminate'></div></div>";
        document.getElementById("temporal-slider").innerHTML = "";
        var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
        console.log("Project id: "+project_id);
        console.log('Cookie session value: '+ Cookies.get('session'));
        if(project_id == "all"){
            xmlhttp.open("GET", url+"/private/"+Cookies.get('session')+"/dashboard/envs/all");
        }else{
            xmlhttp.open("GET", url+"/private/"+Cookies.get('session')+"/dashboard/envs/"+project_id);
        }
        // console.log(this.session);
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                if(xmlhttp.responseText == ""){
                    console.log("Cloud returned empty response!");
                }else{
                    var response = JSON.parse(xmlhttp.responseText);
                    document.getElementById("envs-list").innerHTML = "";
                    this.dash_content = response;
                    var envs = response["envs"];
                    
                    for(var i = 0; i < response["envs"].length; i++){
                        env = response["envs"][i];
                        console.log(env);
                        var content = "<div class='col s12 m6 l4' id='"+env["id"]+"'> ";
                        content += "<div id='profile-card' class='card'>";
                        content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
                        content += "<div class='card-content'>";
                        content += "<img src='../images/env.png' alt='' class='circle responsive-img activator card-profile-image'>";
                        content += "<a onclick='envRemove(\""+env["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='delete'><i class='mdi-action-delete'></i></a>";
                        content += "<a onclick=\"space.env_pull('"+env["id"]+"');\" class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='download'><i class='mdi-file-cloud-download'></i></a>";
                        content += "<div id='update-env-"+env["id"]+"'><a id='update-action' onclick='envEdit(\""+env["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='edit'><i class='mdi-editor-mode-edit'></i></a></div>";
                        content += "<a onclick='config.error_modal(\"Environment details failed\", \"Environment details not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='details'><i class='mdi-action-visibility'></i></a>";

                        content += "<span class='card-title activator grey-text text-darken-4'>"+env["id"]+"</span>";
                        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+env["created"]+"</p>";
                        // if(project_id == "all"){
                        //     content += "<p class='grey-text ultra-small'><i class='mdi-file-folder cyan-text text-darken-2'></i> "+record["head"]["project"]["name"]+"</p>";
                        // }
                        // content += "<p class='grey-text ultra-small'><i class='mdi-navigation-apps cyan-text text-darken-2'></i> "+env["application"]["name"]+"</p>";
                        content += "<div class='row margin'><div class='input-field col s12 m6 l10'><i class='mdi-navigation-apps prefix cyan-text text-darken-2'></i><input readonly id='env-app-"+env["id"]+"' type='text' value='"+env["application"]["name"]+"'></div><div class='input-field col s12 m6 l2'><a onclick='appViewModal(\""+env["application"]["name"]+"\",\""+env["application"]["access"]+"\",\""+env["application"]["about"]+"\");' class='btn waves-effect cyan waves-light col s12 tooltipped' data-position='bottom' data-delay='50' data-tooltip='application'>Show</a></div></div>";
                        content += "<div class='row margin'><div class='input-field col s12'><i class='mdi-action-turned-in prefix cyan-text text-darken-2'></i><input placeholder='computational,experimental,hybrid' readonly id='env-group-"+env["id"]+"' type='text' value='"+env["group"]+"'></div></div>";
                        content += "<div class='row margin'><div class='input-field col s12'><i class='mdi-action-subject prefix cyan-text text-darken-2'></i><input placeholder='container-based,vm-based,tool-based,cloud-based,device-based,lab-based,custom-based' readonly id='env-system-"+env["id"]+"' type='text' value='"+env["system"]+"'></div></div>";
                        
                        content += "<div class='card-action center-align'>";

                        content += "<a onclick='config.error_modal(\"Env ressources view failed\", \"Env resources view not implemented yet!\");' class='valign left tooltipped' data-position='bottom' data-delay='50' data-tooltip='resources'><i class='mdi-file-cloud-download cyan-text text-darken-2'></i><span class='from badge'>"+env["resources"]+"</span></a>";
                        content += "<a onclick='config.error_modal(\"Env comments view failed\", \"Env comments view not implemented yet!\");' class='valign right tooltipped' data-position='bottom' data-delay='50' data-tooltip='comments'><i class='mdi-editor-insert-comment cyan-text text-darken-2'></i> <span class='comments badge'>"+env["comments"]+"</span></a>";
                        content += "<a onclick='config.error_modal(\"Env bundle view failed\", \"Env bundle view not implemented yet!\");' class='valign'><i class='mdi-editor-insert-drive-file cyan-text text-darken-2 tooltipped' data-position='bottom' data-delay='50' data-tooltip='bundle'></i><span class='to badge'>"+env["bundle"].substring(0,4)+"..."+env["bundle"].substring(19,23)+"</span></a>";

                        content += "</div>";
                        content += "</div>";                
                        content += "</div>";
                        content += "</div>";
                        document.getElementById("envs-list").innerHTML += content;
                    }
                }
            } else {
                console.log("Dashboard failed");
            }
        }
    },
    this.query = function(search, exUser, exApp, exProject, exRecord, exDiff, exEnv) {
        var xmlhttp = new XMLHttpRequest();
        var query_result = document.getElementById('query-result');
        query_result.innerHTML = "<div class='progress'><div class='indeterminate'></div></div>";
        console.log('Cookie session value: '+ Cookies.get('session'));
        // console.log(this.session);
        xmlhttp.open("GET", url+"/private/"+Cookies.get('session')+"/dashboard/search?query="+search);
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
                            var picture_uri = url+"/public/user/picture/"+this.query_result["users"]["result"][i]["id"];
                            var user_content = renderer.user(this.query_result["users"]["result"][i], false, picture_uri);
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
                    if(!exDiff == true){
                        for(var i = 0; i < this.query_result["diffs"]["count"]; i++){
                            var diff_content = renderer.diff(this.query_result["diffs"]["result"][i], false);
                            query_result.innerHTML += diff_content;
                        }
                        hits += this.query_result["diffs"]["count"];
                    }
                    if(!exEnv == true){
                        for(var i = 0; i < this.query_result["envs"]["count"]; i++){
                            var env_content = renderer.env(this.query_result["envs"]["result"][i], false);
                            query_result.innerHTML += env_content;
                        }
                        hits += this.query_result["envs"]["count"];
                    }
                    var display = document.getElementById('results-display');
                    display.innerHTML = hits;
                }
            } else {
                console.log("query failed");
                config.error_modal('Query failed', xmlhttp.responseText);
                // Materialize.toast('<span>Query failed</span>', 3000);
            }
        }   
    },
    this.exportToJson = function () {
        var xmlhttp = new XMLHttpRequest();
        console.log('Cookie session value: '+ Cookies.get('session'));
        // console.log(this.session);
        xmlhttp.open("GET", url+"/private/"+Cookies.get('session')+"/dashboard/projects");
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
        console.log('Cookie session value: '+ Cookies.get('session'));
        window.location.replace(url+"/private/"+Cookies.get('session')+"/record/pull"+"/"+record_id);
        console.log("...After");
    }
};

var Record = function (_id){
    var url = config.mode+"://"+config.host+":"+config.port+"/cloud/v0.1";
    console.log('Cookie session value: '+ Cookies.get('session'));
    // this.session = session;
    self._id = _id;
    // This way of doing is not optimal as we do not atomically update a record and change its content we reload the whole page.
    this.save = function(tags, rationels, status) {
        var xmlhttp = new XMLHttpRequest();
        console.log('Cookie session value: '+ Cookies.get('session'));
        xmlhttp.open("POST", url+"/private/"+Cookies.get('session')+"/record/edit/"+self._id);
        var request = { 'tags': tags, 'rationels': rationels, 'status': status};
        xmlhttp.send(JSON.stringify(request));
        xmlhttp.onreadystatechange=function()
        {
            if(xmlhttp.responseText == ""){
                console.log("Cloud returned empty response!");
            }else{
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    // Materialize.toast('<span>Update succeeded</span>', 3000);
                    window.location.reload();
                } else {
                    // Materialize.toast('<span>Update failed</span>', 5000);
                    config.error_modal('Update record failed', xmlhttp.responseText);
                }
            }
        }
    },
    // Half way optimal. We could have just removed the record div instead of reloading the whole page. TODO
    this.trash = function () {
        var xmlhttp = new XMLHttpRequest();
        console.log('Cookie session value: '+ Cookies.get('session'));
        // console.log(this.session);
        xmlhttp.open("GET", url+"/private/"+Cookies.get('session')+"/record/remove/"+self._id);
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if(xmlhttp.responseText == ""){
                console.log("Cloud returned empty response!");
            }else{
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    // Materialize.toast('<span>Record removal succeeded</span>', 3000);
                    window.location.reload();
                } else {
                    config.error_modal('Remove record failed', xmlhttp.responseText);
                    // Materialize.toast('<span>Record removal failed</span>', 3000);
                    console.log("Record remove failed");
                }
            }
        }
    }
};

var Project = function (_id){
    var url = config.mode+"://"+config.host+":"+config.port+"/cloud/v0.1";
    console.log('Cookie session value: '+ Cookies.get('session'));
    // this.session = session;
    self._id = _id;
    // This way of doing is not optimal as we do not atomically update a record and change its content we reload the whole page.
    this.save = function(tags, description, goals) {
        var xmlhttp = new XMLHttpRequest();
        console.log('Cookie session value: '+ Cookies.get('session'));
        xmlhttp.open("POST", url+"/private/"+Cookies.get('session')+"/project/edit/"+self._id);
        var request = { 'tags':tags, 'description': description, 'goals': goals};
        xmlhttp.send(JSON.stringify(request));
        xmlhttp.onreadystatechange=function()
        {
            if(xmlhttp.responseText == ""){
                console.log("Cloud returned empty response!");
            }else{
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    // Materialize.toast('<span>Update succeeded</span>', 3000);
                    window.location.reload();
                } else {
                    config.error_modal('Project update failed', xmlhttp.responseText);
                    // Materialize.toast('<span>Update failed</span>', 5000);
                }
            }
        }
    },
    // Half way optimal. We could have just removed the record div instead of reloading the whole page. TODO
    this.trash = function () {
        var xmlhttp = new XMLHttpRequest();
        console.log('Cookie session value: '+ Cookies.get('session'));
        // console.log(this.session);
        
        xmlhttp.open("GET", url+"/private/"+Cookies.get('session')+"/project/remove/"+self._id);
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if(xmlhttp.responseText == ""){
                console.log("Cloud returned empty response!");
            }else{
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    // Materialize.toast('<span>Record removal succeeded</span>', 3000);
                    window.location.reload();
                } else {
                    config.error_modal('Project remove failed', xmlhttp.responseText);
                    // Materialize.toast('<span>Record removal failed</span>', 3000);
                    console.log("Project remove failed");
                }
            }
        }
    }
};

var Application = function (_id){
    var url = config.mode+"://"+config.host+":"+config.port+"/cloud/v0.1";
    console.log('Cookie session value: '+ Cookies.get('session'));
    // this.session = session;
    self._id = _id;
    // This way of doing is not optimal as we do not atomically update an app and change its content we reload the whole page.
    this.save = function(name, network, about, access) {
        var xmlhttp = new XMLHttpRequest();
        console.log('Cookie session value: '+ Cookies.get('session'));
        xmlhttp.open("POST", url+"/private/"+Cookies.get('session')+"/dashboard/developer/app/update/"+self._id);
        var request = { 'name':name, 'network': network, 'about': about, 'access': access};
        xmlhttp.send(JSON.stringify(request));
        xmlhttp.onreadystatechange=function()
        {
            if(xmlhttp.responseText == ""){
                console.log("Cloud returned empty response!");
            }else{
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    // Materialize.toast('<span>Update succeeded</span>', 3000);
                    window.location.reload();
                } else {
                    config.error_modal('Application update failed', xmlhttp.responseText);
                    // Materialize.toast('<span>Update failed</span>', 5000);
                }
            }
        }
    },
    // Half way optimal. We could have just removed the app div instead of reloading the whole page. TODO
    this.trash = function () {
        var xmlhttp = new XMLHttpRequest();
        console.log('Cookie session value: '+ Cookies.get('session'));
        // console.log(this.session);
        
        xmlhttp.open("GET", url+"/private/"+Cookies.get('session')+"/dashboard/app/delete/"+self._id);
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if(xmlhttp.responseText == ""){
                console.log("Cloud returned empty response!");
            }else{
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    // Materialize.toast('<span>Record removal succeeded</span>', 3000);
                    window.location.reload();
                } else {
                    config.error_modal('Record remove failed', xmlhttp.responseText);
                    // Materialize.toast('<span>Record removal failed</span>', 3000);
                    console.log("Record remove failed");
                }
            }
        }
    }
};

var Diff = function (_id){
    var url = config.mode+"://"+config.host+":"+config.port+"/cloud/v0.1";
    console.log('Cookie session value: '+ Cookies.get('session'));
    // this.session = session;
    self._id = _id;
    // This way of doing is not optimal as we do not atomically update a diff and change its content we reload the whole page.
    this.save = function(method, proposition, status) {
        var xmlhttp = new XMLHttpRequest();
        console.log('Cookie session value: '+ Cookies.get('session'));
        xmlhttp.open("POST", url+"/private/"+Cookies.get('session')+"/diff/edit/"+self._id);
        var request = { 'method':method, 'proposition': proposition, 'status': status};
        xmlhttp.send(JSON.stringify(request));
        xmlhttp.onreadystatechange=function()
        {
            if(xmlhttp.responseText == ""){
                console.log("Cloud returned empty response!");
            }else{
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    // Materialize.toast('<span>Update succeeded</span>', 3000);
                    window.location.reload();
                } else {
                    config.error_modal('Diff update failed', xmlhttp.responseText);
                    // Materialize.toast('<span>Update failed</span>', 5000);
                }
            }
        }
    },
    // Half way optimal. We could have just removed the diff div instead of reloading the whole page. TODO
    this.trash = function () {
        var xmlhttp = new XMLHttpRequest();
        console.log('Cookie session value: '+ Cookies.get('session'));
        // console.log(this.session);
        
        xmlhttp.open("GET", url+"/private/"+Cookies.get('session')+"/diff/remove/"+self._id);
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if(xmlhttp.responseText == ""){
                console.log("Cloud returned empty response!");
            }else{
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    // Materialize.toast('<span>Record removal succeeded</span>', 3000);
                    window.location.reload();
                } else {
                    config.error_modal('Diff remove failed', xmlhttp.responseText);
                    // Materialize.toast('<span>Record removal failed</span>', 3000);
                    console.log("Diff remove failed");
                }
            }
        }
    }
};

var Environment = function (_id){
    var url = config.mode+"://"+config.host+":"+config.port+"/cloud/v0.1";
    console.log('Cookie session value: '+ Cookies.get('session'));
    // this.session = session;
    self._id = _id;
    // This way of doing is not optimal as we do not atomically update a env and change its content we reload the whole page.
    this.save = function(group, system) {
        var xmlhttp = new XMLHttpRequest();
        console.log('Cookie session value: '+ Cookies.get('session'));
        xmlhttp.open("POST", url+"/private/"+Cookies.get('session')+"/env/edit/"+self._id);
        var request = { 'group':group, 'system': system};
        xmlhttp.send(JSON.stringify(request));
        xmlhttp.onreadystatechange=function()
        {
            if(xmlhttp.responseText == ""){
                console.log("Cloud returned empty response!");
            }else{
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    // Materialize.toast('<span>Update succeeded</span>', 3000);
                    window.location.reload();
                } else {
                    // Materialize.toast('<span>Update failed</span>', 5000);
                    config.error_modal('Environment update failed', xmlhttp.responseText);
                }
            }
        }
    },
    // Half way optimal. We could have just removed the env div instead of reloading the whole page. TODO
    this.trash = function () {
        var xmlhttp = new XMLHttpRequest();
        console.log('Cookie session value: '+ Cookies.get('session'));
        // console.log(this.session);
        
        xmlhttp.open("GET", url+"/private/"+Cookies.get('session')+"/env/remove/"+self._id);
        xmlhttp.send();
        xmlhttp.onreadystatechange=function()
        {
            if(xmlhttp.responseText == ""){
                console.log("Cloud returned empty response!");
            }else{
                if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
                    // Materialize.toast('<span>Record removal succeeded</span>', 3000);
                    window.location.reload();
                } else {
                    config.error_modal('Environment remove failed', xmlhttp.responseText);
                    // Materialize.toast('<span>Environment removal failed</span>', 3000);
                    console.log("Environment remove failed");
                }
            }
        }
    }
};