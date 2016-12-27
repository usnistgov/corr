// Env edit callback
function envEdit(env_id){
    var env_update = document.getElementById('update-env-'+env_id);
    env_update.innerHTML = "<a id='update-action' onclick='envSave(\""+env_id+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-content-save'></i></a>";
    var group = document.getElementById('env-group-'+env_id);
    var system = document.getElementById('env-system-'+env_id);
    group.removeAttribute("readonly");
    system.removeAttribute("readonly");
}

// Env save callback
function envSave(env_id){
    var env_update = document.getElementById('update-env-'+env_id);
    env_update.innerHTML = "<a id='update-action' onclick='envEdit(\""+env_id+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-editor-mode-edit'></i></a>";
    var group = document.getElementById('env-group-'+env_id);
    var system = document.getElementById('env-system-'+env_id);
    var env = new Environment(user.session, env_id);
    env.save(group.value, system.value);
}

// Env remove callback
function envRemove(env_id){
    Materialize.toast("<span>Delete "+env_id+"</span><a class=\"btn light-blue\" href=\"http://"+config.host+":"+config.port+"/cloud/v0.1/private/"+user.session+"/env/remove/"+env_id+"\">Confirm</a>", 5000);
}