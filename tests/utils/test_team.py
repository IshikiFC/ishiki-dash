from mydash.utils.team import canonicalize_team


def test_canonicalize_team():
    assert canonicalize_team('湘南ユース') == '湘南U-18'
    assert canonicalize_team('湘南U-18') == '湘南U-18'
    assert canonicalize_team('ランダム') == 'ランダム'
