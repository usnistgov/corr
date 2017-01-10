// Application edit callback
function appEdit(app_id){
    var app_update = document.getElementById('update-app-'+app_id);
    app_update.innerHTML = "<a id='update-action' onclick='appSave(\""+app_id+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-content-save'></i></a>";
    var name = document.getElementById('app-name-'+app_id);
    var network = document.getElementById('app-network-'+app_id);
    var about = document.getElementById('app-about-'+app_id);
    var access = document.getElementById('app-access-'+app_id);
    name.removeAttribute("readonly");
    network.removeAttribute("readonly");
    about.removeAttribute("readonly");
    access.removeAttribute("readonly");
}

// Application save callback
function appSave(app_id){
    var app_update = document.getElementById('update-app-'+app_id);
    app_update.innerHTML = "<a id='update-action' onclick='appEdit(\""+app_id+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-editor-mode-edit'></i></a>";
    var name = document.getElementById('app-name-'+app_id);
    var network = document.getElementById('app-network-'+app_id);
    var about = document.getElementById('app-about-'+app_id);
    var access = document.getElementById('app-access-'+app_id);
    var app = new Application(app_id);
    app.save(name.value, network.value, about.value, access.value);
}

// Application remove callback
function appRemove(app_name, app_id){
    Materialize.toast("<span>Delete "+app_name+"</span><a class=\"btn light-blue\" href=\""+config.mode+"://"+config.host+":"+config.port+"/cloud/v0.1/private/"+Cookies.get('session')+"/app/remove/"+app_id+"\">Confirm</a>", 5000);
}

// Application remove agreement callback
function appRemoveAgree(app_id){
    console.log("in appRemoveAgree!");
    var app = new Application(app_id);
    app.trash();
    window.location.reload();
}