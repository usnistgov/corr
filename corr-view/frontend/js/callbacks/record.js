// Reload upload callback
function uploadRecord(project_name, project_id){
    Materialize.toast('<span>Uploading a new record to Project ['+project_name+']...</span>', 3000);
}

// Record edit callback
function recordEdit(record_id){
    var project_update = document.getElementById('update-record-'+record_id);
    project_update.innerHTML = "<a id='update-action' onclick='recordSave(\""+record_id+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-content-save'></i></a>";
    var tags = document.getElementById('record-tags-'+record_id);
    var rationels = document.getElementById('record-rationels-'+record_id);
    tags.removeAttribute("readonly");
    rationels.removeAttribute("readonly");
}

// Record save callback
function recordSave(record_id){
    var project_update = document.getElementById('update-record-'+record_id);
    project_update.innerHTML = "<a id='update-action' onclick='recordEdit(\""+record_id+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-editor-mode-edit'></i></a>";
    var tags = document.getElementById('record-tags-'+record_id);
    var rationels = document.getElementById('record-rationels-'+record_id);
    var record = new Record(user.session, record_id);
    record.save(tags.value, rationels.value);
}

// Record remove callback
function recordRemove(record_id){
    Materialize.toast("<span>Delete "+record_id+"</span><a class=\"btn light-blue\" href=\"http://"+config.host+":"+config.port+"/cloud/v0.1/private/"+user.session+"/record/remove/"+record_id+"\">Confirm</a>", 5000);
}