import urllib.request
import json

urls = {
    "warp": "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/warp.svg",
    "arc": "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/arc.svg",
    "postman": "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/postman.svg",
    "davinciresolve": "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/davinciresolve.svg",
    "lightroom": "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/adobelightroom.svg",
    "lightroomclassic": "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/adobelightroomclassic.svg",
    "vscode": "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/visualstudiocode.svg"
}

results = {}
for name, url in urls.items():
    try:
        print(f"Fetching {name}...")
        with urllib.request.urlopen(url) as response:
            html = response.read().decode('utf-8')
            results[name] = html
            print(f"  Success ({len(html)} bytes)")
    except Exception as e:
        print(f"  Failed {name}: {e}")

with open("fetched_svgs.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print("Done writing fetched_svgs.json")
