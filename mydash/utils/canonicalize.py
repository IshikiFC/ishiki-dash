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
    '栃木ユース': ['栃木SCU-18'],
    '流通経済大柏高': ['流通経済大学付属柏高'],
    '湘南U-18': ['湘南ユース'],
}
ALIAS_TO_TEAM = dict()
for team, aliases in TEAM_TO_ALIASES.items():
    for alias in aliases:
        ALIAS_TO_TEAM[alias] = team

ALIAS_TO_PLAYER = {
    '川崎裕大': '川﨑裕大',
    '髙山和真': '高山和真',
    '藤崎将汰': '藤﨑将汰',
    '高橋壱晟': '髙橋壱晟',
    '高畑智也': '髙畑智也',
    '高橋大悟': '髙橋大悟',
    '大城螢': '大城蛍',
    '高尾瑠': '髙尾瑠',
    '黒崎隼人': '黒﨑隼人',
    '川崎修平': '川﨑修平',
    '吹ケ徳喜': '吹ヶ徳喜',
    '高橋利樹': '髙橋利樹',
    '石ケ森荘真': '石ヶ森荘真',
    '高窪健人': '髙窪健人',
    '髙瀬太聖': '高瀬太聖',
    'キムソンスン': '金成純',
    'オニエオゴチュクウプロミス': 'オニエオゴチュクウ',
    'ターレスプロコピオカストロデパウラ': 'ターレス',
    'オタボーケネス': 'オタボー'
}


def canonicalize_team(team_name):
    return ALIAS_TO_TEAM.get(team_name, team_name)


def canonicalize_player(player_name):
    return ALIAS_TO_PLAYER.get(player_name, player_name)
