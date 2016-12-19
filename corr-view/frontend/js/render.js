var renderer = {
    user: function(object, ownership, session){
        var content = "<div class='col s12 m6 l4'>";
        content += "<div id='profile-card' class='card'>";
        content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
        content += "<div class='card-content'>";
        content += "<img src='../images/picture.png' alt='' class='circle responsive-img activator card-profile-image'>";
        content += "<a onclick='Materialize.toast(\"<span>Application share not implemented yet!</span>\", 3000);' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-social-share tooltipped' data-position='bottom' data-delay='50' data-tooltip='share'></i></a>";
        // content += "<a onclick='projectRemove(\""+object["name"]+"\",\""+object["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-action-delete'></i></a>";
        // content += "<a onclick='Materialize.toast(\"<span>Project record upload not implemented yet!</span>\", 3000);' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled'><i class='mdi-file-cloud-upload'></i></a>";
        // content += "<a onclick='Materialize.toast(\"<span>Project environment upload not implemented yet!</span>\", 3000);' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled'><i class='mdi-maps-layers'></i></a>";
        // content += "<div id='update-project-"+object["id"]+"'><a id='update-action' onclick='projectEdit(\""+object["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-editor-mode-edit'></i></a></div>";
        // content += "<a href='./?session="+session+"&view=records&project="+object["id"]+"' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right "+disable_view+"'><i class='mdi-action-visibility'></i></a>";
        content += "<span class='card-title activator black-text text-darken-4'> "+object["name"]+"</span>";
        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+object["created"]+"</p>";
        // content += "<p><i class='mdi-device-access-alarm cyan-text text-darken-2'></i> "+object["duration"]+"</p>";
        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-turned-in prefix cyan-text text-darken-2'></i><input readonly id='user-organisation-"+object["id"]+"' type='text' value='"+object["organisation"]+"'></div></div>";
        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='description'><div class='input-field col s12'><i class='mdi-action-description prefix cyan-text text-darken-2'></i><input readonly id='user-email-"+object["id"]+"' type='text' value='"+object["email"]+"'></div></div>";
        // content += "<p><i class='mdi-action-description cyan-text text-darken-2'></i> "+object["description"]+"</p>";
        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='goals'><div class='input-field col s12'><i class='mdi-action-subject prefix cyan-text text-darken-2'></i><textarea readonly class='materialize-textarea' id='user-about-"+object["id"]+"' type='text'>"+object["about"]+"</textarea></div></div>";
        // content += "<p><i class='mdi-action-subject cyan-text text-darken-2'></i> "+object["goals"]+"</p>";
        content += "<div class='card-action center-align'>";
        content += "<a onclick='Materialize.toast(\"<span>Project diffs view not implemented yet!</span>\", 3000);' class='valign left tooltipped' data-position='bottom' data-delay='50' data-tooltip='applications'><i class='mdi-navigation-apps cyan-text text-darken-2'></i> <span class='applications badge'>"+object["apps"]+"</span></a>";
        content += "<a onclick='Materialize.toast(\"<span>Project diffs view not implemented yet!</span>\", 3000);' class='valign tooltipped' data-position='bottom' data-delay='50' data-tooltip='projects'><i class='mdi-file-folder cyan-text text-darken-2'></i> <span class='projects badge'>"+object["projects"]+"</span></a>";
        content += "<a onclick='Materialize.toast(\"<span> Project environments view not implemented yet!</span>\", 3000);' class='valign right tooltipped' data-position='bottom' data-delay='50' data-tooltip='records'><i class='mdi-file-cloud-upload cyan-text text-darken-2'></i> <span class='records badge'>"+object["records"]+"</span></a>";
        content += "</div>";
        content += "</div>";
        content += "</div>";
        content += "<div id='project-"+object["id"]+"-confirm' class='modal'></div>";
        content += "</div>";
        return content;
    },
    application: function(object, ownership, session){
        var content = "<div class='col s12 m6 l4'>";
        content += "<div id='profile-card' class='card'>";
        content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
        content += "<div class='card-content'>";
        content += "<img src='../images/gearsIcon.png' alt='' class='circle responsive-img activator card-profile-image'>";
        content += "<a onclick='Materialize.toast(\"<span>Application share not implemented yet!</span>\", 3000);' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-social-share tooltipped' data-position='bottom' data-delay='50' data-tooltip='share'></i></a>";
        content += "<a onclick='customSearch(\"user\",\""+object["developer-name"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-social-person tooltipped' data-position='bottom' data-delay='50' data-tooltip='"+object["developer-name"]+"'></i></a>";

        // content += "<a onclick='appRemove(\""+object["name"]+"\",\""+object["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-action-delete'></i></a>";
        // content += "<a onclick='Materialize.toast(\"<span>Application upload not implemented yet!</span>\", 3000);' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled'><i class='mdi-file-cloud-upload'></i></a>";
        // content += "<a onclick='Materialize.toast(\"<span>Application download not implemented yet!</span>\", 3000);' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled'><i class='mdi-file-cloud-download'></i></a>";
        // content += "<div id='update-app-"+object["id"]+"'><a id='update-action' onclick='appEdit(\""+object["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-editor-mode-edit'></i></a></div>";
        // content += "<a href='./?session="+session+"&view=records&project="+object["id"]+"' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right "+disable_view+"'><i class='mdi-action-visibility'></i></a>";
        content += "<span class='card-title activator black-text text-darken-4'> "+object["name"]+"</span>";
        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+object["created"]+"</p>";
        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-turned-in prefix cyan-text text-darken-2'></i><input readonly id='app-access-"+object["id"]+"' type='text' value='"+object["access"]+"'></div></div>";
        // content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-settings-ethernet prefix cyan-text text-darken-2'></i><input readonly id='app-network-"+object["id"]+"' type='text' value='"+object["network"]+"'></div></div>";
        // content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-lock prefix cyan-text text-darken-2'></i><input readonly id='app-access-"+object["id"]+"' type='text' value='"+object["access"]+"'></div></div>";
        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='description'><div class='input-field col s12'><i class='mdi-communication-vpn-key prefix cyan-text text-darken-2'></i><input readonly id='app-token-"+object["id"]+"' type='text' value='"+object["token"]+"'></div></div>";
        // content += "<p><i class='mdi-action-description cyan-text text-darken-2'></i> "+object["description"]+"</p>";
        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='goals'><div class='input-field col s12'><i class='mdi-action-subject prefix cyan-text text-darken-2'></i><textarea readonly class='materialize-textarea' id='app-about-"+object["id"]+"' type='text'>"+object["about"]+"</textarea></div></div>";
        // content += "<p><i class='mdi-action-subject cyan-text text-darken-2'></i> "+object["goals"]+"</p>";
        content += "<div class='card-action center-align'>";
        content += "<a onclick='Materialize.toast(\"<span>Project diffs view not implemented yet!</span>\", 3000);' class='valign left tooltipped' data-position='bottom' data-delay='50' data-tooltip='users'><i class='mdi-social-group-add cyan-text text-darken-2'></i> <span class='users badge'>"+object["users"]+"</span></a>";
        content += "<a onclick='Materialize.toast(\"<span>Application projects view not implemented yet!</span>\", 3000);' class='valign tooltipped' data-position='bottom' data-delay='50' data-tooltip='projects'><i class='mdi-file-folder cyan-text text-darken-2'></i> <span class='projects badge'>"+object["projects"]+"</span></a>";
        content += "<a onclick='Materialize.toast(\"<span> Application records view not implemented yet!</span>\", 3000);' class='valign right tooltipped' data-position='bottom' data-delay='50' data-tooltip='records'><i class='mdi-file-cloud-upload cyan-text text-darken-2'></i> <span class='records badge'>"+object["records"]+"</span></a>";
        content += "</div>";
        content += "</div>";
        content += "</div>";
        content += "<div id='app-"+object["id"]+"-confirm' class='modal'></div>";
        content += "</div>";
        return content;
    },
    project: function(object, ownership, session){
        var content = "<div class='col s12 m6 l4'>";
        content += "<div id='profile-card' class='card'>";
        content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
        content += "<div class='card-content'>";
        content += "<img src='../images/project.png' alt='' class='circle responsive-img activator card-profile-image'>";
        content += "<a onclick='Materialize.toast(\"<span>Application share not implemented yet!</span>\", 3000);' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-social-share tooltipped' data-position='bottom' data-delay='50' data-tooltip='share'></i></a>";
        content += "<a onclick='customSearch(\"user\",\""+object["owner-name"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-social-person tooltipped' data-position='bottom' data-delay='50' data-tooltip='"+object["owner-name"]+"'></i></a>";

        // content += "<a onclick='Materialize.toast(\"<span>Project record upload not implemented yet!</span>\", 3000);' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled'><i class='mdi-file-cloud-upload'></i></a>";
        // content += "<a onclick='Materialize.toast(\"<span>Project environment upload not implemented yet!</span>\", 3000);' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled'><i class='mdi-maps-layers'></i></a>";
        // content += "<div id='update-project-"+object["id"]+"'><a id='update-action' onclick='projectEdit(\""+object["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-editor-mode-edit'></i></a></div>";
        // content += "<a href='./?session="+session+"&view=records&project="+object["id"]+"' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right "+disable_view+"'><i class='mdi-action-visibility'></i></a>";
        content += "<span class='card-title activator black-text text-darken-4'> "+object["name"]+"</span>";
        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+object["created"]+"</p>";
        // content += "<p><i class='mdi-device-access-alarm cyan-text text-darken-2'></i> "+object["duration"]+"</p>";
        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-turned-in prefix cyan-text text-darken-2'></i><input readonly id='project-tags-"+object["id"]+"' type='text' value='"+object["tags"]+"'></div></div>";
        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='description'><div class='input-field col s12'><i class='mdi-action-description prefix cyan-text text-darken-2'></i><input readonly id='project-desc-"+object["id"]+"' type='text' value='"+object["description"]+"'></div></div>";
        // content += "<p><i class='mdi-action-description cyan-text text-darken-2'></i> "+object["description"]+"</p>";
        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='goals'><div class='input-field col s12'><i class='mdi-action-subject prefix cyan-text text-darken-2'></i><textarea readonly class='materialize-textarea' id='project-goals-"+object["id"]+"' type='text'>"+object["goals"]+"</textarea></div></div>";
        // content += "<p><i class='mdi-action-subject cyan-text text-darken-2'></i> "+object["goals"]+"</p>";
        content += "<div class='card-action center-align'>";
        content += "<a onclick='Materialize.toast(\"<span>Project diffs view not implemented yet!</span>\", 3000);' class='valign left tooltipped' data-position='bottom' data-delay='50' data-tooltip='records'><i class='mdi-file-cloud-done cyan-text text-darken-2'></i> <span class='records badge'>"+object["records"]+"</span></a>";
        content += "<a onclick='Materialize.toast(\"<span>Project diffs view not implemented yet!</span>\", 3000);' class='valign tooltipped' data-position='bottom' data-delay='50' data-tooltip='diffs'><i class='mdi-image-compare cyan-text text-darken-2'></i> <span class='diffs badge'>"+object["diffs"]+"</span></a>";
        content += "<a onclick='Materialize.toast(\"<span> Project environments view not implemented yet!</span>\", 3000);' class='valign right tooltipped' data-position='bottom' data-delay='50' data-tooltip='environments'><i class='mdi-maps-layers cyan-text text-darken-2'></i> <span class='containers badge'>"+object["environments"]+"</span></a>";
        content += "</div>";
        content += "</div>";
        content += "</div>";
        content += "<div id='project-"+object["id"]+"-confirm' class='modal'></div>";
        content += "</div>";
        return content;
    },
    record: function(object, ownership, session){
        var content = "<div class='col s12 m6 l4' id='"+object["head"]["id"]+"'> ";
        content += "<div id='profile-card' class='card'>";
        content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
        content += "<div class='card-content'>";
        // var disable_download = "";
        // if(object["environments"] == null){
        //     disable_download = "disabled";
        // }
        content += "<img src='../images/record.png' alt='' class='circle responsive-img activator card-profile-image'>";
        content += "<a onclick='Materialize.toast(\"<span>Application share not implemented yet!</span>\", 3000);' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-social-share tooltipped' data-position='bottom' data-delay='50' data-tooltip='share'></i></a>";
        content += "<a onclick='customSearch(\"project\",\""+object["head"]["project"]+" "+object["head"]["project-name"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-file-folder tooltipped' data-position='bottom' data-delay='50' data-tooltip='"+object["head"]["project-name"]+"'></i></a>";
        // content += "<a onclick='recordRemove(\""+object["head"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-action-delete'></i></a>";
        content += "<a onclick=\"space.pull('"+object["head"]["project"]+"','"+object["head"]["id"]+"')\" class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-file-cloud-download tooltipped' data-position='top' data-delay='50' data-tooltip='download'></i></a>";
        // content += "<div id='update-record-"+object["head"]["id"]+"'><a id='update-action' onclick='recordEdit(\""+object["head"]["id"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-editor-mode-edit'></i></a></div>";
        content += "<span class='card-title activator grey-text text-darken-4'>"+object["head"]["id"]+"</span>";
        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+object["head"]["created"]+"</p>";
        // content += "<p class='grey-text ultra-small'><i class='mdi-file-folder cyan-text text-darken-2'></i> "+object["head"]["project-name"]+"</p>";
        // content += "<p><i class='mdi-device-access-alarm cyan-text text-darken-2'></i> "+object["head"]["updated"]+"</p>";
        content += "<div class='row margin'><div class='input-field col s12'><i class='mdi-action-turned-in prefix cyan-text text-darken-2'></i><input readonly id='record-tags-"+object["head"]["id"]+"' type='text' value='"+object["head"]["tags"]+"'></div></div>";
        content += "<div class='row margin'><div class='input-field col s12'><i class='mdi-notification-event-note prefix cyan-text text-darken-2'></i><input readonly id='record-rationels-"+object["head"]["id"]+"' type='text' value='"+object["head"]["rationels"]+"'></div></div>";
        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='status'><div class='input-field col s12'><i class='mdi-action-subject prefix cyan-text text-darken-2'></i><textarea readonly class='materialize-textarea' id='record-status-"+object["head"]["id"]+"' type='text'>This record status is: "+object["head"]["status"]+"</textarea></div></div>";
        // content += "<p><i class='mdi-notification-sync cyan-text text-darken-2'></i> "+object["head"]["status"]+"</p>";
        content += "<div class='card-action center-align'>";
        content += "<a onclick='Materialize.toast(\"<span>Record inputs view not implemented yet!</span>\", 3000);' class='valign left'><i class='mdi-communication-call-received cyan-text text-darken-2'></i> <span class='inputs badge'>"+object["head"]["inputs"]+"</span></a>";
        content += "<a onclick='Materialize.toast(\"<span>Record outputs view not implemented yet!</span>\", 3000);' class='valign'><i class='mdi-communication-call-made cyan-text text-darken-2'></i> <span class='outputs badge'>"+object["head"]["outputs"]+"</span></a>";
        content += "<a onclick='Materialize.toast(\"<span>Record dependencies view not implemented yet!</span>\", 3000);' class='valign right'><i class='mdi-editor-insert-link cyan-text text-darken-2'></i> <span class='dependencies badge'>"+object["head"]["dependencies"]+"</span></a>";
        content += "</div>";
        content += "</div>";                
        content += "</div>";
        content += "</div>";
        return content;
    }
}