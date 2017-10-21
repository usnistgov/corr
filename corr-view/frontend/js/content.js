var Space = function (){
    var url = config.mode+"://"+config.host+":"+config.port+"/cloud/v0.1";
    this.dash_content = "";
    this.query_result = "";
    this.dashboard = function(page) {
        var circular_loader = "<div class='preloader-wrapper big active'><div class='spinner-layer spinner-cyan-only'><div class='circle-clipper left'><div class='circle'></div></div><div class='gap-patch'><div class='circle'></div></div><div class='circle-clipper right'><div class='circle'></div></div></div></div>";
        var linear_loader = "<div class='progress'><div class='indeterminate'></div></div>";
        var corr_base = location.protocol + '//' + location.host + '/';
        if(parseInt(page) == 0){
            document.getElementById("projects-list").innerHTML = linear_loader;
            document.getElementById("temporal-slider").innerHTML = "";
        }else if(parseInt(page) > 0){
            document.getElementById("load-more-projects-block").innerHTML = linear_loader;
        }else{
            document.getElementById("projects-list").innerHTML = linear_loader;
        }
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {
                    if(parseInt(page) == 0){
                        document.getElementById("projects-list").innerHTML = "";
                    }else if(parseInt(page) > 0){
                        var loadMoreEl = document.getElementById("load-more-projects-block");
                        loadMoreEl.parentNode.removeChild(loadMoreEl);
                    }else{
                        document.getElementById("projects-list").innerHTML = "";
                    }

                    var response = JSON.parse(this.responseText);
                    this.dash_content = response;
                    var version = response["version"];
                    var end = response["end"];

                    for(var i = 0; i < response["projects"].length; i++){
                        project = response["projects"][i];
                        var disable_view = "";
                        if(project["project"]["records"] == 0){
                            disable_view = "disabled";
                        }

                        var accessible = false;
                        if(project["project"]["access"] == "public"){
                            accessible = true;
                        }

                        function succeed(xhttp, params){
                            var content = xhttp.responseText;
                            if(document.getElementById("update-project"+params[1]) == null){
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
                        var content = "<div class='col s12 m6 l4' id='project-block-"+project["project"]["id"]+"'>";
                        content += "<div id='profile-card' class='card'>";
                        content += "<div class='card-image waves-effect waves-block waves-light'><img disabled class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
                        content += "<div class='card-content'>";

                        content += "<img src='../images/project.png' alt='' class='circle responsive-img activator card-profile-image'>";
                        content += "<a onclick='projectRemove(\""+project["project"]["name"]+"\",\""+project["project"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='delete'><i class='mdi-action-delete'></i></a>";
                        content += "<a onclick='launchRecordModal(\""+project["project"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='download'><i class='mdi-file-cloud-upload'></i></a>";
                        content += "<a onclick='launchEnvModal(\""+project["project"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='environment'><i class='mdi-maps-layers'></i></a>";
                        content += "<div id='update-project-"+project["project"]["id"]+"'><a id='update-action' onclick='projectEdit(\""+project["project"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='edit and save'><i class='mdi-editor-mode-edit'></i></a></div>";
                        content += "<a onclick='config.error_modal(\"Project details failed\", \"Project details not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='details'><i class='mdi-action-visibility'></i></a>";
                        content += "<a href='"+corr_base+"share/?type=project&id="+project["id"]+"' target='_blank' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='share'><i class='mdi-social-share'></i></a>";

                        if(Cookies.get("group") == "admin"){
                            content += "<a onclick='userViewModal(\""+project["project"]["owner"]["id"]+"\",\""+project["project"]["owner"]["profile"]["fname"]+"\""+",\""+project["project"]["owner"]["profile"]["lname"]+"\",\""+project["project"]["owner"]["profile"]["organisation"]+"\",\""+project["project"]["owner"]["profile"]["about"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='"+project["project"]["owner"]["profile"]["fname"]+"'><i class='mdi-social-person'></i></a>";
                        }

                        content += "<span class='card-title black-text text-darken-4'> "+project["project"]["name"]+"</span>";
                        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+project["project"]["created"]+"</p>";
                        if(accessible){
                            content += "<div class='row margin'><div class='switch col s12'><i class='mdi-social-public prefix cyan-text text-darken-2'></i> <label>Private <input id='project-access-"+project["project"]["id"]+"' onclick='projectAccess(\""+project["project"]["id"]+"\");' type='checkbox' checked><span class='lever'></span> Public</label></div></div>";
                        }else{
                            content += "<div class='row margin'><div class='switch col s12'><i class='mdi-social-public prefix cyan-text text-darken-2'></i> <label>Private <input id='project-access-"+project["project"]["id"]+"' onclick='projectAccess(\""+project["project"]["id"]+"\");' type='checkbox'><span class='lever'></span></label> Public</div></div>";
                        }
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-turned-in prefix cyan-text text-darken-2'></i><input readonly id='project-tags-"+project["project"]["id"]+"' type='text' value='"+project["project"]["tags"]+"'></div></div>";
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='description'><div class='input-field col s12'><i class='mdi-action-description prefix cyan-text text-darken-2'></i><input readonly id='project-desc-"+project["project"]["id"]+"' type='text' value='"+project["project"]["description"]+"'></div></div>";
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='goals'><div class='input-field col s12'><i class='mdi-action-subject prefix cyan-text text-darken-2'></i><input readonly id='project-goals-"+project["project"]["id"]+"' type='text' value='"+project["project"]["goals"]+"'></div></div>";
                        content += "<div class='card-action center-align'>";
                        content += "<a href='./?view=records&project="+project["project"]["id"]+"&page=0' class='valign left tooltipped' data-position='bottom' data-delay='50' data-tooltip='records'><i class='mdi-file-cloud-upload cyan-text text-darken-2'></i> <span class='records badge'>"+project["project"]["records"]+"</span></a>";
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
                    // Add load more to the end.
                    if(end != -1){
                        var next_Page = parseInt(page)+1;
                         if(parseInt(page) == 0){
                            document.getElementById("projects-list").innerHTML += "<div id='load-more-projects-block' class='col s12 m12 l12 center'><a onclick='space.dashboard(1);' class='btn-floating btn-large waves-effect waves-light tooltipped cyan' data-position='top' data-delay='50' data-tooltip='Load More'><i class='mdi-hardware-keyboard-arrow-down'></i></a></div>";
                        }else if(parseInt(page) > 0){
                            document.getElementById("projects-list").innerHTML += "<div id='load-more-projects-block' class='col s12 m12 l12 center'><a onclick='space.dashboard("+next_Page+");' class='btn-floating btn-large waves-effect waves-light tooltipped cyan' data-position='top' data-delay='50' data-tooltip='Load More'><i class='mdi-hardware-keyboard-arrow-down'></i></a></div>";
                        }else{
                            document.getElementById("projects-list").innerHTML += "<div id='load-more-projects-block' class='col s12 m12 l12 center'><a onclick='space.dashboard(1);' class='btn-floating btn-large waves-effect waves-light tooltipped cyan' data-position='top' data-delay='50' data-tooltip='Load More'><i class='mdi-hardware-keyboard-arrow-down'></i></a></div>";
                        }
                    }
                }else{
                    config.error_modal('Dashboard home failed', this.responseText);
                }
            }
        };
        xmlhttp.open("GET", url+"/private/dashboard/projects?page="+page);
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        xmlhttp.send();
    },
    this.users = function(page) {
        var circular_loader = "<div class='preloader-wrapper big active'><div class='spinner-layer spinner-cyan-only'><div class='circle-clipper left'><div class='circle'></div></div><div class='gap-patch'><div class='circle'></div></div><div class='circle-clipper right'><div class='circle'></div></div></div></div>";
        var linear_loader = "<div class='progress'><div class='indeterminate'></div></div>";
        var corr_base = location.protocol + '//' + location.host + '/';
        if(parseInt(page) == 0){
            document.getElementById("users-list").innerHTML = linear_loader;
            document.getElementById("temporal-slider").innerHTML = "";
        }else if(parseInt(page) > 0){
            document.getElementById("load-more-users-block").innerHTML = linear_loader;
        }else{
            document.getElementById("users-list").innerHTML = linear_loader;
        }
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {
                    if(parseInt(page) == 0){
                        document.getElementById("users-list").innerHTML = "";
                    }else if(parseInt(page) > 0){
                        var loadMoreEl = document.getElementById("load-more-users-block");
                        loadMoreEl.parentNode.removeChild(loadMoreEl);
                    }else{
                        document.getElementById("users-list").innerHTML = "";
                    }

                    var response = JSON.parse(this.responseText);
                    this.dash_content = response;
                    var version = response["version"];
                    var end = response["end"];
                    
                    for(var i = 0; i < response["users"].length; i++){
                        account = response["users"][i];

                        var picture_uri = url+"/public/user/picture/"+account["id"];

                        var content = "<div class='col s12 m6 l4 id='user-block-"+account["id"]+"'>";
                        content += "<div id='profile-card' class='card'>";
                        content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
                        content += "<div class='card-content'>";
                        content += "<img src='"+picture_uri+"' alt='' class='circle responsive-img activator card-profile-image'>";
                        content += "<div id='update-user-"+account["id"]+"'><a id='update-action' onclick='userEdit(\""+account["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='edit'><i class='mdi-editor-mode-edit'></i></a></div>";
                        content += "<a onclick='config.error_modal(\"User details failed.\", \"User details not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='details'><i class='mdi-action-visibility'></i></a>";
                        content += "<a href='"+corr_base+"share/?type=user&id="+account["id"]+"' target='_blank' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='share'><i class='mdi-social-share'></i></a>";

                        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+account["created"]+"</p>";
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-perm-identity prefix cyan-text text-darken-2'></i><input readonly id='user-fname-"+account["id"]+"' type='text' value='"+account["fname"]+"'></div></div>";
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-assignment-ind prefix cyan-text text-darken-2'></i><input readonly id='user-lname-"+account["id"]+"' type='text' value='"+account["lname"]+"'></div></div>";
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-picture-in-picture prefix cyan-text text-darken-2'></i><input readonly placeholder='unregistered,blocked,approved,signup' id='user-auth-"+account["id"]+"' type='text' value='"+account["auth"]+"'></div></div>";
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-communication-vpn-key prefix cyan-text text-darken-2'></i><input readonly id='user-password-"+account["id"]+"' type='text' value=''></div></div>";

                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-assessment prefix cyan-text text-darken-2'></i><input readonly placeholder='%' id='user-usage-"+account["id"]+"' type='text' value='"+account["usage"]+"%'></div></div>";
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-notification-disc-full prefix cyan-text text-darken-2'></i><input readonly placeholder='in GB' id='user-quota-"+account["id"]+"' type='text' value='"+account["max-quota"]+"GB'></div></div>";
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
                    }
                    document.getElementById("footer-version").innerHTML = version;
                    // Add load more to the end.
                    if(end != -1){
                        var next_Page = parseInt(page)+1;
                         if(parseInt(page) == 0){
                            document.getElementById("users-list").innerHTML += "<div id='load-more-users-block' class='col s12 m12 l12 center'><a onclick='space.users(1);' class='btn-floating btn-large waves-effect waves-light tooltipped cyan' data-position='top' data-delay='50' data-tooltip='Load More'><i class='mdi-hardware-keyboard-arrow-down'></i></a></div>";
                        }else if(parseInt(page) > 0){
                            document.getElementById("users-list").innerHTML += "<div id='load-more-users-block' class='col s12 m12 l12 center'><a onclick='space.users("+next_Page+");' class='btn-floating btn-large waves-effect waves-light tooltipped cyan' data-position='top' data-delay='50' data-tooltip='Load More'><i class='mdi-hardware-keyboard-arrow-down'></i></a></div>";
                        }else{
                            document.getElementById("users-list").innerHTML += "<div id='load-more-users-block' class='col s12 m12 l12 center'><a onclick='space.users(1);' class='btn-floating btn-large waves-effect waves-light tooltipped cyan' data-position='top' data-delay='50' data-tooltip='Load More'><i class='mdi-hardware-keyboard-arrow-down'></i></a></div>";
                        }
                    }
                }else{
                    config.error_modal('Dashboard users failed', this.responseText);
                }
            }
        };
        xmlhttp.open("GET", url+"/private/dashboard/users?page="+page);
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        xmlhttp.send();
    },
    this.apps = function() {
        var xmlhttp = new XMLHttpRequest();
        var corr_base = location.protocol + '//' + location.host + '/';
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {
                    var response = JSON.parse(this.responseText);
                    this.dash_content = response;
                    document.getElementById("apps-list").innerHTML = "";
                    for(var i = 0; i < response["content"]["apps"].length; i++){
                        app = response["content"]["apps"][i];
                        var disable_view = "";
                        function succeed(xhttp, params){
                            var content = xhttp.responseText;
                            if(document.getElementById("update-app"+params[1]) == null){
                                content = content.replace(/app_id/g, params[1]);
                                content = content.replace(/app_name/g, params[2]);
                                content = content.replace(/app_created/g, params[3]);
                                content = content.replace(/app_access/g, params[5]);
                                content = content.replace(/app_storage/g, params[6]);
                                content = content.replace(/app_token/g, params[7]);
                                content = content.replace(/app_about/g, params[8]);
                            }
                        };
                        function failed(){
                            window.location.replace("/error/?code=404");
                        };

                        var params = [app["id"], app["name"], app["created"], app["access"], app["storage"], app["token"], app["about"]];
                        var content = "<div class='col s12 m6 l4' id='app-block-"+app["id"]+"'>";
                        content += "<div id='profile-card' class='card'>";
                        content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
                        content += "<div class='card-content'>";
                        content += "<img src='../images/gearsIcon.png' alt='' class='circle responsive-img activator card-profile-image'>";
                        if(Cookies.get('group') == "admin"){
                            content += "<a onclick='appRemove(\""+app["name"]+"\",\""+app["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='delete'><i class='mdi-action-delete'></i></a>";
                            content += "<a onclick='appRetoken(\""+app["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='retoken'><i class='mdi-communication-vpn-key'></i></a>";
                        }
                        // Downloads only the credentials for now.
                        // Next make it download the tool itself too. ;-)
                        content += "<a onclick='return user.config(\""+app["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='download'><i class='mdi-file-cloud-download'></i></a>";
                        if(Cookies.get('group') == "admin"){
                            content += "<div id='update-app-"+app["id"]+"'><a id='update-action' onclick='appEdit(\""+app["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='edit'><i class='mdi-editor-mode-edit'></i></a></div>";
                        }
                        content += "<a onclick='config.error_modal(\"Application details failed\", \"Application details not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='details'><i class='mdi-action-visibility'></i></a>";
                        content += "<a href='"+corr_base+"share/?type=app&id="+app["id"]+"' target='_blank' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='share'><i class='mdi-social-share'></i></a>";

                        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+app["created"]+"</p>";
                        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-turned-in prefix cyan-text text-darken-2'></i><input readonly id='app-name-"+app["id"]+"' type='text' value='"+app["name"]+"'></div></div>";
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
                }else{
                    config.error_modal('Dashboard apps failed', this.responseText);
                }
            }
        };
        xmlhttp.open("GET", url+"/private/dashboard/developer/apps");
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        xmlhttp.send();
    },
    this.records = function(project_id, page) {
        var circular_loader = "<div class='preloader-wrapper big active'><div class='spinner-layer spinner-cyan-only'><div class='circle-clipper left'><div class='circle'></div></div><div class='gap-patch'><div class='circle'></div></div><div class='circle-clipper right'><div class='circle'></div></div></div></div>";
        var linear_loader = "<div class='progress'><div class='indeterminate'></div></div>";
        var corr_base = location.protocol + '//' + location.host + '/';
        if(parseInt(page) == 0){
            document.getElementById("records-list").innerHTML = linear_loader;
            document.getElementById("temporal-slider").innerHTML = "";
        }else if(parseInt(page) > 0){
            document.getElementById("load-more-records-block").innerHTML = linear_loader;
        }else{
            document.getElementById("records-list").innerHTML = linear_loader;
        }
        
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {
                    var response = JSON.parse(this.responseText);
                    if(parseInt(page) == 0){
                        document.getElementById("records-list").innerHTML = "";
                    }else if(parseInt(page) > 0){
                        var loadMoreEl = document.getElementById("load-more-records-block");
                        loadMoreEl.parentNode.removeChild(loadMoreEl);
                    }else{
                        document.getElementById("records-list").innerHTML = "";
                    }
                    
                    this.dash_content = response;
                    var records = response["records"];
                    var selected_records = [];
                    var end = response["end"];
                    
                    for(var i = 0; i < response["records"].length; i++){
                        record = response["records"][i];
                        var content = "<div class='col s12 m6 l4' id='record-block-"+record["head"]["id"]+"'> ";
                        content += "<div id='profile-card' class='card'>";
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

                        content += "<div id='update-record-"+record["head"]["id"]+"'><a id='update-action' onclick='recordEdit(\""+record["head"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='edit'><i class='mdi-editor-mode-edit'></i></a></div>";
                        content += "<a onclick='config.error_modal(\"Record details failed\", \"Record details not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='details'><i class='mdi-action-visibility'></i></a>";

                        content += "<a onclick='projectViewModal(\""+record["head"]["project"]["name"]+"\",\""+record["head"]["project"]["tags"]+"\",\""+record["head"]["project"]["description"]+"\",\""+record["head"]["project"]["goals"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='"+record["head"]["project"]["name"]+"'><i class='mdi-file-folder'></i></a>";

                        if(Cookies.get("group") == "admin"){
                            content += "<a onclick='userViewModal(\""+record["head"]["project"]["owner"]["id"]+"\",\""+record["head"]["project"]["owner"]["profile"]["fname"]+"\""+",\""+record["head"]["project"]["owner"]["profile"]["lname"]+"\",\""+record["head"]["project"]["owner"]["profile"]["organisation"]+"\",\""+record["head"]["project"]["owner"]["profile"]["about"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='"+record["head"]["project"]["owner"]["profile"]["fname"]+"'><i class='mdi-social-person'></i></a>";
                        }

                        content += "<a href='"+corr_base+"share/?type=record&id="+record["head"]["id"]+"' target='_blank' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='share'><i class='mdi-social-share'></i></a>";

                        content += "<div id='select-record-"+record["head"]["id"]+"'><a id='select-action' onclick='recordSelect(\""+record["head"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='select'><i class='mdi-toggle-check-box-outline-blank'></i></a></div>";

                        content += "<span class='card-title grey-text text-darken-4'>"+record["head"]["id"]+"</span>";
                        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+record["head"]["created"]+"</p>";
                        content += "<p><i class='mdi-action-restore cyan-text text-darken-2'></i> "+record["head"]["duration"].split(",")[0].split(".")[0]+" ago.</p>";
                        
                        if(accessible){
                            content += "<div class='row margin'><div class='switch col s12'><i class='mdi-social-public prefix cyan-text text-darken-2'></i> <label>Private <input id='record-access-"+record["head"]["id"]+"' onclick='recordAccess(\""+record["head"]["id"]+"\");' type='checkbox' checked><span class='lever'></span> Public</label></div></div>";
                        }else{
                            content += "<div class='row margin'><div class='switch col s12'><i class='mdi-social-public prefix cyan-text text-darken-2'></i> <label>Private <input id='record-access-"+record["head"]["id"]+"' onclick='recordAccess(\""+record["head"]["id"]+"\");' type='checkbox'><span class='lever'></span> Public</label></div></div>";
                        }

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
                    // Add load more to the end.
                    if(end != -1){
                        var next_Page = parseInt(page)+1;
                         if(parseInt(page) == 0){
                            document.getElementById("records-list").innerHTML += "<div id='load-more-records-block' class='col s12 m12 l12 center'><a onclick='space.records(\""+project_id+"\", 1);' class='btn-floating btn-large waves-effect waves-light tooltipped cyan' data-position='top' data-delay='50' data-tooltip='Load More'><i class='mdi-hardware-keyboard-arrow-down'></i></a></div>";
                        }else if(parseInt(page) > 0){
                            document.getElementById("records-list").innerHTML += "<div id='load-more-records-block' class='col s12 m12 l12 center'><a onclick='space.records(\""+project_id+"\", "+next_Page+");' class='btn-floating btn-large waves-effect waves-light tooltipped cyan' data-position='top' data-delay='50' data-tooltip='Load More'><i class='mdi-hardware-keyboard-arrow-down'></i></a></div>";
                        }else{
                            document.getElementById("records-list").innerHTML += "<div id='load-more-records-block' class='col s12 m12 l12 center'><a onclick='space.records(\""+project_id+"\", 1);' class='btn-floating btn-large waves-effect waves-light tooltipped cyan' data-position='top' data-delay='50' data-tooltip='Load More'><i class='mdi-hardware-keyboard-arrow-down'></i></a></div>";
                        }
                        
                        // Add a button to load more.
                    }
                }else{
                    config.error_modal('Dashboard records failed', this.responseText);
                }
            }
        };
        if(project_id == "all"){
            xmlhttp.open("GET", url+"/private/dashboard/records/all?page="+page);
        }else{
            xmlhttp.open("GET", url+"/private/dashboard/records/"+project_id+"?page="+page);
        }
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        xmlhttp.send();
    },
    this.diffs = function(project_id, page) {
        var circular_loader = "<div class='preloader-wrapper big active'><div class='spinner-layer spinner-cyan-only'><div class='circle-clipper left'><div class='circle'></div></div><div class='gap-patch'><div class='circle'></div></div><div class='circle-clipper right'><div class='circle'></div></div></div></div>";
        var linear_loader = "<div class='progress'><div class='indeterminate'></div></div>";
        var corr_base = location.protocol + '//' + location.host + '/';
        if(parseInt(page) == 0){
            document.getElementById("diffs-list").innerHTML = linear_loader;
            document.getElementById("temporal-slider").innerHTML = "";
        }else if(parseInt(page) > 0){
            document.getElementById("load-more-diffs-block").innerHTML = linear_loader;
        }else{
            document.getElementById("diffs-list").innerHTML = linear_loader;
        }
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {

                    if(parseInt(page) == 0){
                        document.getElementById("diffs-list").innerHTML = "";
                    }else if(parseInt(page) > 0){
                        var loadMoreEl = document.getElementById("load-more-diffs-block");
                        loadMoreEl.parentNode.removeChild(loadMoreEl);
                    }else{
                        document.getElementById("diffs-list").innerHTML = "";
                    }

                    var response = JSON.parse(this.responseText);
                    this.dash_content = response;
                    var end = response["end"];
                    
                    for(var i = 0; i < response["number"]; i++){
                        diff = response["diffs"][i];
                        var content = "<div class='col s12 m6 l4' id='diff-block-"+diff["id"]+"'> ";
                        content += "<div id='profile-card' class='card'>";
                        content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
                        content += "<div class='card-content'>";
                        content += "<img src='../images/diff.png' alt='' class='circle responsive-img activator card-profile-image'>";
                        content += "<a onclick='diffRemove(\""+diff["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-action-delete'></i></a>";
                        content += "<a onclick='config.error_modal(\"Diff comment failed\", \"Diff comment not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='comment'><i class='mdi-editor-insert-comment'></i></a>";
                        content += "<a onclick=\"space.pull_diff('"+diff["id"]+"');\" class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='download'><i class='mdi-file-cloud-download'></i></a>";
                        content += "<div id='update-diff-"+diff["id"]+"'><a id='update-action' onclick='diffEdit(\""+diff["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='edit'><i class='mdi-editor-mode-edit'></i></a></div>";
                        content += "<a onclick='config.error_modal(\"Diff details failed\", \"Diff details not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='details'><i class='mdi-action-visibility'></i></a>";

                        if(Cookies.get("group") == "admin"){
                            var record_from = diff["from"];
                            var record_to = diff["to"];
                            content += "<a onclick='userViewModal(\""+record_from["head"]["project"]["owner"]["id"]+"\",\""+record_from["head"]["project"]["owner"]["profile"]["fname"]+"\""+",\""+record_from["head"]["project"]["owner"]["profile"]["lname"]+"\",\""+record_from["head"]["project"]["owner"]["profile"]["organisation"]+"\",\""+record_from["head"]["project"]["owner"]["profile"]["about"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='"+record_from["head"]["project"]["owner"]["profile"]["fname"]+"'><i class='mdi-social-person'></i></a>";
                            content += "<a onclick='userViewModal(\""+record_to["head"]["project"]["owner"]["id"]+"\",\""+record_to["head"]["project"]["owner"]["profile"]["fname"]+"\""+",\""+record_to["head"]["project"]["owner"]["profile"]["lname"]+"\",\""+record_to["head"]["project"]["owner"]["profile"]["organisation"]+"\",\""+record_to["head"]["project"]["owner"]["profile"]["about"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='"+record_to["head"]["project"]["owner"]["profile"]["fname"]+"'><i class='mdi-social-person'></i></a>";
                        }
                        content += "<a href='"+corr_base+"share/?type=diff&id="+diff["id"]+"' target='_blank' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='share'><i class='mdi-social-share'></i></a>";
                        content += "<span class='card-title grey-text text-darken-4'>"+diff["id"]+"</span>";
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
                    // Add load more to the end.
                    if(end != -1){
                        var next_Page = parseInt(page)+1;
                         if(parseInt(page) == 0){
                            document.getElementById("diffs-list").innerHTML += "<div id='load-more-diffs-block' class='col s12 m12 l12 center'><a onclick='space.diffs(\""+project_id+"\", 1);' class='btn-floating btn-large waves-effect waves-light tooltipped cyan' data-position='top' data-delay='50' data-tooltip='Load More'><i class='mdi-hardware-keyboard-arrow-down'></i></a></div>";
                        }else if(parseInt(page) > 0){
                            document.getElementById("diffs-list").innerHTML += "<div id='load-more-diffs-block' class='col s12 m12 l12 center'><a onclick='space.diffs(\""+project_id+"\", "+next_Page+");' class='btn-floating btn-large waves-effect waves-light tooltipped cyan' data-position='top' data-delay='50' data-tooltip='Load More'><i class='mdi-hardware-keyboard-arrow-down'></i></a></div>";
                        }else{
                            document.getElementById("diffs-list").innerHTML += "<div id='load-more-diffs-block' class='col s12 m12 l12 center'><a onclick='space.diffs(\""+project_id+"\", 1);' class='btn-floating btn-large waves-effect waves-light tooltipped cyan' data-position='top' data-delay='50' data-tooltip='Load More'><i class='mdi-hardware-keyboard-arrow-down'></i></a></div>";
                        }
                        
                        // Add a button to load more.
                    }
                }else{
                    config.error_modal('Dashboard diffs failed', this.responseText);
                }
            }
        };
        if(project_id == "all"){
            xmlhttp.open("GET", url+"/private/dashboard/diffs/all?page="+page);
        }else{
            xmlhttp.open("GET", url+"/private/dashboard/diffs/"+project_id+"?page="+page);
        }
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        xmlhttp.send();
    },
    this.envs = function(project_id, page) {
        var circular_loader = "<div class='preloader-wrapper big active'><div class='spinner-layer spinner-cyan-only'><div class='circle-clipper left'><div class='circle'></div></div><div class='gap-patch'><div class='circle'></div></div><div class='circle-clipper right'><div class='circle'></div></div></div></div>";
        var linear_loader = "<div class='progress'><div class='indeterminate'></div></div>";
        var corr_base = location.protocol + '//' + location.host + '/';

        if(parseInt(page) == 0){
            document.getElementById("envs-list").innerHTML = linear_loader;
            document.getElementById("temporal-slider").innerHTML = "";
        }else if(parseInt(page) > 0){
            document.getElementById("load-more-envs-block").innerHTML = linear_loader;
        }else{
            document.getElementById("envs-list").innerHTML = linear_loader;
        }
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {
                    if(parseInt(page) == 0){
                        document.getElementById("envs-list").innerHTML = "";
                    }else if(parseInt(page) > 0){
                        var loadMoreEl = document.getElementById("load-more-envs-block");
                        loadMoreEl.parentNode.removeChild(loadMoreEl);
                    }else{
                        document.getElementById("envs-list").innerHTML = "";
                    }

                    var response = JSON.parse(this.responseText);
                    this.dash_content = response;
                    var envs = response["envs"];
                    var end = response["end"];
                    
                    for(var i = 0; i < response["envs"].length; i++){
                        env = response["envs"][i];
                        var content = "<div class='col s12 m6 l4' id='env-block-"+env["id"]+"'> ";
                        content += "<div id='profile-card' class='card'>";
                        content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
                        content += "<div class='card-content'>";
                        content += "<img src='../images/env.png' alt='' class='circle responsive-img activator card-profile-image'>";
                        content += "<a onclick='envRemove(\""+env["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='delete'><i class='mdi-action-delete'></i></a>";
                        content += "<a onclick=\"space.pull_env('"+env["id"]+"');\" class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='download'><i class='mdi-file-cloud-download'></i></a>";
                        content += "<div id='update-env-"+env["id"]+"'><a id='update-action' onclick='envEdit(\""+env["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='edit'><i class='mdi-editor-mode-edit'></i></a></div>";
                        content += "<a onclick='config.error_modal(\"Environment details failed\", \"Environment details not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='details'><i class='mdi-action-visibility'></i></a>";
                        content += "<a href='"+corr_base+"share/?type=env&id="+env["id"]+"' target='_blank' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='share'><i class='mdi-social-share'></i></a>";

                        if(Cookies.get("group") == "admin"){
                            content += "<a onclick='projectViewModal(\""+env["project"]["name"]+"\",\""+env["project"]["tags"]+"\",\""+env["project"]["description"]+"\",\""+env["project"]["goals"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='"+env["project"]["name"]+"'><i class='mdi-file-folder'></i></a>";                        
                        }

                        content += "<span class='card-title grey-text text-darken-4'>"+env["id"]+"</span>";
                        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+env["created"]+"</p>";
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
                    // Add load more to the end.
                    if(end != -1){
                        var next_Page = parseInt(page)+1;
                         if(parseInt(page) == 0){
                            document.getElementById("envs-list").innerHTML += "<div id='load-more-envs-block' class='col s12 m12 l12 center'><a onclick='space.envs(\""+project_id+"\", 1);' class='btn-floating btn-large waves-effect waves-light tooltipped cyan' data-position='top' data-delay='50' data-tooltip='Load More'><i class='mdi-hardware-keyboard-arrow-down'></i></a></div>";
                        }else if(parseInt(page) > 0){
                            document.getElementById("envs-list").innerHTML += "<div id='load-more-envs-block' class='col s12 m12 l12 center'><a onclick='space.envs(\""+project_id+"\", "+next_Page+");' class='btn-floating btn-large waves-effect waves-light tooltipped cyan' data-position='top' data-delay='50' data-tooltip='Load More'><i class='mdi-hardware-keyboard-arrow-down'></i></a></div>";
                        }else{
                            document.getElementById("envs-list").innerHTML += "<div id='load-more-envs-block' class='col s12 m12 l12 center'><a onclick='space.envs(\""+project_id+"\", 1);' class='btn-floating btn-large waves-effect waves-light tooltipped cyan' data-position='top' data-delay='50' data-tooltip='Load More'><i class='mdi-hardware-keyboard-arrow-down'></i></a></div>";
                        }
                        
                        // Add a button to load more.
                    }
                } else{
                    config.error_modal('Dashboard envs failed', this.responseText);
                }
            }
        };
        if(project_id == "all"){
            xmlhttp.open("GET", url+"/private/dashboard/envs/all?page="+page);
        }else{
            xmlhttp.open("GET", url+"/private/dashboard/envs/"+project_id+"?page="+page);
        }
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        xmlhttp.send();
    },
    this.query = function(search, exUser, exApp, exProject, exRecord, exDiff, exEnv, public, page) {
        var circular_loader = "<div class='preloader-wrapper big active'><div class='spinner-layer spinner-cyan-only'><div class='circle-clipper left'><div class='circle'></div></div><div class='gap-patch'><div class='circle'></div></div><div class='circle-clipper right'><div class='circle'></div></div></div></div>";
        var linear_loader = "<div class='progress'><div class='indeterminate'></div></div>";
        var corr_base = location.protocol + '//' + location.host + '/';
        var query_result = document.getElementById('query-result');
        if(parseInt(page) == 0){
            hits = 0;
            query_result.innerHTML = linear_loader;
        }else if(parseInt(page) > 0){
            document.getElementById("load-more-search-block").innerHTML = linear_loader;
        }else{
            hits = 0;
            query_result.innerHTML = linear_loader;
        }
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {
                    if(parseInt(page) == 0){
                        query_result.innerHTML = "";
                    }else if(parseInt(page) > 0){
                        var loadMoreEl = document.getElementById("load-more-search-block");
                        loadMoreEl.parentNode.removeChild(loadMoreEl);
                    }else{
                        query_result.innerHTML = "";
                    }
                    var response = JSON.parse(this.responseText);
                    var end = response["content"]["end"];
                    if(response["code"] == 500){
                        config.error_modal('Query failed', response["content"]);
                    }else{
                        this.query_result = response["content"];
                        console.log(this.query_result);
                        if(!exUser == true || exRecord == "false"){
                            for(var i = 0; i < this.query_result["users"]["count"]; i++){
                                var picture_uri = url+"/public/user/picture/"+this.query_result["users"]["result"][i]["id"];
                                var user_content = renderer.user(this.query_result["users"]["result"][i], false, picture_uri);
                                query_result.innerHTML += user_content;
                            }
                            hits += this.query_result["users"]["count"];
                        }
                        if(!exApp == true || exApp == "false"){
                            for(var i = 0; i < this.query_result["applications"]["count"]; i++){
                                var app_content = renderer.application(this.query_result["applications"]["result"][i], false);
                                query_result.innerHTML += app_content;
                            }
                            hits += this.query_result["applications"]["count"];
                        }
                        if(!exProject == true || exProject == "false"){
                            for(var i = 0; i < this.query_result["projects"]["count"]; i++){
                                var project_content = renderer.project(this.query_result["projects"]["result"][i], false);
                                query_result.innerHTML += project_content;
                            }
                            hits += this.query_result["projects"]["count"];
                        }
                        if(!exRecord == true || exRecord == "false"){
                            for(var i = 0; i < this.query_result["records"]["count"]; i++){
                                var record_content = renderer.record(this.query_result["records"]["result"][i], false, public);
                                query_result.innerHTML += record_content;
                            }
                            hits += this.query_result["records"]["count"];
                        }
                        if(!exDiff == true || exDiff == "false"){
                            for(var i = 0; i < this.query_result["diffs"]["count"]; i++){
                                var diff_content = renderer.diff(this.query_result["diffs"]["result"][i], false);
                                query_result.innerHTML += diff_content;
                            }
                            hits += this.query_result["diffs"]["count"];
                        }
                        if(!exEnv == true || exEnv == "false"){
                            for(var i = 0; i < this.query_result["envs"]["count"]; i++){
                                var env_content = renderer.env(this.query_result["envs"]["result"][i], false);
                                query_result.innerHTML += env_content;
                            }
                            hits += this.query_result["envs"]["count"];
                        }
                        var display = document.getElementById('results-display');
                        display.innerHTML = hits;
                    }
                    // Add load more to the end.
                    if(end != -1){
                        var next_Page = parseInt(page)+1;
                        if(parseInt(page) == 0){
                            query_result.innerHTML += "<div id='load-more-search-block' class='col s12 m12 l12 center'><a onclick='space.query(\""+search+"\", \""+exUser+"\", \""+exApp+"\", \""+exProject+"\", \""+exRecord+"\", \""+exDiff+"\", \""+exEnv+"\", \""+public+"\", 1);' class='btn-floating btn-large waves-effect waves-light tooltipped cyan' data-position='top' data-delay='50' data-tooltip='Load More'><i class='mdi-hardware-keyboard-arrow-down'></i></a></div>";
                        }else if(parseInt(page) > 0){
                            query_result.innerHTML += "<div id='load-more-search-block' class='col s12 m12 l12 center'><a onclick='space.query(\""+search+"\", \""+exUser+"\", \""+exApp+"\", \""+exProject+"\", \""+exRecord+"\", \""+exDiff+"\", \""+exEnv+"\", \""+public+"\", "+next_Page+");' class='btn-floating btn-large waves-effect waves-light tooltipped cyan' data-position='top' data-delay='50' data-tooltip='Load More'><i class='mdi-hardware-keyboard-arrow-down'></i></a></div>";
                        }else{
                            query_result.innerHTML += "<div id='load-more-search-block' class='col s12 m12 l12 center'><a onclick='space.query(\""+search+"\", \""+exUser+"\", \""+exApp+"\", \""+exProject+"\", \""+exRecord+"\", \""+exDiff+"\", \""+exEnv+"\", \""+public+"\", 1);' class='btn-floating btn-large waves-effect waves-light tooltipped cyan' data-position='top' data-delay='50' data-tooltip='Load More'><i class='mdi-hardware-keyboard-arrow-down'></i></a></div>";
                        }
                        
                        // Add a button to load more.
                    }
                }else {
                    config.error_modal('Query failed', this.responseText);
                }
            }
        };
        var filter = exUser+"-"+exApp+"-"+exProject+"-"+exRecord+"-"+exDiff+"-"+exEnv;
        if(public == "true" || public == true){
            xmlhttp.open("GET", url+"/public/dashboard/search?page="+page+"&filter="+filter+"&req="+search);
        }else{
            xmlhttp.open("GET", url+"/private/dashboard/search?page="+page+"&filter="+filter+"&req="+search);
            xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        }
        xmlhttp.send();
    },
    this.exportToJson = function () {
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {
                    var pom = document.createElement('a');
                    pom.setAttribute('href', 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(JSON.parse(this.responseText), null, 2)));
                    pom.setAttribute('download', 'dashboard.json');

                    if (document.createEvent) {
                        var event = document.createEvent('MouseEvents');
                        event.initEvent('click', true, true);
                        pom.dispatchEvent(event);
                    }
                    else {
                        pom.click();
                    }
                }else {
                    config.error_modal('Dashboard download failed', this.responseText);
                }
            }
        };
        xmlhttp.open("GET", url+"/private/dashboard/projects");
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        xmlhttp.send();
    },
    this.pull = function(project_name, record_id) {
        $('#loading-modal').openModal();
        window.location.replace(url+"/private/"+Cookies.get('session')+"/record/pull"+"/"+record_id);
        $('#loading-modal').closeModal();
    },
    this.pull_env = function(env_id) {
        $('#loading-modal').openModal();
        window.location.replace(url+"/private/"+Cookies.get('session')+"/env/download"+"/"+env_id);
        $('#loading-modal').closeModal();
    },
    this.pull_diff = function(diff_id) {
        $('#loading-modal').openModal();
        window.location.replace(url+"/private/"+Cookies.get('session')+"/diff/download"+"/"+diff_id);
        $('#loading-modal').closeModal();
    }
};

var Record = function (_id){
    var url = config.mode+"://"+config.host+":"+config.port+"/cloud/v0.1";
    var self = this;
    self._id = _id;
    self.switchAccess = function() {
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {
                    content = JSON.parse(this.responseText);
                    if(content['head']['access'] == 'private'){
                        self.access('public');
                    }else{
                        self.access('private');
                    }
                } else {
                    config.error_modal('Project update failed', "An error occured while processing your request.");
                }
            }
        };
        xmlhttp.open("GET", url+"/private/record/view/"+self._id);
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        xmlhttp.send();
    }
    // This way of doing is not optimal as we do not atomically update a record and change its content we reload the whole page.
    self.save = function(tags, rationels, status) {
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("POST", url+"/private/record/edit/"+self._id);
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        var request = { 'tags': tags, 'rationels': rationels, 'status': status};
        $('#loading-modal').openModal();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {
                    $('#loading-modal').closeModal();
                    Materialize.toast('Update succeeded', 3000, 'rounded');
                    recordProtect(self._id);
                    // config.error_modal('Update succeeded', 'Your changes to this record were pushed.');
                } else {
                    $('#loading-modal').closeModal();
                    config.error_modal('Update record failed', this.responseText);
                }
            }
        };
        if(!user.sanitize([tags, rationels, status])){
            $('#loading-modal').closeModal();
            Materialize.toast('Update failed: Invalid characters found!', 3000, 'rounded');
        }else{
            xmlhttp.open("POST", url+"/private/record/edit/"+self._id);
            xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
            xmlhttp.send(JSON.stringify(request));
        }
    }

    self.access = function(access_value) {
        var xmlhttp = new XMLHttpRequest();
        var request = {'access':access_value};
        $('#loading-modal').openModal();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                var r_access = document.getElementById('record-access-'+self._id);
                if (this.status == 200) {
                    $('#loading-modal').closeModal();
                    Materialize.toast('Record access updated', 3000, 'rounded');
                    // config.error_modal('Record access updated', 'Your record is now: '+access_value+".");
                } else {
                    $('#loading-modal').closeModal();
                    config.error_modal('Record access update failed', this.responseText);
                    if(access_value == 'public'){
                        r_access.removeAttribute("checked");
                    }else{
                        r_access.setAttribute("checked");
                    }
                }
            }
        };
        xmlhttp.open("POST", url+"/private/record/edit/"+self._id);
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        xmlhttp.send(JSON.stringify(request));
    }
    // Half way optimal. We could have just removed the record div instead of reloading the whole page. TODO
    self.trash = function () {
        var xmlhttp = new XMLHttpRequest();
        console.log('Cookie session value: '+ Cookies.get('session'));
        $('#loading-modal').openModal();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {
                    var elem = document.getElementById("record-block-"+self._id);
                    elem.parentElement.removeChild(elem);
                    $('#loading-modal').closeModal();
                    Materialize.toast('Deletion succeeded', 3000, 'rounded');
                    // config.error_modal('Deletion succeeded', 'The selected record was deleted.');
                } else {
                    $('#loading-modal').closeModal();
                    config.error_modal('Remove record failed', "An error occured while processing your request.");
                }
            }
        };
        xmlhttp.open("GET", url+"/private/record/remove/"+self._id);
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
         xmlhttp.send();
    }
    return self;
};

var Account = function (_id){
    var url = config.mode+"://"+config.host+":"+config.port+"/cloud/v0.1";
    var self = this;
    self._id = _id;
    // This way of doing is not optimal as we do not atomically update a record and change its content we reload the whole page.
    self.save = function(fname, lname, password, group, auth, org, about, quota) {
        var xmlhttp = new XMLHttpRequest();
        var request = { 'fname':fname, 'lname': lname, 'group': group, 'auth': auth, 'about': about, 'org': org, 'max-quota': quota};
        if(password != ''){
            request['password'] = password;
        }
        $('#loading-modal').openModal();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {
                    $('#loading-modal').closeModal();
                    Materialize.toast('Update succeeded', 3000, 'rounded');
                    userProtect(self._id);
                    // config.error_modal('Update succeeded', 'Your changes to this acount were pushed.');
                } else {
                    $('#loading-modal').closeModal();
                    config.error_modal('Account update failed', this.responseText);
                }
            }
        };
        if(!user.sanitize([fname, lname, org, about, auth, quota])){
            $('#loading-modal').closeModal();
            Materialize.toast('Update failed: Invalid characters found!', 3000, 'rounded');
        }else{
            xmlhttp.open("POST", url+"/private/account/update/"+self._id);
            xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
            xmlhttp.send(JSON.stringify(request));
        }
    }
    return self;
};

var Project = function (_id){
    var url = config.mode+"://"+config.host+":"+config.port+"/cloud/v0.1";
    var self = this;
    self._id = _id;
    self.switchAccess = function() {
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {
                    content = JSON.parse(this.responseText);
                    if(content['project']['access'] == 'private'){
                        self.access('public');
                    }else{
                        self.access('private');
                    }
                } else {
                    config.error_modal('Project update failed', "An error occured while processing your request.");
                }
            }
        };
        xmlhttp.open("GET", url+"/private/project/view/"+self._id);
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        xmlhttp.send();
    }
    // This way of doing is not optimal as we do not atomically update a record and change its content we reload the whole page.
    self.save = function(tags, description, goals) {
        var xmlhttp = new XMLHttpRequest();
        var request = { 'tags':tags, 'description': description, 'goals': goals};
        $('#loading-modal').openModal();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {
                    $('#loading-modal').closeModal();
                    Materialize.toast('Update succeeded', 3000, 'rounded');
                    projectProtect(self._id);
                    // config.error_modal('Update succeeded', 'Your changes to this project were pushed.');
                } else {
                    $('#loading-modal').closeModal();
                    config.error_modal('Project update failed', this.responseText);
                }
            }
        };
        if(!user.sanitize([tags, description, goals])){
            $('#loading-modal').closeModal();
            Materialize.toast('Update failed: Invalid characters found!', 3000, 'rounded');
        }else{
            xmlhttp.open("POST", url+"/private/project/edit/"+self._id);
            xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
            xmlhttp.send(JSON.stringify(request));
        }
    }
    self.access = function(access_value) {
        var xmlhttp = new XMLHttpRequest();
        var request = {'access':access_value};
        $('#loading-modal').openModal();
        xmlhttp.onreadystatechange = function()
        {
           if(this.readyState == 4){
                var p_access = document.getElementById('project-access-'+self._id);
                if (this.status == 200) {
                    console.log("Project access updated.");
                    $('#loading-modal').closeModal();
                    Materialize.toast('Project access updated', 3000, 'rounded');
                    // config.error_modal('Project access updated', 'Your project is now: '+access_value+".");
                } else {
                    $('#loading-modal').closeModal();
                    config.error_modal('Project access update failed', this.responseText);
                    if(access_value == 'public'){
                        p_access.removeAttribute("checked");
                    }else{
                        p_access.setAttribute("checked");
                    }
                }
            }
        };
        xmlhttp.open("POST", url+"/private/project/edit/"+self._id);
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        xmlhttp.send(JSON.stringify(request));
    }
    // Half way optimal. We could have just removed the record div instead of reloading the whole page. TODO
    self.trash = function () {
        var xmlhttp = new XMLHttpRequest();
        $('#loading-modal').openModal();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {
                    var elem = document.getElementById("project-block-"+self._id);
                    elem.parentElement.removeChild(elem);
                    $('#loading-modal').closeModal();
                    Materialize.toast('Deletion succeeded', 3000, 'rounded');
                    // config.error_modal('Deletion succeeded', 'The selected project was deleted.');
                } else {
                    $('#loading-modal').closeModal();
                    config.error_modal('Project remove failed', "An error occured while processing your request.");
                }
            }
        };
        xmlhttp.open("GET", url+"/private/project/remove/"+self._id);
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        xmlhttp.send();
    }
    return self;
};

