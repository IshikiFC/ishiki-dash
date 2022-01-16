from mydash.utils.categorize import categorize_team, TeamCategory


def test_canonicalize_team():
    assert categorize_team('富山第一高') == TeamCategory.HIGH
    assert categorize_team('神奈川大') == TeamCategory.UNIV
    assert categorize_team('湘南ユース') == TeamCategory.YOUTH
    assert categorize_team('星槎国際高湘南') == TeamCategory.HIGH
    assert categorize_team('ランダム') == TeamCategory.OTHER
