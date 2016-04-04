import httplib
import json

# conn = httplib.HTTPSConnection("http://0.0.0.0:5100")
# Root CoRR api token.
base = "/api/v0.1/87b7188171a6f6eed3ce7591ec175fe0e088e43cb282fa21a13a54d07826a073/admin"
headers = {"Accept": "application/json"}

def app_create(data={}):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("POST","%s/app/create"%base, json.dumps(data), headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def app_show(app_id=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/app/show/%s"%(base, app_id))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def app_delete(app_id=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/app/delete/%s"%(base, app_id))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def get_apps():
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/apps"%base)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

if __name__ == '__main__':


    app1 = {
        "developer":"56f004079f9d51790fa8316a",
        "name":"CoRR-Cmd",
        "about":"This application is the CoRR native client. It is an event based simulation management tool. It uses the system calls and processes table stack and some information extraction to make the record more sustainable and reusable. CoRR-Cmd support parallel and distributed simulation."
    }
    app2 = {
        "developer":"56f004079f9d51790fa8316a",
        "name":"Sumatra",
        "about":"Sumatra is a tool for managing and tracking projects based on numerical simulation and/or analysis, with the aim of supporting reproducible research. It can be thought of as an automated electronic lab notebook for computational projects."
    }

    # print get_apps()

    # print app_create(app1)
    # print app_create(app2)

    # print get_apps()

    # print app_show('56f0065f9f9d5179bb5569c6')
    # print app_show('56f0065f9f9d5179bb5569c9')

    # print app_delete('56f0065f9f9d5179bb5569c6')
    # print app_delete('56f0065f9f9d5179bb5569c9')

    # print get_apps()

    # print app_show('56f0065f9f9d5179bb5569c6')
    # print app_show('56f0065f9f9d5179bb5569c9')
