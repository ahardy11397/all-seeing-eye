import urllib.request, json
url = "https://api.github.com/search/code?q=night_vision+repo:home-assistant/core+path:homeassistant/components/android_ip_webcam"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        print(response.read().decode('utf-8')[:500])
except Exception as e:
    print(e)
