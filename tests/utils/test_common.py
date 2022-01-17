from mydash.utils.common import clean_name, clean_text, build_url


def test_clean_name():
    assert clean_name('  ニャン　太郎 ') == 'ニャン太郎'


def test_clean_text():
    assert clean_text('  名古屋U-18（2018プロ契約） ') == '名古屋U-18'
    assert clean_text('Ｃ大阪Ｕ-18') == 'C大阪U-18'
    assert clean_text('山形ユース') == '山形ユース'


def test_build_url():
    url = 'https://google.com'
    query = {'foo': 1, 'bar': 2}
    assert build_url(url, query) == 'https://google.com?foo=1&bar=2'
