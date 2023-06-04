from sys import argv, stderr
from os import makedirs, path
import json as _json
import requests as _requests


def readjson(fn):
    with open(fn, encoding='utf8') as f:
        return _json.load(f)


def dumpjson(fn, json, pretty_print=False):
    with open(fn, 'w', encoding='utf8') as f:
        return _json.dump(json, f, indent=(4 if pretty_print else None), ensure_ascii=(not pretty_print))


def downloadjson(url):
    with _requests.get(url) as mf:
        #return mf.json()
        return _json.loads(mf.content.decode('utf8'))


def downloadfile(url, fn):
    with _requests.get(url) as mf:
        with open(fn, 'wb') as f:
            f.write(mf.content)


def parse_resource_location(s):
    i = s.find(':')
    if i < 0:
        return ('minecraft', s)
    return (s[:i], s[i+1:])


def log(*args, **kwargs):
    pass
