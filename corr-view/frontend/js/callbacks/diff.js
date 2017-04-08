// Diff edit callback
function diffEdit(diff_id){
    var diff_update = document.getElementById('update-diff-'+diff_id);
    diff_update.innerHTML = "<a id='update-action' onclick='diffSave(\""+diff_id+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-content-save'></i></a>";
    var method = document.getElementById('diff-method-'+diff_id);
    var proposition = document.getElementById('diff-proposition-'+diff_id);
    var status = document.getElementById('diff-status-'+diff_id);
    method.removeAttribute("readonly");
    proposition.removeAttribute("readonly");
    status.removeAttribute("readonly");
}

// Diff save callback
function diffSave(diff_id){
    var diff_update = document.getElementById('update-diff-'+diff_id);
    diff_update.innerHTML = "<a id='update-action' onclick='diffEdit(\""+diff_id+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-editor-mode-edit'></i></a>";
    var method = document.getElementById('diff-method-'+diff_id);
    var proposition = document.getElementById('diff-proposition-'+diff_id);
    var status = document.getElementById('diff-status-'+diff_id);
    var diff = new Diff(diff_id);
    method.setAttribute("readonly", "");
    proposition.setAttribute("readonly", "");
    status.setAttribute("readonly", "");
    diff.save(method.value, proposition.value, status.value);
}

// Diff remove callback
function diffRemove(diff_id){
    Materialize.toast("<span>Delete "+diff_id+"</span><a class=\"btn light-blue\" onclick='diffRemoveAgree(\""+diff_id+"\");'>Confirm</a>", 5000);
}

// Diff remove agreement callback
function diffRemoveAgree(diff_id){
    var diff = new Diff(diff_id);
    diff.trash();
}