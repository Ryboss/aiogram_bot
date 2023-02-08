import openpyxl
import csv

from typing import Any, List, Set, TypeVar, Type, Union, Callable, Generator, Iterable, Tuple, Optional, Literal
from aiogram import types

from openpyxl.styles.borders import Border, Side, BORDER_THIN
from openpyxl.worksheet.dimensions import DimensionHolder
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from app.models.utils import GenericValidationError, ExcelModel


def sql_validation_error(loc: List[str], type: str, msg: Optional[str] = None) -> List[dict]:
    """
    Генерирует сообщение с ошибками SQL возвращаемое в стиле ошибок pydantic'а, когда ошибка идёт на уровне БД, например:
    UniqueViolationError, ForeignKeyViolationError по каким-то полям
    """

    return [GenericValidationError(loc=loc, msg=msg, type=type).dict(exclude_none=True)]


async def generate_excel(file_path: str, message: types.Message) -> str:
    """
    Генерация Excel по файлу CSV
    """

    wb = openpyxl.Workbook()
    ws = wb.active
    dh: DimensionHolder = ws.column_dimensions

    border = Side(border_style=BORDER_THIN, color="00000000")

    thin_border = Border(
        top=border,
        left=border,
        right=border,
        bottom=border,)

    with open(file_path) as f:
        reader = csv.reader(f, delimiter=",")
        for i, row in enumerate(reader):
            ws.append(row)
            for s, column in enumerate(row):
                ws.cell(row=i + 1, column=s + 1).border = thin_border
                dh[get_column_letter(s + 1)].width = len(column) + 5

    path_to_save = f"download_files/{message.from_user.id}/generate_excel_{message.message_id}.xlsx"
    wb.save(filename=path_to_save)

    return path_to_save


async def generate_json_to_excel(data: List[ExcelModel]) -> None:
    """
    Генерация Excel на основе json
    """

    wb = openpyxl.Workbook()
    ws = wb.active

    border = Side(border_style=BORDER_THIN, color="00000000")

    r_len = len(data)

    thin_border = Border(
        top=border,
        left=border,
        right=border,
        bottom=border,)

    for i, sheet in enumerate(data):
        title = sheet.title
        titles = sheet.titles
        data = sheet.data

        ws: Worksheet = wb.create_sheet(f"Report{i + 1}") if r_len > 1 and i > 0 else wb.active
        ws.title = title

        for i, t in enumerate(titles):
            if t:
                ws.cell(column=i + 1, row=2, value=t)
