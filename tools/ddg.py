import urllib.request, json, urllib.parse
query = urllib.parse.quote('site:github.com "IP Webcam" "Pavel" "settings" "night_vision"')
url = f"https://html.duckduckgo.com/html/?q={query}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        print(response.read().decode('utf-8')[:2000])
except Exception as e:
    print(e)
