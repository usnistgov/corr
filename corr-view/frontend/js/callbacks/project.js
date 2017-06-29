// Project edit callback
function projectEdit(project_id){
    var project_update = document.getElementById('update-project-'+project_id);
    project_update.innerHTML = "<a id='update-action' onclick='projectSave(\""+project_id+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-content-save'></i></a>";
    var tags = document.getElementById('project-tags-'+project_id);
    var description = document.getElementById('project-desc-'+project_id);
    var goals = document.getElementById('project-goals-'+project_id);
    tags.removeAttribute("readonly");
    description.removeAttribute("readonly");
    goals.removeAttribute("readonly");
}

// Project save callback
function projectSave(project_id){
    // var project_update = document.getElementById('update-project-'+project_id);
    // project_update.innerHTML = "<a id='update-action' onclick='projectEdit(\""+project_id+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-editor-mode-edit'></i></a>";
    var tags = document.getElementById('project-tags-'+project_id);
    var description = document.getElementById('project-desc-'+project_id);
    var goals = document.getElementById('project-goals-'+project_id);
    var project = new Project(project_id);
    // tags.setAttribute("readonly", "");
    // description.setAttribute("readonly", "");
    // goals.setAttribute("readonly", "");
    project.save(tags.value, description.value, goals.value);
}

// Project protect callback
function projectProtect(project_id){
    var project_update = document.getElementById('update-project-'+project_id);
    project_update.innerHTML = "<a id='update-action' onclick='projectEdit(\""+project_id+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-editor-mode-edit'></i></a>";
    var tags = document.getElementById('project-tags-'+project_id);
    var description = document.getElementById('project-desc-'+project_id);
    var goals = document.getElementById('project-goals-'+project_id);
    tags.setAttribute("readonly", "");
    description.setAttribute("readonly", "");
    goals.setAttribute("readonly", "");
}

function projectAccess(project_id){
    var p_access = document.getElementById('project-access-'+project_id);
    var project = new Project(project_id);
    project.switchAccess();
}

// Project remove callback
function projectRemove(project_name, project_id){
    Materialize.toast("<span>Delete "+project_name+"</span><a class=\"btn light-blue\" onclick='projectRemoveAgree(\""+project_id+"\");'>Confirm</a>", 5000);
}

// Project remove agreement callback
function projectRemoveAgree(project_id){
    var project = new Project(project_id);
    project.trash();
}