from mydash.utils.canonicalize import canonicalize_team, canonicalize_player


def test_canonicalize_team():
    assert canonicalize_team('湘南ユース') == '湘南U-18'
    assert canonicalize_team('湘南U-18') == '湘南U-18'
    assert canonicalize_team('ランダム') == 'ランダム'


def test_canonicalize_player():
    assert canonicalize_player('川崎裕大') == '川﨑裕大'
    assert canonicalize_player('ランダム') == 'ランダム'
