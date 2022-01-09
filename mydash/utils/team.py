TEAM_TO_ALIASES = {
    'JFAアカデミー福島': ['JFAアカデミー福島U18', 'JFAアカデミー福島U-18'],
    '三菱養和ユース': ['三菱養和SCユース'],
    '名古屋U18': ['名古屋U-18'],
    '四日市中央工高': ['四日市中央工業高'],
    '国士舘大': ['国士舘大'],
    '大宮U18': ['大宮ユース', '大宮U-18'],
    '山梨学院高': ['山梨学院大学附属高', '山梨学院大附属高'],
    '川崎FU-18': ['川崎フロンターレU-18'],
    '慶應義塾大': ['慶應義塾大学'],
    '栃木ユース': ['栃木SCU-18	'],
    '流通経済大柏高': ['流通経済大学付属柏高'],
    '湘南U-18': ['湘南ユース'],
}
ALIAS_TO_TEAM = dict()
for team, aliases in TEAM_TO_ALIASES.items():
    for alias in aliases:
        ALIAS_TO_TEAM[alias] = team


def canonicalize_team(team_name):
    return ALIAS_TO_TEAM.get(team_name, team_name)
