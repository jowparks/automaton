Installing:

`docker build -t automaton .`

Docker configurations:
```
# Variables
OMBI_URL = http://192.168.88.3:3579
OMBI_KEY = <see api key in ombi>

# Paths
/mnt/user/appdata/automaton/automaton:/automaton
/mnt/user/appdata/automaton/db:/db

# Port
8888:8000
```
URLs available (POST):
```
http://192.168.88.3:8888/api/request/basic/
http://192.168.88.3:8888/api/notify/radarr/
http://192.168.88.3:8888/api/notify/sonarr/
```