var Application = function (_id){
    var url = config.mode+"://"+config.host+":"+config.port+"/cloud/v0.1";
    self._id = _id;
    // This way of doing is not optimal as we do not atomically update an app and change its content we reload the whole page.
    this.save = function(name, about, access) {
        var xmlhttp = new XMLHttpRequest();
        var request = { 'name':name, 'about': about, 'access': access};
        $('#loading-modal').openModal();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {
                    $('#loading-modal').closeModal();
                    Materialize.toast('Update succeeded', 3000, 'rounded');
                    appProtect(self._id);
                    // config.error_modal('Update succeeded', 'Your changes to this tool credentials were pushed.');
                } else {
                    $('#loading-modal').closeModal();
                    config.error_modal('Tool update failed', this.responseText);
                }
            }
        };
        if(!user.sanitize([name, about, access])){
            $('#loading-modal').closeModal();
            Materialize.toast('Update failed: Invalid characters found!', 3000, 'rounded');
        }else{
            xmlhttp.open("POST", url+"/private/dashboard/developer/app/update/"+self._id);
            xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
            xmlhttp.send(JSON.stringify(request));
        }
    },
    this.retoken = function() {
        var xmlhttp = new XMLHttpRequest();
        $('#loading-modal').openModal();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {
                    document.getElementById("app-token-"+self._id).value = this.responseText;
                    $('#loading-modal').closeModal();
                    Materialize.toast('Update succeeded', 3000, 'rounded');
                    // config.error_modal('Update succeeded', 'Your tool key renewal was done.');
                } else {
                    $('#loading-modal').closeModal();
                    config.error_modal('Tool key renew failed', "An error occured while processing your request.");
                }
            }
        };
        xmlhttp.open("GET", url+"/private/dashboard/developer/app/retoken/"+self._id);
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        xmlhttp.send();
    },
    // Half way optimal. We could have just removed the app div instead of reloading the whole page. TODO
    this.trash = function () {
        var xmlhttp = new XMLHttpRequest();
        $('#loading-modal').openModal();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {
                    var elem = document.getElementById("app-block-"+self._id);
                    elem.parentElement.removeChild(elem);
                    $('#loading-modal').closeModal();
                    Materialize.toast('Deletion succeeded', 3000, 'rounded');
                    // config.error_modal('Deletion succeeded', 'The selected tool was deleted.');
                } else {
                    $('#loading-modal').closeModal();
                    config.error_modal('Tool remove failed', "An error occured while processing your request.");
                }
            }
        };
        xmlhttp.open("GET", url+"/private/dashboard/developer/app/remove/"+self._id);
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        xmlhttp.send();
    }
};

