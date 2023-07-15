from enum import StrEnum


class Views(StrEnum):
    HOME = 'notes:home'
    ADD_NOTE = 'notes:add'
    NOTE_LIST = 'notes:list'
    NOTE_DETAIL = 'notes:detail'
    DELETE_NOTE = 'notes:delete'
    EDIT_NOTE = 'notes:edit'
    SUCCESS = 'notes:success'
    LOGIN = 'users:login'
    LOGOUT = 'users:logout'
    SIGHNUP = 'users:signup'
