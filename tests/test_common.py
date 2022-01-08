from mydash.utils import clean_name, clean_text, build_url


def test_clean_name():
    assert clean_name('  ニャン　太郎 ') == 'ニャン太郎'


def test_clean_text():
    assert clean_text('  吾輩は猫である（だろうか？） ') == '吾輩は猫である'


def test_build_url():
    url = 'https://google.com'
    query = {
        'foo': 1,
        'bar': 2
    }
    assert build_url(url, query) == 'https://google.com?foo=1&bar=2'
