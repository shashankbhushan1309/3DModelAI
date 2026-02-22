import json
import urllib.request

req = urllib.request.Request(
    url="http://localhost:8000/api/generate",
    data=json.dumps({"prompt": "Create a parametric cube 20x20x20 mm with a 10mm hole in the middle"}).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

print("Sending generation request to the backend...")
try:
    with urllib.request.urlopen(req) as response:
        print("Status", response.status)
        print(response.read().decode("utf-8"))
except Exception as e:
    print(e)
    if hasattr(e, 'read'):
        print(e.read().decode('utf-8'))
