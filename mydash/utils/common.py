import re
import urllib


def clean_name(s):
    return ''.join(s.strip().split())


def clean_text(s):
    return (re.split(r'\(|（', s)[0]).strip()


def build_url(base_url, query_dict):
    query = urllib.parse.urlencode(query_dict)
    return f'{base_url}?{query}'