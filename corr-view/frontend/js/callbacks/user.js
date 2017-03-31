// User edit callback
function userEdit(user_id){
    var user_update = document.getElementById('update-project-'+user_id);
    user_update.innerHTML = "<a id='update-action' onclick='userSave(\""+user_id+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-content-save'></i></a>";
    var fname = document.getElementById('user-fname-'+user_id);
    var lname = document.getElementById('user-lname-'+user_id);
    var group = document.getElementById('user-group-'+user_id);
    var auth = document.getElementById('user-auth-'+user_id);
    var org = document.getElementById('user-org-'+user_id);
    var about = document.getElementById('user-about-'+user_id);
    fname.removeAttribute("readonly");
    lname.removeAttribute("readonly");
    group.removeAttribute("readonly");
    auth.removeAttribute("readonly");
    org.removeAttribute("readonly");
    about.removeAttribute("readonly");
}

// User save callback
function userSave(user_id){
    var user_update = document.getElementById('update-project-'+user_id);
    user_update.innerHTML = "<a id='update-action' onclick='userEdit(\""+user_id+"\");' class='btn-floating activator btn-move-up waves-effect waves-light darken-2 right'><i class='mdi-editor-mode-edit'></i></a>";
    var fname = document.getElementById('user-fname-'+user_id);
    var lname = document.getElementById('user-lname-'+user_id);
    var group = document.getElementById('user-group-'+user_id);
    var auth = document.getElementById('user-auth-'+user_id);
    var org = document.getElementById('user-org-'+user_id);
    var about = document.getElementById('user-about-'+user_id);
    console.log('Cookie session value: '+ Cookies.get('session'));
    fname.setAttribute("readonly", "");
    lname.setAttribute("readonly", "");
    group.setAttribute("readonly", "");
    auth.setAttribute("readonly", "");
    org.setAttribute("readonly", "");
    about.setAttribute("readonly", "");
    var account = new Account(user_id);
    account.save(fname.value, lname.value, group.value, auth.value, organization.value, about.value);
    // Make account object in contents.js and a save function for edit make sure it is in cloud/user/edit.
    // Add auth and group in edit for admin user. Maybe recreate another user edit for admin.
}