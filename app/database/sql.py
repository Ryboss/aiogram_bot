from sqlalchemy.sql import text
from sqlalchemy.sql.elements import TextClause


def GET_USERS() -> TextClause:
    """
    Получение польщователей
    """

    return text("""SELECT username, user_id, phone FROM "users" """)


def GET_COMPANIES() -> TextClause:
    """
    Получение списка компаний
    """

    return text("""SELECT company_name, adress, company_phone, email FROM "companies" """)
