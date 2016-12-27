// Search processor
function processSearch()
{
    var query_search = document.getElementById("search").value;
    var usersQ = document.getElementById("exclude-users").checked;
    var applicationsQ = document.getElementById("exclude-applications").checked;
    var projectsQ = document.getElementById("exclude-projects").checked;
    var recordsQ = document.getElementById("exclude-records").checked;
    var diffsQ = document.getElementById("exclude-diffs").checked;
    Materialize.toast("<span>Exclude Users: "+usersQ+" Exclude Apps: "+applicationsQ+" Exclude Projects: "+projectsQ+" Exclude Records: "+recordsQ+" Exclude Diffs: "+diffsQ+" </span>", 5000);
    space.query(query_search, usersQ, applicationsQ, projectsQ, recordsQ, diffsQ);
}

// Search link sub research injection
function customSearch(type, value)
{
    if(type == "user"){
        document.getElementById("search").value = value;
        document.getElementById("exclude-users").checked = false;
        document.getElementById("exclude-applications").checked = true;
        document.getElementById("exclude-projects").checked = true;
        document.getElementById("exclude-records").checked = true;
    }else if(type == "project"){
        document.getElementById("search").value = value;
        document.getElementById("exclude-users").checked = true;
        document.getElementById("exclude-applications").checked = true;
        document.getElementById("exclude-projects").checked = false;
        document.getElementById("exclude-records").checked = true;
    }
    processSearch();
}

// Enter key for search process trigger.
function searchKeyPress(e)
{
    e = e || window.event;
    if (e.keyCode == 13)
    {
        processSearch();
    }
}