var Diff = function (_id){
    var url = config.mode+"://"+config.host+":"+config.port+"/cloud/v0.1";
    self._id = _id;
    // This way of doing is not optimal as we do not atomically update a diff and change its content we reload the whole page.
    this.save = function(method, proposition, status) {
        var xmlhttp = new XMLHttpRequest();
        var request = { 'method': method, 'proposition': proposition, 'status': status};
        $('#loading-modal').openModal();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {
                    $('#loading-modal').closeModal();
                    Materialize.toast('Update succeeded', 3000, 'rounded');
                    diffProtect(self._id);
                    // config.error_modal('Update succeeded', 'Your changes to this assessment were pushed.');
                } else {
                    $('#loading-modal').closeModal();
                    config.error_modal('Assessment update failed', this.responseText);
                }
            }
        };
        xmlhttp.open("POST", url+"/private/diff/edit/"+self._id);
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        xmlhttp.send(JSON.stringify(request));
    },
    // Half way optimal. We could have just removed the diff div instead of reloading the whole page. TODO
    this.trash = function () {
        var xmlhttp = new XMLHttpRequest();
        $('#loading-modal').openModal();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {
                    var elem = document.getElementById("diff-block-"+self._id);
                    elem.parentElement.removeChild(elem);
                    $('#loading-modal').closeModal();
                    Materialize.toast('Deletion succeeded', 3000, 'rounded');
                    // config.error_modal('Deletion succeeded', 'The selected assessment was deleted.');
                } else {
                    $('#loading-modal').closeModal();
                    config.error_modal('Assessment remove failed', this.responseText);
                }
            }
        };
        xmlhttp.open("GET", url+"/private/diff/remove/"+self._id);
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        xmlhttp.send();
    }
};

