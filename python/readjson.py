import json

def get_config():
    configfile = open("config.json","r")
    data = json.load(configfile)
    return data

def getKey(Key):
    data = get_config()
    return data[Key]

print (getKey("name"))
print (getKey("age"))