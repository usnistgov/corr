// Record upload callback
function uploadRecord(project_name, project_id){
    Materialize.toast('<span>Uploading a new record to Project ['+project_name+']...</span>', 3000);
}

// Record edit callback
function recordEdit(record_id){
    var record_update = document.getElementById('update-record-'+record_id);
    record_update.innerHTML = "<a id='update-action' onclick='recordSave(\""+record_id+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-content-save'></i></a>";
    var tags = document.getElementById('record-tags-'+record_id);
    var rationels = document.getElementById('record-rationels-'+record_id);
    var status = document.getElementById('record-status-'+record_id);
    tags.removeAttribute("readonly");
    rationels.removeAttribute("readonly");
    status.removeAttribute("readonly");
}

// Record save callback
function recordSave(record_id){
    var record_update = document.getElementById('update-record-'+record_id);
    record_update.innerHTML = "<a id='update-action' onclick='recordEdit(\""+record_id+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-editor-mode-edit'></i></a>";
    var tags = document.getElementById('record-tags-'+record_id);
    var rationels = document.getElementById('record-rationels-'+record_id);
    var status = document.getElementById('record-status-'+record_id);
    var record = new Record(record_id);
    record.save(tags.value, rationels.value, status.value);
}

// Record remove callback
function recordRemove(record_id){
    Materialize.toast("<span>Delete "+record_id+"</span><a class=\"btn light-blue\" onclick='recordRemoveAgree(\""+record_id+"\");'>Confirm</a>", 5000);
}

// Record remove agreement callback
function recordRemoveAgree(record_id){
    var record = new Record(record_id);
    record.trash();
}

function recordSelect(record_id){
    var left_float = document.getElementById("results-display");
    selected_records.push(record_id);
    var record_update = document.getElementById('select-record-'+record_id);
    record_update.innerHTML = "<a id='deselect-action' onclick='recordDeselect(\""+record_id+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-toggle-check-box'></i></a>";
    if(selected_records.length == 2){
        left_float.innerHTML = "<i class='large mdi-editor-vertical-align-center'></i>";
        left_float.setAttribute( "onClick", "launchDiffModal();");
        left_float.setAttribute( "data-tooltip", "create diff from selection");
    }
}

function recordDeselect(record_id){
    var left_float = document.getElementById("results-display");
    for(var i=0; i<selected_records.length; i++){
        if(selected_records[i]==record_id){
            selected_records.splice(i,1);
            break;
        }
    }
    if(selected_records.length == 1){
        left_float.innerHTML = hits;
        left_float.removeAttribute( "onClick");
        left_float.setAttribute( "data-tooltip", "number of hits");
    }
    var record_update = document.getElementById('select-record-'+record_id);
    record_update.innerHTML = "<a id='select-action' onclick='recordSelect(\""+record_id+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-toggle-check-box-outline-blank'></i></a>";
}

function recordAccess(record_id){
    var r_access = document.getElementById('record-access-'+record_id);
    var record = new Record(record_id);
    record.switchAccess();
}