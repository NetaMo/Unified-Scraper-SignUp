import requests

### Syntax for sending chat in json format###

# The data to be sent, in json format
data1 = {"contact":{"name":"asaf", "type":"person"}, "messages":[{"name":"asaf", "text":"hi moses!", "time":"5:22 PM, 4/7/2016"}, {"name":"moses", "text":"××” ×›×•×©×™ ×©×œ×™", "time":"5:23 PM, 4/7/2016"}]}
# The Server adress, notice the handler name at the end
url = "http://localhost:8888/chat"
# The content type
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
# The actual post request
r = requests.post(url, json=data1, headers=headers)

### Syntax for sending end of session and user name ###

data2 = {"userName": "tahat"}
url = "http://localhost:8888/chatFinished"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
r2 = requests.post(url, json=data2, headers=headers)