import httplib
import json
import re
import requests
import thread
import daemon

# conn = httplib.HTTPSConnection("http://0.0.0.0:5100")
base = "/api/v0.1/private/4e785500d0f3c132a5151e22a4f6b3cb5369d25bfee54cc60c592d58596cd050"
headers = {"Accept": "application/json"}

def user_status(app_token=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/%s/user/status"%(base, app_token))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_home(app_token=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/%s/user/home"%(base, app_token))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_search(app_token="", user_name=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/%s/user/search/%s"%(base, app_token, user_name))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_app_connectivity(app_token=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/%s/connectivity"%(base, app_token))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

# Messages
def user_message_create(app_token="", data={}):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("POST","%s/%s/message/create"%(base, app_token), json.dumps(data), headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_message_show(app_token="", message_id=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/%s/message/show/%s"%(base, app_token, message_id))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_message_update(app_token="", message_id="", data={}):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("POST","%s/%s/message/update/%s"%(base, app_token,message_id), json.dumps(data), headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_message_delete(app_token="", message_id=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/%s/message/delete/%s"%(base, app_token, message_id))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_get_messages(app_token=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/%s/messages"%(base, app_token))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

# Files
def user_file_create(app_token="", data={}):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("POST","%s/%s/file/create"%(base, app_token), json.dumps(data), headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_file_show(app_token="", file_id=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/%s/file/show/%s"%(base, app_token, file_id))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_file_update(app_token="", file_id="", data={}):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("POST","%s/%s/file/update/%s"%(base, app_token,file_id), json.dumps(data), headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_file_delete(app_token="", file_id=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/%s/file/delete/%s"%(base, app_token, file_id))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_file_upload(app_token="", group='unknown', item_id="", file_name=""):
    url = "http://0.0.0.0:5100%s/%s/file/upload/%s/%s"%(base, app_token,group,item_id)
    files = {'file': open('%s'%file_name)}
    response = requests.post(url, files=files)
    return response.content

def user_file_download(app_token="", file_id=""):
    url = "http://0.0.0.0:5100%s/%s/file/download/%s"%(base, app_token, file_id)
    # conn = httplib.HTTPConnection("0.0.0.0", 5100)
    # conn.request("GET","%s/%s/file/download/%s"%(base, app_token, file_id))
    # response = conn.getresponse()
    response = requests.get(url)
    # return "Headers: %s"%response.headers
    content = response.content
    fname = "unknown-name"
    try:
        d = response.headers['Content-Disposition']
        fname = re.findall("filename=(.+)", d)
    except:
        pass
    with open(fname[0], 'w') as downloaded_f:
        downloaded_f.write(content)
    return '%s Downloaded'%fname

def user_get_files(app_token=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/%s/files"%(base, app_token))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

# Projects
def user_project_create(app_token="", data={}):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("POST", "%s/%s/project/create"%(base, app_token), json.dumps(data), headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_project_show(app_token="", project_id=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/%s/project/show/%s"%(base, app_token, project_id))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_project_delete(app_token="", project_id=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/%s/project/delete/%s"%(base, app_token, project_id))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_get_projects(app_token=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/%s/projects"%(base, app_token))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data


# +++ Records

def user_record_create(app_token="", project_id="", data={}):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("POST", "%s/%s/project/record/create/%s"%(base, app_token, project_id), json.dumps(data), headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_record_show(app_token="", record_id=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/%s/record/show/%s"%(base, app_token, record_id))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_record_update(app_token="", record_id="", data={}):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("POST", "%s/%s/record/update/%s"%(base, app_token, record_id), json.dumps(data), headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_record_delete(app_token="", record_id=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/%s/record/delete/%s"%(base, app_token, record_id))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_get_records(app_token="", project_id=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/%s/project/records/list/%s"%(base, app_token, project_id))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_download_record(app_token="", record_id=""):
    url = "http://0.0.0.0:5100%s/%s/record/download/%s"%(base, app_token, record_id)
    response = requests.get(url)
    content = response.content
    try:
        d = response.headers['Content-Disposition']
        fname = re.findall("filename=(.+)", d)
    except:
        fname = "unknown-name"
    with open(fname[0], 'w') as downloaded_f:
        downloaded_f.write(content)
    return '%s Downloaded'%fname

# --- Diff

def user_diff_create(app_token="", data={}):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("POST","%s/%s/diff/create"%(base, app_token), json.dumps(data), headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_diff_show(app_token="", diff_id=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/%s/diff/show/%s"%(base, app_token, diff_id))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_diff_update(app_token="", diff_id="", data={}):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("POST","%s/%s/diff/update/%s"%(base, app_token,diff_id), json.dumps(data), headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_get_diffs(app_token=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/%s/diffs"%(base, app_token))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

# --- Env

def user_update_env_bundle(app_token="", bundle="", file_name=""):
    def handle_file_resolution(bundle, file_name):
        url = "http://0.0.0.0:5100%s/%s/file/upload/bundle/%s"%(base, app_token, bundle)
        files = {'file': open('%s'%file_name)}
        response = requests.post(url, files=files)
        print response.content
        with open('user-bundle-%s-upload.log'%bundle, 'w') as bundle_log:
            bundle_log.write(response.content)

    # handle_file_resolution(bundle, file_name)
    with daemon.DaemonContext():
        handle_file_resolution(bundle, file_name)
    # thread.start_new_thread(handle_file_resolution, (bundle, file_name,))
    # t = threading.Thread(target = handle_file_resolution, args=(bundle, file_name,)).start()    
    return 'Thread sheduled for upload!'

def user_project_env_next(app_token="", project_id="", data={}):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("POST","%s/%s/project/env/next/%s"%(base, app_token, project_id), json.dumps(data), headers)
    response = conn.getresponse()
    print response.status
    data = response.read()
    conn.close()
    return data

def user_project_env_update(app_token="", project_id="", env_id="", data={}):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("POST","%s/%s/project/env/update/%s/%s"%(base, app_token, project_id, env_id), json.dumps(data), headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_project_envs(app_token="", project_id=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/%s/project/envs/%s"%(base, app_token, project_id))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_project_envs_head(app_token="", project_id=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/%s/project/envs/head/%s"%(base, app_token, project_id))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_project_env_show(app_token="", project_id="", env_id=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/%s/project/env/show/%s/%s"%(base, app_token, project_id, env_id))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

if __name__ == '__main__':

    # print user_status('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9')
    # print user_home('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9')
    # print user_search('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', 'User2-CoRR')
    # print user_search('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', 'CoRR')

    # print user_app_connectivity('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9')
    
    message1 = {
        "receiver":"56f004079f9d51790fa83168",
        "title":"Test New Message 1",
        "content":"This is a test from user api."
    }

    message2 = {
        "receiver":"56f004079f9d51790fa83168",
        "title":"Test New Message 2",
        "content":"This is another test from user api."
    }

    message3 = {
        "receiver":"56f004079f9d51790fa83168",
        "title":"Test New Message 3",
        "content":"This is yet another test from user api."
    }

    # print user_get_messages('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9')
    # print user_message_create('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', message1)
    # print user_message_create('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', message2)
    # print user_message_create('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', message3)
    # print user_get_messages('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9')
    # print user_message_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f028d89f9d510187653211')
    # message3['content'] = 'This is yet another updated message done from the user api.'
    # print user_message_update('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f028d89f9d510187653211', message3)
    # print user_message_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f028d89f9d510187653211')
    # print user_message_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f028d89f9d510187653210')
    # print user_message_delete('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f028d89f9d510187653210')
    # print user_message_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f028d89f9d510187653210')


    file1 = {
        "name":"Another reference to pymks-paper-2015.pdf",
        "storage":"566b18159f9d516b595d7e19_pymks-paper-2015.pdf",
        "group": "resource",
        "description":"This a resource pdf file of a PyMKS paper."
    }

    file2 = {
        "name":"An Introduction to Quantum Computing",
        "storage":"http://sergeev.fiz.univ.szczecin.pl/Dydaktyka/Wyklady/Kaye.pdf",
        "group": "file",
        "access": "private",
        "description":"We have offered a course at the University of Waterloo in quantum comput-\
                       ing since 1999. We have had students from a variety of backgrounds take the\
                       course, including students in mathematics, computer science, physics, and engi-\
                       neering. While there is an abundance of very good introductory papers, surveys\
                       and books, many of these are geared towards students already having a strong\
                       background in a particular area of physics or mathematics."
    }

    # print user_get_files('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9')
    # print user_file_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f0065f9f9d5179bb5569c5')
    # print user_file_download('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f0065f9f9d5179bb5569c5')
    # print user_file_create('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', file1)
    # print user_file_create('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', file2)
    # print user_get_files('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9')

    # print user_file_upload('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', 'attach-message', '56f028d89f9d510187653211', '0602096.pdf')
    # print user_get_files('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9')
    # # Show the uploaded file and download it.
    # print user_file_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f02f2a9f9d51041c2c9e01')
    # print user_file_download('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f02f2a9f9d51041c2c9e01')

    #File 2 download
    # print user_file_download('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f02c169f9d51031bf667e1')

    # file1['description'] = 'This is an updated description of the PyMKS paper.'
    # print user_file_update('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f02bf99f9d51031bf667df', file1)
    # print user_file_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f02bf99f9d51031bf667df')

    # # File 1 delete
    # print user_file_delete('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f02bf99f9d51031bf667df')
    # print user_file_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f02bf99f9d51031bf667df')

    
    project1 = {
        "name":"Python-Qrcode",
        "description":"This module uses image libraries, Python Imaging Library (PIL) by default, to generate QR Codes. It is recommended to use the pillow fork rather than PIL itself.",
        "goals":"A Quick Response code is a two-dimensional pictographic code used for its fast readability and comparatively large storage capacity. The code consists of black modules arranged in a square pattern on a white background. The information encoded can be made up of any kind of data (e.g., binary, alphanumeric, or Kanji symbols)",
        "tags":["code","unique","pictographic"],
        "group":"computational"
    }
    project2 = {
        "name":"Muon Detector Simulation",
        "description":"This program allows the user to simulate a Muon Detector with a specified number of Muons at a specified starting energy in MeV.",
        "goals":"To get the program to work the user needs to change the path for which they want the two, final, comma seperated value file to save to this can be located in the 'Histogram' class under the method 'writeToDisk'. If the user does not specify the file path before running the program then it will not save the data for simulated muon paths. The data can be observed in Microsoft Excel by plotting the x-postion or Bin value against both energy and y-value depending on which comma seperated value file was opened. The user can also add aditional detector materials and create instances to do this. The detector is currently made from Iron this is a dense material that Muons will interact with.",
        "tags":["simulation","muon","tomography"],
        "group":"computational"
    }

    # print user_get_projects('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9')
    # print user_project_create('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', project1)
    # print user_project_create('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', project2)
    # print user_get_projects('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9')


    env1 = {
        "group":"computational",
        "system":"container-based",
        "specifics":{'container-system':'docker', 'container-version':'1.0'},
        "version":{
            "system":"git",
            "baseline":"develop",
            "marker":"9c264611cf9af99057ac31d3f863fa300da8e2d7"
        },
        "bundle":{
            "location":"https://s3-us-west-2.amazonaws.com/ddsm-bucket/5595f1b789adcc1556eb41cd-5597914cc922f075f076fa35-unknown.tar"
        }
    }
    env2 = {
        "group":"computational",
        "system":"container-based",
        "specifics":{'container-system':'docker', 'container-version':'1.0'},
        "version":{
            "system":"git",
            "baseline":"master",
            "marker":"35d3d3de724af4dec758be1c02fb56f0600b16b8"
        },
        "bundle":{
            "location":"https://s3-us-west-2.amazonaws.com/ddsm-bucket/5595f1b789adcc1556eb41cd-559aa346c922f009dbc3b872-unknown.tar"
        }
    }

    env3 = {
        "group":"computational",
        "system":"container-based",
        "specifics":{'container-system':'docker', 'container-version':'1.0'},
        "version":{
            "system":"git",
            "baseline":"master",
            "marker":"35d3d3de724af4dec758be1c02fb56f0600b1634"
        },
        "bundle":{
            "location":"https://s3-us-west-2.amazonaws.com/ddsm-bucket/5595f1b789adcc1556eb41cd-559aa346c922f009dbc3b872-unknown.tar"
        }
    }

    # print user_project_envs_head('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e204')
    # print user_project_envs_head('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e207')
    # print user_project_envs_head('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '568409159f9d5136e4351029')
    
    # print user_project_envs('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e204')
    # print user_project_envs('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e207')

    # print user_project_env_next('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e204', env1)
    # print user_project_env_next('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e207', env2)
    # print user_project_env_next('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '568409159f9d5136e4351029', env3)

    # print user_project_envs_head('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e204')
    # print user_project_envs_head('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e207')

    # print user_project_envs('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e204')
    # print user_project_envs('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e207')

    # print user_project_env_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e204', '56f038189f9d5106ecaa3bfe')
    # print user_project_env_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e207', '56f038189f9d5106ecaa3c01')
    # print user_project_env_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e207', '5684068b9f9d5134b5e01338')
    # print user_project_env_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '568409159f9d5136e4351029', '56840b129f9d5137d5675488')
    
    # !!!Second parameter is the bundle id.
    # print user_update_env_bundle('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f038189f9d5106ecaa3c00', '/home/fyc/Documents/Projects/NIST/CoRR/github/demo-sumatra.tar')
    # print user_update_env_bundle('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f038189f9d5106ecaa3c03', '/home/fyc/Documents/Projects/NIST/CoRR/github/presentation_11-23-2015.pdf')
    # print user_update_env_bundle('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56747b939f9d51373dc0a5ec', '/home/fyc/Documents/Projects/NIST/CoRR/github/Howe_chapter.pdf')
    # print user_project_env_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e204', '56f038189f9d5106ecaa3bfe')
    # print user_project_env_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e207', '56f038189f9d5106ecaa3c01')
    # print user_project_env_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e207', '5684068b9f9d5134b5e01338')
    # print user_project_env_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '568409159f9d5136e4351029', '56840b129f9d5137d5675488')
    # env2['bundle']['location'] = "https://s3-us-west-2.amazonaws.com/ddsm-bucket/5595f1b789adcc1556eb41cd-5597914cc922f075f076fa35-unknown.tar"
    # print user_project_env_update('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e207', '56f038189f9d5106ecaa3c01', env2)
    # print user_project_env_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e207', '56f038189f9d5106ecaa3c01')

    # print user_project_env_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e204', '56f038189f9d5106ecaa3bfe')
    # print user_project_env_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e207', '56f038189f9d5106ecaa3c01')
    # print user_project_env_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e207', '5684068b9f9d5134b5e01338')
    # print user_project_env_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '568409159f9d5136e4351029', '56840b129f9d5137d5675488')


    # Records

    record1 = {
        "project":"56f035f89f9d51064e12e204",
        "system":{
            "architecture_bits": "64bit",
            "architecture_linkage": "ELF",
            "ip_addr": "127.0.0.1",
            "machine": "x86_64",
            "network_name": "606d8d28528d",
            "processor": "Intel Core i7-4470HQ CPU @ 2.20Ghz x 8",
            "gpu":"Intel Iris Pro Graphics 5200 (GT3 + 128 MB eDRAM)",
            "release": "3.19.0-18-generic",
            "system_name": "Linux",
            "distribution": "Ubuntu 15.04",
            "version": "#18-Ubuntu SMP Tue May 19 18:31:35 UTC 2015"
        },
        "inputs":[
            {
                "parameters": {

                    "content": "modulus = 100, 120 # Elastic modulus\nratio = 0.3, 0.3 # Poissons ratio\nstrain = 0.02 # Macro strain\nsize = 21, 21 # Microstructure size",
                    "type": "SimpleParameterSet"
                }
            },
            {
                "script_arguments": "<parameters>"
            }
        ],
        "outputs":[
            {
                "creation": "2015-07-01 04:53:59",
                "digest": "43a47cb379df2a7008fdeb38c6172278d000fdc4",
                "metadata": {
                    "encoding": '',
                    "mimetype": '',
                    "size": 2500
                },
                "path": "example2.dat"
            }
        ],
        "dependencies":[
            {
                "diff": "",
                "module": "python",
                "name": "_markerlib",
                "path": "/usr/lib/python2.7/dist-packages/_markerlib",
                "source": '',
                "version": "unknown"
            },
            {
                "diff": "",
                "module": "python",
                "name": "numpy",
                "path": "/usr/lib/python2.7/dist-packages/numpy",
                "source": "attribute",
                "version": "1.8.2"
            },
            {
                "diff": "",
                "module": "python",
                "name": "pymks",
                "path": "/usr/lib/python2.7/dist-packages/pymks",
                "source": "attribute",
                "version": "0.2.3"
            },
            {
                "diff": "",
                "module": "python",
                "name": "setuptools",
                "path": "/usr/lib/python2.7/dist-packages/setuptools",
                "source": "attribute",
                "version": "3.3"
            }
        ],
        "status":"running",
        "rationels":[
            "Compute the linear strain field for a two phase composite material",
            "Linear Elasticity in 2D"
        ]
    }

    record2 = {
        "project":"56f035f89f9d51064e12e207",
        "system":{
            "architecture_bits": "64bit",
            "architecture_linkage": "ELF",
            "ip_addr": "127.0.0.1",
            "machine": "x86_64",
            "network_name": "606d8d28528d",
            "processor": "Intel Core i7-4470HQ CPU @ 2.20Ghz x 8",
            "gpu":"Intel Iris Pro Graphics 5200 (GT3 + 128 MB eDRAM)",
            "release": "3.19.0-18-generic",
            "system_name": "Linux",
            "distribution": "Ubuntu 15.04",
            "version": "#18-Ubuntu SMP Tue May 19 18:31:35 UTC 2015"
        },
        "inputs":[
            {
                "script_arguments": "<parameters>"
            }
        ],
        "outputs":[
            {
                    "stdout_stderr": "Not launched."
            },
            {
                "stdout_stderr": "No output."
            }
        ],
        "dependencies":[
            {
                "diff": "",
                "module": "python",
                "name": "_markerlib",
                "path": "/usr/lib/python2.7/dist-packages/_markerlib",
                "source": '',
                "version": "unknown"
            },
            {
                "diff": "",
                "module": "python",
                "name": "numpy",
                "path": "/usr/lib/python2.7/dist-packages/numpy",
                "source": "attribute",
                "version": "1.8.2"
            },
            {
                "diff": "",
                "module": "python",
                "name": "fipy",
                "path": "/usr/lib/python2.7/dist-packages/fipy",
                "source": "attribute",
                "version": "3.1"
            },
            {
                "diff": "",
                "module": "python",
                "name": "setuptools",
                "path": "/usr/lib/python2.7/dist-packages/setuptools",
                "source": "attribute",
                "version": "3.3"
            }
        ],
        "status":"starting",
        "rationels":[
            "First record",
            "Simple example for integration",
            "Crank-Nicholson transient diffusion"
        ]
    }

    record3 = {
        "project":"568409159f9d5136e4351029",
        "system":{
            "architecture_bits": "64bit",
            "architecture_linkage": "ELF",
            "ip_addr": "127.0.0.1",
            "machine": "x86_64",
            "network_name": "606d8d28528d",
            "processor": "Intel Core i7-4470HQ CPU @ 2.20Ghz x 8",
            "gpu":"Intel Iris Pro Graphics 5200 (GT3 + 128 MB eDRAM)",
            "release": "3.19.0-18-generic",
            "system_name": "Linux",
            "distribution": "Ubuntu 15.04",
            "version": "#18-Ubuntu SMP Tue May 19 18:31:35 UTC 2015"
        },
        "inputs":[
            {
                "script_arguments": "<parameters>"
            }
        ],
        "outputs":[
            {
                    "stdout_stderr": "Not launched."
            },
            {
                "stdout_stderr": "No output."
            }
        ],
        "dependencies":[
            {
                "diff": "",
                "module": "python",
                "name": "_markerlib",
                "path": "/usr/lib/python2.7/dist-packages/_markerlib",
                "source": '',
                "version": "unknown"
            },
            {
                "diff": "",
                "module": "python",
                "name": "numpy",
                "path": "/usr/lib/python2.7/dist-packages/numpy",
                "source": "attribute",
                "version": "1.8.2"
            },
            {
                "diff": "",
                "module": "python",
                "name": "fipy",
                "path": "/usr/lib/python2.7/dist-packages/scikitlearn",
                "source": "attribute",
                "version": "2.9"
            },
            {
                "diff": "",
                "module": "python",
                "name": "setuptools",
                "path": "/usr/lib/python2.7/dist-packages/setuptools",
                "source": "attribute",
                "version": "3.3"
            }
        ],
        "status":"starting",
        "rationels":[
            "Test record",
            "Machine learning test"
        ]
    }

    # print user_get_records('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e204')
    # print user_get_records('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e207')
    # print user_get_records('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '568409159f9d5136e4351029')

    # print user_record_create('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e204', record1)
    # print user_record_create('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e207', record2)
    # print user_record_create('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '568409159f9d5136e4351029', record3)

    # print user_get_records('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e204')
    # print user_get_records('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f035f89f9d51064e12e207')
    # print user_get_records('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '568409159f9d5136e4351029')

    # print user_record_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f045ca9f9d510b764381f1')
    # print user_record_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f045ca9f9d510b764381f4')
    # print user_record_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '568550149f9d513065c68b36')
    # print user_record_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '568550149f9d513065c68b38')

    # print user_record_update('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f045ca9f9d510b764381f1', {'access':'public'})
    # print user_record_update('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f045ca9f9d510b764381f4', {'access':'private'})
    # print user_record_update('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '568550149f9d513065c68b36', {'access':'public'})
    # print user_record_update('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '568550149f9d513065c68b38', {'access':'public'})

    # print user_record_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f045ca9f9d510b764381f1')
    # print user_record_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f045ca9f9d510b764381f4')
    # print user_record_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '568550149f9d513065c68b36')
    # print user_record_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '568550149f9d513065c68b38')

    # print user_download_record('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f045ca9f9d510b764381f1')

    # ++ Diff
    diff1 = {
        "from":"56f045ca9f9d510b764381f4",
        "to":"56f045ca9f9d510b764381f1",
        "method":"default",
        "proposition":"reproduced",
        "status":"proposed"
    }

    diff2 = {
        "from":"568550149f9d513065c68b36",
        "to":"568550149f9d513065c68b33",
        "method":"visual",
        "proposition":"reproduced",
        "status":"proposed"
    }

    # print user_get_diffs('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9')

    # print user_diff_create('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', diff1)
    # print user_diff_create('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', diff2)

    # print user_get_diffs('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9')

    # print user_diff_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f04ed99f9d510e567e7623')
    # print user_diff_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '5685596a9f9d514743604332')

    # diff1['status'] = 'agreed'

    # print user_diff_update('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f04ed99f9d510e567e7623', diff1)

    # print user_diff_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '56f04ed99f9d510e567e7623')


























