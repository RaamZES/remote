import requests

response = requests.get('http://10.123.120.47:5000/get_rooms')
dict = response.json()
print(dict)