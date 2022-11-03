from inspect import FrameInfo, stack
import jsonpickle
import datetime
import typing

# В UTF-8
jsonpickle.set_encoder_options('json', ensure_ascii=False)


class LogRowTraceWhere(typing.NamedTuple):
    """Где происошло событие"""
    # Файл
    filename: str
    # Функция
    func: str
    # Срока
    line: str


class LogRowTrace(typing.NamedTuple):
    """Подробные данные для строки лога"""
    # Где случился вызов лога (ПутьФайлу:Функция:строка).
    where: LogRowTraceWhere
    # Локальные переменные в момент создания лога.
    loacl: dict[str, typing.Any]


class LogRow(typing.NamedTuple):
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
    trace: LogRowTrace

    def _(title: str, flags: list[str], data: str, is_trace: bool = False, stack_back: int = 1) -> str:
        """
        stack_back: Сколько функций вверх, по умолчанию на одну
        """
        row = None
        if not is_trace:
            row = LogRow(
                date=datetime.datetime.now(),
                title=title, flags=flags, data=data, trace=None)
        else:
            where: FrameInfo = stack()[stack_back]
            row = LogRow(
                date=datetime.datetime.now(), title=title, flags=flags,
                data=data, trace=LogRowTrace(
                    where=LogRowTraceWhere(
                        filename=where.filename,
                        func=where.function, line=where.lineno
                    ),
                    loacl=where.frame.f_locals
                )
            )
        return f"{jsonpickle.encode(row, unpicklable=False)}\n"
