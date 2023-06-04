from json_util import *
from dateutil.parser import isoparse
import subprocess


MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
ASSETS = "https://resources.download.minecraft.net"


TIME_SINCE_BUNDLER = isoparse('2021-09-29T16:00:00+00:00')
# time = 2021-09-29T16:27:05+00:00


def findversion(versions, vid):
    for j in versions:
        if j.get('id') == vid:
            return j.get('url')
    return None


def dlserver(json_url, dirname=None, ref=None):
    log(f'Downloading server from {json_url}')
    json = downloadjson(json_url)
    server = json.get('downloads', {}).get('server', {}).get('url')
    if not server:
        log(f'ERROR: couldn\'t get server jar from {json_url}')
        return None
    fn = f'server-{dirname}.jar' if dirname else 'server.jar'
    downloadfile(server, fn)
    # Assets Index
    if ref:
        assetIndex = json.get('assetIndex', {}).get('url')
        if assetIndex:
            ref(downloadjson(assetIndex))
    # Date
    releaseTime = isoparse(json.get('releaseTime', '9999-99-99T23:59:59+00:00'))
    return_args = ["java"]
    if releaseTime > TIME_SINCE_BUNDLER:
        return_args += ["-DbundlerMainClass=net.minecraft.data.Main", "-jar", fn]
    else:
        return_args += ["-cp", fn, "net.minecraft.data.Main"]
    return_args += ['--reports', '--output', f'generated-{dirname}' if dirname else 'generated']
    log(f'Args: {return_args}')
    return return_args


def exec_command(l):
    p = subprocess.run(l, capture_output=True, text=True)
    log(p.stdout)
    log(p.stderr, file=stderr)


def read_itemlist(dirname):
    j = readjson(f'generated-{dirname}/reports/registries.json')
    return sorted(list(j.get('minecraft:item').get('entries')))


def diff_lists(old, new):
    for i in new:
        if i not in old:
            yield i


def getitemsmeta(items, translations):
    m = {}
    for item in items:
        rl = parse_resource_location(item)
        tr = translations.get(f'item.{rl[0]}.{rl[1]}')
        if not tr:
            tr = translations.get(f'block.{rl[0]}.{rl[1]}')
        if not tr:
            if rl[0] == 'minecraft' and rl[1].endswith('_smithing_template'):
                tr = '\u953b\u9020\u6a21\u677f'
        if not tr:
            log(f'Failed to get translation for {item}')
            m[f'{rl[0]}:{rl[1]}'] = '???'
            continue
        m[f'{rl[0]}:{rl[1]}'] = {'name': tr, 'name_length': len(tr)}
    return m


def main(version_from, version_to, output=None):
    if not output:
        output = 'output-repo'
    if not path.exists(output):
        makedirs(output)
    log(f'Diffing from {version_from} to {version_to}')
    versions = downloadjson(MANIFEST).get('versions', [])
    urlfrom = findversion(versions, version_from)
    urlto = findversion(versions, version_to)
    if not urlfrom:
        log(f'ERROR: Version id {version_from} not found')
        return
    if not urlto:
        log(f'ERROR: Version id {version_to} not found')
        return
    assetIndex = []
    argsfrom = dlserver(urlfrom, version_from)
    argsto = dlserver(urlto, version_to, lambda x: assetIndex.append(x))
    if not (argsfrom and argsto):
        return
    exec_command(argsfrom)
    exec_command(argsto)
    log('Generating diff list')
    new_items = diff_lists(read_itemlist(version_from), read_itemlist(version_to))
    log('Fetching translations')
    if not assetIndex:
        log('Warning: assetIndex missing')
        assetIndex = downloadjson('https://piston-meta.mojang.com/v1/packages/3d9e16c18f36a8c565641583e48af3cb33315dfc/5.json')
    else:
        assetIndex = assetIndex.pop()
    thehash = assetIndex.get('objects', {}).get('minecraft/lang/zh_cn.json', {}).get('hash')
    translations = downloadjson(f'{ASSETS}/{thehash[:2]}/{thehash}')
    
    log('Calculating meta')
    #dumpjson(output + '/diff.json', new_items, True)
    dumpjson(output + '/meta.json', getitemsmeta(new_items, translations), True)


if __name__ == '__main__':
    vf = None
    vt = None
    output = None
    if len(argv) > 1:
        vf = argv[1]
    if len(argv) > 2:
        vt = argv[2]
    if len(argv) > 3:
        output = argv[3]
    
    if vf and vt:
        log = print
        if len(argv) > 4:
            MANIFEST = argv[4]
            log(f'WARNING: Changing manifest url into {MANIFEST}')
        if len(argv) > 5:
            ASSETS = argv[5]
            log(f'WARNING: Changing assets url into {ASSETS}')
        main(vf, vt)
    else:
        print(f'ERROR: Versions not defined. version_from={vf} version_to={vt}', file=stderr)
        exit(-1)
