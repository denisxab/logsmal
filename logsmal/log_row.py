from inspect import FrameInfo, stack
import datetime
import typing
from pydantic import BaseModel


class LogRowTraceWhere(BaseModel):
    """Где происошло событие"""
    # Файл
    filename: str
    # Функция
    func: str
    # Срока
    line: str


class LogRowTrace(BaseModel):
    """Подробные данные для строки лога"""
    # Где случился вызов лога (ПутьФайлу:Функция:строка).
    where: LogRowTraceWhere
    # Локальные переменные в момент создания лога.
    loacl: dict[str, typing.Any]


class LogRow(BaseModel):
    """Строка лог"""
    # Дата лога
    date: str
    # Тип лога (хорошо,плохо,информативно,...)
    title: str
    # Флаги
    flags: list[str]
    # Лог сообщение
    data: str
    # Подробные данные, для отладки
    trace: LogRowTrace | None

    def _(title: str, flags: list[str], data: str, is_trace: bool = False, stack_back: int = 1) -> str:
        """
        stack_back: Сколько функций вверх, по умолчанию на одну
        """
        row = None
        if not is_trace:
            row = LogRow(
                date=str(datetime.datetime.now()),
                title=title, flags=[str(x) for x in flags], data=repr(data), trace=None)
        else:
            where: FrameInfo = stack()[stack_back]
            row = LogRow(
                date=str(datetime.datetime.now()), title=title, flags=[str(x) for x in flags],
                data=repr(data), trace=LogRowTrace(
                    where=LogRowTraceWhere(
                        filename=where.filename,
                        func=where.function, line=where.lineno
                    ),
                    loacl={k: repr(v) for k, v in where.frame.f_locals.items()}
                )
            )
        return f"{row.json(ensure_ascii=False)}\n"
