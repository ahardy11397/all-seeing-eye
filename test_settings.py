import urllib.request, json
url = "http://127.0.0.1:8090/api/settings"
def post(data):
    req = urllib.request.Request(url, data=json.dumps(data).encode(), method="POST")
    return urllib.request.urlopen(req).read()

def get():
    req = urllib.request.Request("http://127.0.0.1:8090/api/state")
    return json.loads(urllib.request.urlopen(req).read())

print("Before:", get()["settings"]["min_confidence"])
post({"min_confidence": 0.88})
print("After:", get()["settings"]["min_confidence"])
