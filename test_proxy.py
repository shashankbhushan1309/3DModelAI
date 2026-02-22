import json, urllib.request

req = urllib.request.Request(
    url="http://127.0.0.1:8000/api/generate",
    data=json.dumps({"prompt": "Create a simple 20x20x20 mm box"}).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
print("Testing directly against backend at 127.0.0.1:8000...")
try:
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print("SUCCESS!")
        print("Status:", data.get("status"))
        print("STL URL:", data.get("stl_url"))
        print("Code:", data.get("code", "")[:300])
except Exception as e:
    print("ERROR:", e)
    if hasattr(e, 'read'):
        print(e.read().decode('utf-8'))
