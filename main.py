import json

with open('heritage_sites.json', 'r', encoding='utf-8') as file:
    heritage_sites = json.load(file)

for site in heritage_sites:
    print(f"🏛️ {site['name']} — {site['location']}")
    print(f"  Facts: {site['facts']}")
    print(f"  Precautions: {', '.join(site['precautions'])}")
    print("-" * 50)
