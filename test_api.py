import urllib.request, json
url = "http://127.0.0.1:8090/api/camera"
def post(data):
    req = urllib.request.Request(url, data=json.dumps(data).encode(), method="POST")
    urllib.request.urlopen(req)

post({"action": "torch", "value": True})
post({"action": "torch", "value": False})
post({"action": "night_vision", "value": "on"})
post({"action": "night_vision", "value": "off"})
print("Success!")
