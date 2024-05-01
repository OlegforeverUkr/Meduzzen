from enum import Enum

class InviteStatusEnum(Enum):
    INVITE = 'invite'
    REQUEST = 'request'
    DECLINED = 'declined'


class InviteTypeEnum(Enum):
    INVITE = 'invite'
    REQUEST = 'request'