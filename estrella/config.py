from os import environ

config_defaults = {
    "ESTRELLA_FOLDER": "/tmp/allstars",
    "ESTRELLA_SQLA_CONN": "mysql://",
    "ESTRELLA_PROJECT": "jaffleshop",
}

for k in config_defaults.keys():
    if k in environ and environ.get(k):
        globals()[k] = environ.get(k)
    else:
        globals()[k] = config_defaults[k]
