from typing import Type, Tuple, Any, List, Dict, Optional, Union, Generator, Iterator
from datetime import date, datetime
from sqlalchemy.sql import text
from sqlalchemy.sql.elements import TextClause


def GET_USERS() -> TextClause:
    """
    Получение польщователей
    """

    return text("""SELECT id, user_id, phone FROM "usercreate" """)
