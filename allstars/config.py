from os import environ

config_defaults = {
    "ALLSTARS_FOLDER": "/tmp/allstars",
    "ALLSTARS_SQLA_CONN": "mysql://",
    "ALLSTARS_PROJECT": "jaffleshop",
}

for k in config_defaults.keys():
    if k in environ and environ.get(k):
        globals()[k] = environ.get(k)
    else:
        globals()[k] = config_defaults[k]
