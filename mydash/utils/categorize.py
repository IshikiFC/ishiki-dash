from enum import Enum

from mydash.utils import reverse_list_map


class TeamCategory(Enum):
    HIGH = '高校'
    UNIV = '大学'
    YOUTH = 'ユース'
    OTHER = 'その他'


TEAM_CATEGORY_TO_SUFFIXES = {
    TeamCategory.HIGH: ['高校', '高', '学園', '中等教育学校'],
    TeamCategory.UNIV: ['大学', '大'],
    TeamCategory.YOUTH: ['ユース', 'U-18', 'U18']
}
SUFFIX_TO_TEAM_CATEGORY = reverse_list_map(TEAM_CATEGORY_TO_SUFFIXES)

TEAM_NAME_TO_CATEGORY = {
    'JFAアカデミー福島': TeamCategory.YOUTH,
    '星槎国際高湘南': TeamCategory.HIGH,
    '常葉大浜松': TeamCategory.UNIV,
    '東海大熊本': TeamCategory.UNIV,
    '北海道教育大学岩見沢校': TeamCategory.UNIV
}


def categorize_team(team_name) -> TeamCategory:
    for suffix, category in SUFFIX_TO_TEAM_CATEGORY.items():
        if team_name.endswith(suffix):
            return category
    if team_name in TEAM_NAME_TO_CATEGORY:
        return TEAM_NAME_TO_CATEGORY.get(team_name)
    return TeamCategory.OTHER
