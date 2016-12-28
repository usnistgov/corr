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
    console.log('Cookie session value: '+ Cookies.get('session'));
    var diff_update = document.getElementById('update-diff-'+diff_id);
    diff_update.innerHTML = "<a id='update-action' onclick='diffEdit(\""+diff_id+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-editor-mode-edit'></i></a>";
    var method = document.getElementById('diff-method-'+diff_id);
    var proposition = document.getElementById('diff-proposition-'+diff_id);
    var status = document.getElementById('diff-status-'+diff_id);
    var diff = new Diff(user.session, diff_id);
    diff.save(method.value, proposition.value, status.value);
}

// Diff remove callback
function diffRemove(diff_id){
    Materialize.toast("<span>Delete "+diff_id+"</span><a class=\"btn light-blue\" href=\"http://"+config.host+":"+config.port+"/cloud/v0.1/private/"+user.session+"/diff/remove/"+diff_id+"\">Confirm</a>", 5000);
}

// Diff remove agreement callback
function diffRemoveAgree(session, diff_id){
    console.log("in diffRemoveAgree!");
    console.log('Cookie session value: '+ Cookies.get('session'));
    var diff = new Diff(session, diff_id);
    diff.trash();
    window.location.reload();
}