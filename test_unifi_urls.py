import http.client
import json

conn = http.client.HTTPSConnection("api.ui.com")
headers = {
    'Accept': 'application/json',
    'X-API-Key': 'nMUrZf3r-Lt_O0m_tPMmqrUofJsyMWag'
}
conn.request("GET", "/v1/clients/main", "", headers)
res = conn.getresponse()
data = res.read()
json_data = json.loads(data.decode("utf-8"))
print(json.dumps(json_data, indent=2, ensure_ascii=False))
conn.close()