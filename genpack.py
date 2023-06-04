from json_util import *
from base64 import b64decode


def trymkdirs(d):
    if not path.exists(d):
        makedirs(d)


def dumptag(ns, fn, l, output):
    dirname = f'{output}/data/{ns}/tags/items/update_120'
    trymkdirs(dirname)
    dumpjson(f'{dirname}/{fn}.json', {'replace':False,'values':l})


def invalidmeta(meta):
    for k in meta:
        if meta[k] == '???':
            return k
    return None


def main(_filein, output):
    meta = readjson(_filein)
    if (_invalid := invalidmeta(meta)):
        log(f'ERROR: Found invalid value at {_invalid}')
    
    trymkdirs(f'{output}/data/speedabc/tags/items/update_120')
    trymkdirs(f'{output}/data/hannumspeed/tags/items/update_120')
    
    log('Generating speedabc')
    speedabc = {}
    for c in (chr(i) for i in range(ord('a'), ord('z')+1)):
        speedabc[c] = []
        #dumpjson(f'{output}/data/speedabc/tags/items/{c}.json', {'replace':False,'values':[f'#speedabc:update_120/{c}']})
    for _id in meta:
        _id = parse_resource_location(_id)
        if not _id[1]:
            log(f'Error parsing id {_id}')
            return
        _id = _id[1]
        speedabc[_id[0]].append(_id)
    for k in speedabc:
        if speedabc[k]:
            dumptag('speedabc', k, speedabc[k], output)
            dumpjson(f'{output}/data/speedabc/tags/items/{k}.json', {'replace':False,'values':[f'#speedabc:update_120/{k}']})
    
    log('Generating hannumspeed')
    hannumspeed = {}
    for i in range(1, 11):
        hannumspeed[i] = []
    for _id in meta:
        ni = meta[_id].get('name_length')
        if not ni:
            log(f'WARNING: invalid length {ni} found at {_id}')
            continue
        hannumspeed[ni].append(_id)
    for k in hannumspeed:
        if hannumspeed[k]:
            dumptag('hannumspeed', f'len_{k}', hannumspeed[k], output)
            dumpjson(f'{output}/data/hannumspeed/tags/items/len_{k}.json', {'replace':False,'values':[f'#hannumspeed:update_120/len_{k}']})
    
    log('Writing pack.mcmeta and misc files')
    dumpjson(f'{output}/pack.mcmeta', {'pack':{'pack_format':12,'description':[{'translate':'dataPack.speedrun.alphabet.ext.120','bold':True,'color':'dark_green','fallback':"\u03b1\u03b2speedrun: Add 1.20 Exp. Support"},'\n',{'translate':'dataPack.speedrun.alphabet.ext.120.reqmod','color':'white','fallback': 'Requires \u03b1\u03b2speedrun mod for 1.20'}]}})
    with open(f'{output}/version.properties', 'w') as f:
        f.write('mc=1.20\ndate=2023-06-04')
    with open(f'{output}/license.txt', 'w') as f:
        f.write('Copyright (c) teddyxlandlee 2022-2023.\n\nThis data pack is licensed under CC BY-SA 4.0.\nSee https://creativecommons.org/licenses/by-sa/4.0/ for more info.\n')
    with open(f'{output}/pack.png', 'wb') as f:
        f.write(b64decode(b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAq0lEQVQ4y2NgoAco1WD6T7bmOnO+/yEqnP/pa/scAfH/IAzSDLIdRBNlEEjTFmG5//+nzQXTIM0gsbviqmA+XoPgmmW0//+PywQbAscgPlAcryEoBmDBIFcgG4LTAJhCZBqGYfwQTr7/WEMbZADMEJi/YXyY64gyABkjGwTzAlYDsLkCm0E4NcMMgIUFNu+A5PAaAAIgBTBDYAmKaM3IhsDiG5wagXyiNZMKANOS2s9rfvFXAAAAAElFTkSuQmCC'))
    log('Done!')


if __name__ == "__main__":
    filein = None
    output = None
    if len(argv) > 1:
        filein = argv[1]
    if len(argv) > 2:
        output = argv[2]
    if filein and output:
        log = print
        main(filein, output)
    else:
        print(f'Invalid arguments: in={filein} out={output}', file=stderr)
        exit(-1)