var Environment = function (_id){
    var url = config.mode+"://"+config.host+":"+config.port+"/cloud/v0.1";
    self._id = _id;
    // This way of doing is not optimal as we do not atomically update a env and change its content we reload the whole page.
    this.save = function(group, system) {
        var xmlhttp = new XMLHttpRequest();
        var request = { 'group':group, 'system': system};
        $('#loading-modal').openModal();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {
                    $('#loading-modal').closeModal();
                    Materialize.toast('Update succeeded', 3000, 'rounded');
                    envProtect(self._id);
                    // config.error_modal('Update succeeded', 'Your changes to this environment were pushed.');
                } else {
                    $('#loading-modal').closeModal();
                    config.error_modal('Environment update failed', this.responseText);
                }
            }
        };
        xmlhttp.open("POST", url+"/private/env/edit/"+self._id);
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        xmlhttp.send(JSON.stringify(request));
    },
    // Half way optimal. We could have just removed the env div instead of reloading the whole page. TODO
    this.trash = function () {
        var xmlhttp = new XMLHttpRequest();
        $('#loading-modal').openModal();
        xmlhttp.onreadystatechange = function()
        {
            if(this.readyState == 4){
                if (this.status == 200) {
                    var elem = document.getElementById("env-block-"+self._id);
                    elem.parentElement.removeChild(elem);
                    $('#loading-modal').closeModal();
                    Materialize.toast('Deletion succeeded', 3000, 'rounded');
                    // config.error_modal('Deletion succeeded', 'The selected environment was deleted.');
                } else {
                    $('#loading-modal').closeModal();
                    config.error_modal('Environment remove failed', "An error occured while processing your request.");
                }
            }
        };
        xmlhttp.open("GET", url+"/private/env/remove/"+self._id);
        xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
        xmlhttp.send();
    }
};