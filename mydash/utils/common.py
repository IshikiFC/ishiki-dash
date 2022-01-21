import re
import urllib

import jaconv


def clean_name(s):
    return ''.join(s.strip().split())


def clean_text(s):
    s = jaconv.z2h(s, kana=False, ascii=True, digit=True)
    return (re.split(r'\(|（', s)[0]).strip()


def build_url(base_url, query_dict):
    query = urllib.parse.urlencode(query_dict)
    return f'{base_url}?{query}'


def reverse_list_map(list_map):
    ret = dict()
    for k, vs in list_map.items():
        for v in vs:
            ret[v] = k
    return ret
