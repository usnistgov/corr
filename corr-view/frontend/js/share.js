var sharer = {
    user: function(object, picture){
        var content = "<div class='col s12 m6 l4'>";
        content += "<div id='profile-card' class='card'>";
        content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
        content += "<div class='card-content'>";
        content += "<img src='"+picture+"' alt='' class='circle responsive-img activator card-profile-image'>";
        content += "<a onclick='config.error_modal(\"User details failed.\", \"User details not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='details'><i class='mdi-action-visibility'></i></a>";

        content += "<span class='card-title black-text text-darken-4'> "+object["name"]+"</span>";
        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+object["created"]+"</p>";
        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-turned-in prefix cyan-text text-darken-2'></i><input readonly id='user-organisation-"+object["id"]+"' type='text' value='"+object["organisation"]+"'></div></div>";
        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='description'><div class='input-field col s12'><i class='mdi-action-description prefix cyan-text text-darken-2'></i><input readonly id='user-email-"+object["id"]+"' type='text' value='"+object["email"]+"'></div></div>";
        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='goals'><div class='input-field col s12'><i class='mdi-action-subject prefix cyan-text text-darken-2'></i><textarea readonly class='materialize-textarea' id='user-about-"+object["id"]+"' type='text'>"+object["about"]+"</textarea></div></div>";
        content += "<div class='card-action center-align'>";
        content += "<a onclick='config.error_modal(\"User apps view failed.\", \"User apps view not implemented yet!\");' class='valign left tooltipped' data-position='bottom' data-delay='50' data-tooltip='applications'><i class='mdi-navigation-apps cyan-text text-darken-2 tooltipped' data-position='bottom' data-delay='50' data-tooltip='applications'></i> <span class='applications badge'>"+object["apps"]+"</span></a>";
        content += "<a onclick='config.error_modal(\"User projects view failed.\", \"User projects view not implemented yet!\");' class='valign tooltipped' data-position='bottom' data-delay='50' data-tooltip='projects'><i class='mdi-file-folder cyan-text text-darken-2 tooltipped' data-position='bottom' data-delay='50' data-tooltip='projects'></i> <span class='projects badge'>"+object["projects"]+"</span></a>";
        content += "<a onclick='config.error_modal(\"User records view failed.\", \"User records view not implemented yet!\");' class='valign right tooltipped' data-position='bottom' data-delay='50' data-tooltip='records'><i class='mdi-file-cloud-upload cyan-text text-darken-2 tooltipped' data-position='bottom' data-delay='50' data-tooltip='records'></i> <span class='records badge'>"+object["records"]+"</span></a>";
        content += "</div>";
        content += "</div>";
        content += "</div>";
        content += "<div id='project-"+object["id"]+"-confirm' class='modal'></div>";
        content += "</div>";
        return content;
    },
    app: function(object){
        var content = "<div class='col s12 m12 l12'>";
        content += "<div id='profile-card' class='card'>";
        content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
        content += "<div class='card-content'>";
        content += "<img src='../images/gearsIcon.png' alt='' class='circle responsive-img activator card-profile-image'>";
        content += "<a onclick='config.error_modal(\"Application download failed.\", \"Application download not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='download'><i class='mdi-file-cloud-download'></i></a>";
        content += "<a onclick='userViewModal(\""+object["developer"]["id"]+"\",\""+object["developer"]["profile"]["fname"]+"\""+",\""+object["developer"]["profile"]["lname"]+"\",\""+object["developer"]["profile"]["organisation"]+"\",\""+object["developer"]["profile"]["about"]+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-delay='50' data-tooltip='"+object["developer-name"]+"'><i class='mdi-social-person' data-position='bottom'></i></a>";
        content += "<a onclick='config.error_modal(\"Application details failed.\", \"Application details not implemented yet!\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right disabled tooltipped' data-position='bottom' data-delay='50' data-tooltip='details'><i class='mdi-action-visibility'></i></a>";

        content += "<span class='card-title black-text text-darken-4'> "+object["name"]+"</span>";
        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+object["created"]+"</p>";
        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-turned-in prefix cyan-text text-darken-2'></i><input readonly id='app-access-"+object["id"]+"' type='text' value='"+object["access"]+"'></div></div>";
        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='description'><div class='input-field col s12'><i class='mdi-communication-vpn-key prefix cyan-text text-darken-2'></i><input readonly id='app-token-"+object["id"]+"' type='text' value='"+object["token"]+"'></div></div>";
        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='goals'><div class='input-field col s12'><i class='mdi-action-subject prefix cyan-text text-darken-2'></i><textarea readonly class='materialize-textarea' id='app-about-"+object["id"]+"' type='text'>"+object["about"]+"</textarea></div></div>";
        content += "<div class='card-action center-align'>";
        content += "<a onclick='config.error_modal(\"Application users view failed.\", \"Application users view not implemented yet!\");' class='valign left tooltipped' data-position='bottom' data-delay='50' data-tooltip='users'><i class='mdi-social-group-add cyan-text text-darken-2 tooltipped' data-position='bottom' data-delay='50' data-tooltip='users'></i> <span class='users badge'>"+object["users"]+"</span></a>";
        content += "<a onclick='config.error_modal(\"Application projects view failed.\", \"Application projects view not implemented yet!\");' class='valign tooltipped' data-position='bottom' data-delay='50' data-tooltip='projects'><i class='mdi-file-folder cyan-text text-darken-2 tooltipped' data-position='bottom' data-delay='50' data-tooltip='projects'></i> <span class='projects badge'>"+object["projects"]+"</span></a>";
        content += "<a onclick='config.error_modal(\"Application records view failed.\", \"Application records view not implemented yet!\");' class='valign right tooltipped' data-position='bottom' data-delay='50' data-tooltip='records'><i class='mdi-file-cloud-upload cyan-text text-darken-2 tooltipped' data-position='bottom' data-delay='50' data-tooltip='records'></i> <span class='records badge'>"+object["records"]+"</span></a>";
        content += "</div>";
        content += "</div>";
        content += "</div>";
        content += "<div id='app-"+object["id"]+"-confirm' class='modal'></div>";
        content += "</div>";
        return content;
    },
    project: function(object){
        var object = object['project'];
        var content = "<div class='col s12 m12 l12'>";
        content += "<div id='profile-card' class='card'>";
        content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
        content += "<div class='card-content'>";
        content += "<img src='../images/project.png' alt='' class='circle responsive-img activator card-profile-image'>";

        content += "<span class='card-title black-text text-darken-4'> "+object["name"]+"</span>";
        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+object["created"]+"</p>";
        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='tags'><div class='input-field col s12'><i class='mdi-action-turned-in prefix cyan-text text-darken-2'></i><input readonly id='project-tags-"+object["id"]+"' type='text' value='"+object["tags"]+"'></div></div>";
        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='description'><div class='input-field col s12'><i class='mdi-action-description prefix cyan-text text-darken-2'></i><input readonly id='project-desc-"+object["id"]+"' type='text' value='"+object["description"]+"'></div></div>";
        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='goals'><div class='input-field col s12'><i class='mdi-action-subject prefix cyan-text text-darken-2'></i><textarea readonly class='materialize-textarea' id='project-goals-"+object["id"]+"' type='text'>"+object["goals"]+"</textarea></div></div>";
        content += "<div class='card-action center-align'>";
        content += "<a onclick='config.error_modal(\"Project records view failed.\", \"Project records view not implemented yet!\");' class='valign left tooltipped' data-position='bottom' data-delay='50' data-tooltip='records'><i class='mdi-file-cloud-done cyan-text text-darken-2'></i> <span class='records badge'>"+object["records"]+"</span></a>";
        content += "<a onclick='config.error_modal(\"Project diffs view failed.\", \"Project diffs view not implemented yet!\");' class='valign tooltipped' data-position='bottom' data-delay='50' data-tooltip='diffs'><i class='mdi-image-compare cyan-text text-darken-2'></i> <span class='diffs badge'>"+object["diffs"]+"</span></a>";
        content += "<a onclick='config.error_modal(\"Project environments view failed.\", \"Project environments view not implemented yet!\");' class='valign right tooltipped' data-position='bottom' data-delay='50' data-tooltip='environments'><i class='mdi-maps-layers cyan-text text-darken-2'></i> <span class='containers badge'>"+object["environments"]+"</span></a>";
        content += "</div>";
        content += "</div>";
        content += "</div>";
        content += "<div id='project-"+object["id"]+"-confirm' class='modal'></div>";
        content += "</div>";
        return content;
    },
    record: function(object){
        var content = "<div class='col s12 m12 l12' id='"+object["head"]["id"]+"'> ";
        content += "<div id='profile-card' class='card'>";
        content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
        content += "<div class='card-content'>";
        content += "<img src='../images/record.png' alt='' class='circle responsive-img activator card-profile-image'>";
        content += "<a onclick=\"space.pull('"+object["head"]["project"]["id"]+"','"+object["head"]["id"]+"')\" class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='top' data-delay='50' data-tooltip='download'><i class='mdi-file-cloud-download'></i></a>";

        content += "<span class='card-title grey-text text-darken-4'>"+object["head"]["id"]+"</span>";
        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+object["head"]["created"]+"</p>";
        content += "<div class='row margin'><div class='input-field col s12'><i class='mdi-action-turned-in prefix cyan-text text-darken-2'></i><input readonly id='record-tags-"+object["head"]["id"]+"' type='text' value='"+object["head"]["tags"]+"'></div></div>";
        content += "<div class='row margin'><div class='input-field col s12'><i class='mdi-notification-event-note prefix cyan-text text-darken-2'></i><input readonly id='record-rationels-"+object["head"]["id"]+"' type='text' value='"+object["head"]["rationels"]+"'></div></div>";
        content += "<div class='row margin tooltipped' data-position='bottom' data-delay='50' data-tooltip='status'><div class='input-field col s12'><i class='mdi-action-subject prefix cyan-text text-darken-2'></i><textarea readonly class='materialize-textarea' id='record-status-"+object["head"]["id"]+"' type='text'>This record status is: "+object["head"]["status"]+"</textarea></div></div>";
        content += "<div class='card-action center-align'>";
        content += "<a onclick='config.error_modal(\"Record inputs view failed.\", \"Record inputs view not implemented yet!\");' class='valign left'><i class='mdi-communication-call-received cyan-text text-darken-2'></i> <span class='inputs badge'>"+object["head"]["inputs"].length+"</span></a>";
        content += "<a onclick='config.error_modal(\"Record outputs view failed.\", \"Record outputs view not implemented yet!\");' class='valign'><i class='mdi-communication-call-made cyan-text text-darken-2'></i> <span class='outputs badge'>"+object["head"]["outputs"].length+"</span></a>";
        content += "<a onclick='config.error_modal(\"Record dependencies view failed.\", \"Record dependencies view not implemented yet!\");' class='valign right'><i class='mdi-editor-insert-link cyan-text text-darken-2'></i> <span class='dependencies badge'>"+object["head"]["dependencies"].length+"</span></a>";
        content += "</div>";
        content += "</div>";                
        content += "</div>";
        content += "</div>";
        return content;
    },
    diff: function(object){
        var content = "<div class='col s12 m12 l12' id='"+object["id"]+"'> ";
        content += "<div id='profile-card' class='card'>";
        content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
        content += "<div class='card-content'>";
        content += "<img src='../images/diff.png' alt='' class='circle responsive-img activator card-profile-image'>";
        content += "<a onclick=\"space.pull_diff('"+object["id"]+"');\" class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='download'><i class='mdi-file-cloud-download'></i></a>";

        content += "<span class='card-title grey-text text-darken-4'>"+object["id"]+"</span>";
        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+object["created"]+"</p>";
        content += "<div class='row margin'><div class='input-field col s12'><i class='mdi-action-book prefix cyan-text text-darken-2'></i><input readonly placeholder='default,visual,custom' id='diff-method-"+object["id"]+"' type='text' value='"+object["method"]+"'></div></div>";
        content += "<div class='row margin'><div class='input-field col s12'><i class='mdi-action-assignment prefix cyan-text text-darken-2'></i><input readonly placeholder='repeated,reproduced,replicated,non-replicated,non-repeated,non-reproduced' id='diff-proposition-"+object["id"]+"' type='text' value='"+object["proposition"]+"'></div></div>";


        content += "<div class='row margin'><div class='input-field col s12'><i class='mdi-notification-sync prefix cyan-text text-darken-2'></i><textarea class='materialize-textarea' readonly placeholder='agreed,denied' id='diff-status-"+object["id"]+"' type='text'>"+object["status"]+"</textarea></div></div>";
        content += "<div class='card-action center-align'>";
        var record_from = object["from"];
        var record_to = object["to"];

        content += "<a onclick='config.error_modal(\"Diff record from view failed.\", \"Diff record from view not implemented yet!\");' class='valign left tooltipped' data-position='bottom' data-delay='50' data-tooltip='record from'><i class='mdi-file-cloud-download cyan-text text-darken-2'></i><span class='from badge'>"+record_from["head"]["id"].substring(0,4)+"..."+record_from["head"]["id"].substring(19,23)+"</span></a>";
        content += "<a onclick='config.error_modal(\"Diff record to view failed.\", \"Diff record to view not implemented yet!\");' class='valign'><i class='mdi-file-cloud-upload cyan-text text-darken-2 tooltipped' data-position='bottom' data-delay='50' data-tooltip='record to'></i><span class='to badge'>"+record_to["head"]["id"].substring(0,4)+"..."+record_to["head"]["id"].substring(19,23)+"</span></a>";
        content += "<a onclick='config.error_modal(\"Diff comments view failed.\", \"Diff comments view not implemented yet!\");' class='valign right'><i class='mdi-editor-insert-comment cyan-text text-darken-2 tooltipped' data-position='bottom' data-delay='50' data-tooltip='comments'></i> <span class='comments badge'>"+object["comments"]+"</span></a>";

        content += "</div>";
        content += "</div>";                
        content += "</div>";
        content += "</div>";
        return content;
    },
    env: function(object){
        var content = "<div class='col s12 m12 l12' id='"+object["id"]+"'>";
        content += "<div id='profile-card' class='card'>";
        content += "<div class='card-image waves-effect waves-block waves-light'><img class='activator' src='../images/user-bg.jpg' alt='user background'></div>";
        content += "<div class='card-content'>";
        content += "<img src='../images/env.png' alt='' class='circle responsive-img activator card-profile-image'>";
        content += "<a onclick=\"space.pull_env('"+object["id"]+"');\" class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right tooltipped' data-position='bottom' data-delay='50' data-tooltip='download'><i class='mdi-file-cloud-download'></i></a>";        

        content += "<span class='card-title grey-text text-darken-4'>"+object["id"]+"</span>";
        content += "<p class='grey-text ultra-small'><i class='mdi-device-access-time cyan-text text-darken-2'></i> "+object["created"]+"</p>";

        content += "<div class='row margin'><div class='input-field col s12'><i class='mdi-navigation-apps prefix cyan-text text-darken-2'></i><input readonly id='env-app-"+object["id"]+"' type='text' value='"+object["application"]["name"]+"'></div></div>";
        content += "<div class='row margin'><div class='input-field col s12'><i class='mdi-action-turned-in prefix cyan-text text-darken-2'></i><input readonly placeholder='computational,experimental' id='env-group-"+object["id"]+"' type='text' value='"+object["group"]+"'></div></div>";
        content += "<div class='row margin'><div class='input-field col s12'><i class='mdi-action-subject prefix cyan-text text-darken-2'></i><textarea class='materialize-textarea' readonly placeholder='container-based,vm-based,tool-based,cloud-based,device-based,lab-based,custom-based' id='env-system-"+object["id"]+"' type='text'>"+object["system"]+"</textarea></div></div>";


        content += "<div class='card-action center-align'>";

        content += "<a onclick='config.error_modal(\"Env resources view failed.\", \"Env resources view not implemented yet!\");' class='valign left tooltipped' data-position='bottom' data-delay='50' data-tooltip='resources'><i class='mdi-action-view-list cyan-text text-darken-2'></i><span class='from badge'>"+object["resources"]+"</span></a>";
        content += "<a onclick='config.error_modal(\"Env comments view failed.\", \"Env comments view not implemented yet!\");' class='valign right tooltipped' data-position='bottom' data-delay='50' data-tooltip='comments'><i class='mdi-editor-insert-comment cyan-text text-darken-2'></i> <span class='comments badge'>"+object["comments"]+"</span></a>";
        content += "<a onclick='config.error_modal(\"Env bundle view failed.\", \"Env bundle view not implemented yet!\");' class='valign tooltipped' data-position='bottom' data-delay='50' data-tooltip='bundle'><i class='mdi-editor-insert-drive-file cyan-text text-darken-2'></i><span class='to badge'>"+object["bundle"]["id"].substring(0,4)+"..."+object["bundle"]["id"].substring(19,23)+"</span></a>";

        content += "</div>";
        content += "</div>";                
        content += "</div>";
        content += "</div>";
        return content;
    }
}