import httplib
import json

# conn = httplib.HTTPSConnection("http://0.0.0.0:5100")
base = "/api/v0.1"
headers = {"Accept": "application/json"}

def admin_user_create(data={}):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("POST","%s/admin/87b7188171a6f6eed3ce7591ec175fe0e088e43cb282fa21a13a54d07826a073/user/create"%base, json.dumps(data), headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def admin_user_profile_create(user_id="", data={}):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("POST","%s/admin/87b7188171a6f6eed3ce7591ec175fe0e088e43cb282fa21a13a54d07826a073/user/profile/create/%s"%(base, user_id), json.dumps(data), headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def admin_user_profile_show(user_id=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/admin/87b7188171a6f6eed3ce7591ec175fe0e088e43cb282fa21a13a54d07826a073/user/profile/show/%s"%(base, user_id))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def admin_user_show(user_id=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/admin/87b7188171a6f6eed3ce7591ec175fe0e088e43cb282fa21a13a54d07826a073/user/show/%s"%(base, user_id))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def public_user_profile_show(user_id=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/public/user/profile/show/%s"%(base, user_id))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def public_user_show(user_id=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/public/user/show/%s"%(base, user_id))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_profile_show(app_token="", api_token=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/private/%s/%s/profile/show"%(base, api_token, app_token))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def user_show(app_token="", api_token=""):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/private/%s/%s/user/status"%(base, api_token, app_token))
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

# to be deprecated or reserved to admin.
def admin_user_login(data={}):
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("POST","%s/admin/87b7188171a6f6eed3ce7591ec175fe0e088e43cb282fa21a13a54d07826a073/user/login"%base, json.dumps(data), headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def admin_get_users():
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/admin/87b7188171a6f6eed3ce7591ec175fe0e088e43cb282fa21a13a54d07826a073/users"%base)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def public_get_users():
    conn = httplib.HTTPConnection("0.0.0.0", 5100)
    conn.request("GET","%s/public/users"%base)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data
    
if __name__ == '__main__':
    user1 = {
        "email":"u1_corr@corr.gov",
        "password":"U12015",
        "passwordAgain":"U12015",
        "group":"user"
    }
    user2 = {
        "email":"u2_corr@corr.gov",
        "password":"U22015",
        "passwordAgain":"U22015",
        "group":"user"
    }
    dev1 = {
        "email":"d1_corr@corr.gov",
        "password":"D12015",
        "passwordAgain":"D12015",
        "group":"developer"
    }

    # print admin_get_users()
    # print public_get_users()

    # resp1 = json.loads(admin_user_create(user1))
    # resp2 = json.loads(admin_user_create(user2))
    # resp3 = json.loads(admin_user_create(dev1))

    # print resp1
    # print resp2
    # print resp3

    profile_user1 = {
        "fname":"User1",
		"lname":"CoRR",
		"about":"I am one of CoRR early stage User1."
    }
    profile_user2 = {
        "fname":"User2",
		"lname":"CoRR",
		"about":"I am one of CoRR early stage User2."
    }
    profile_dev1 = {
        "fname":"Developer1",
		"lname":"CoRR",
		"about":"I am one of CoRR early stage App developer1."
    }

    # if resp1['code'] == 201:
    #     print user_profile_create(resp1['content']['id'], profile_user1)
    #     del user1['group']
    #     resp11 = user_login(user1)
    #     print user_profile_show(resp1['content']['id'])
    # else:
    #     print '%d: %s'%(resp1['code'], resp1['content'])

    # if resp2['code'] == 201:
    #     print user_profile_create(resp2['content']['id'], profile_user2)
    #     del user2['group']
    #     resp21 = user_login(user2)
    #     print user_profile_show(resp2['content']['id'])
    # else:
    #     print '%d: %s'%(resp1['code'], resp1['content'])

    # if resp3['code'] == 201:
    #     print user_profile_create(resp3['content']['id'], profile_user3)
    #     del user3['group']
    #     resp31 = user_login(user3)
    #     print user_profile_show(resp3['content']['id'])
    # else:
    #     print '%d: %s'%(resp1['code'], resp1['content'])


    # print admin_user_profile_create('56f003399f9d51782907bb23', profile_user1)
    # print admin_user_profile_create('56f004079f9d51790fa83168', profile_user2)
    # print admin_user_profile_create('56f004079f9d51790fa8316a', profile_dev1)

    # del user1['group']
    # del user2['group']
    # del dev1['group']

    # print admin_user_login(user1)
    # print admin_user_login(user2)
    # print admin_user_login(dev1)

    # print admin_user_show('56f003399f9d51782907bb23')
    # print admin_user_show('56f004079f9d51790fa83168')
    # print admin_user_show('56f004079f9d51790fa8316a')

    # print public_user_show('56f003399f9d51782907bb23')
    # print public_user_show('56f004079f9d51790fa83168')
    # print public_user_show('56f004079f9d51790fa8316a')

    # print user_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '4e785500d0f3c132a5151e22a4f6b3cb5369d25bfee54cc60c592d58596cd050')
    # print user_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '761af78a0a0d4663be6879f9f7da2e14893aaa7e8a2f39e17b1df0eeec9e1faa')
    # print user_show('b4063dd1c02084ea5b4fbdd7eea4a2e4248b3605b0cb7f6e18d021e2d987106b', 'c81422a6752a34539a78bcdf90153944611bd0a4088efc800c1cc6a57bb02682')

    # print admin_user_profile_show('56f003399f9d51782907bb23')
    # print admin_user_profile_show('56f004079f9d51790fa83168')
    # print admin_user_profile_show('56f004079f9d51790fa8316a')

    # print public_user_profile_show('56f003399f9d51782907bb23')
    # print public_user_profile_show('56f004079f9d51790fa83168')
    # print public_user_profile_show('56f004079f9d51790fa8316a')

    # print user_profile_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '4e785500d0f3c132a5151e22a4f6b3cb5369d25bfee54cc60c592d58596cd050')
    # print user_profile_show('9646216f8e0001cc4bd26dd6fcd213b50f4e44ddeee74c78436677bebc67aee9', '761af78a0a0d4663be6879f9f7da2e14893aaa7e8a2f39e17b1df0eeec9e1faa')
    # print user_profile_show('b4063dd1c02084ea5b4fbdd7eea4a2e4248b3605b0cb7f6e18d021e2d987106b', 'c81422a6752a34539a78bcdf90153944611bd0a4088efc800c1cc6a57bb02682')

    