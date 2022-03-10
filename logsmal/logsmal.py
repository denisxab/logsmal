import datetime
from enum import Enum
from typing import Final
from typing import Optional, Any, Callable, Union

from .independent.helpful import toBitSize
from .independent.log_file import LogFile
from .independent.zip_file import ZippFile, ZipCompression


class MetaLogger:
    """
    Мета данные логгера
    """
    #: Конец цвета
    reset_: Final[str] = "\x1b[0m"
    blue: Final[str] = "\x1b[96m"
    yellow: Final[str] = "\x1b[93m"
    read: Final[str] = "\x1b[91m"
    green: Final[str] = "\x1b[92m"
    #: Серый
    gray: Final[str] = "\x1b[90m"
    #: Неон
    neon: Final[str] = "\x1b[96m"


class CompressionLog(Enum):
    """
    Варианты действий при достижении лимита размера файла
    """
    #: Перезаписать файл (Удалить все и начать с 0)
    rewrite_file = lambda _path_file: CompressionLog._rewrite_file(_path_file)

    #: Сжать лог файл в архив, а после удалить лог файл
    zip_file = lambda _path_file: CompressionLog._zip_file(_path_file)

    @staticmethod
    def _rewrite_file(_path_file: str):
        _f = LogFile(_path_file)
        logger.system_info(f"{_path_file}:{_f.sizeFile()}", flag="DELETE")
        _f.deleteFile()

    @staticmethod
    def _zip_file(_path_file: str):
        ZippFile(f"{_path_file}.zip").writeFile(_path_file, compression=ZipCompression.ZIP_LZMA)
        LogFile(_path_file).deleteFile()
        logger.system_info(_path_file, flag="ZIP_AND_DELETE")


class loglevel:
    """
    Создание логгера
    """
    __slots__ = [
        "title_logger",
        "fileout",
        "int_level",
        "console_out",
        "color_flag",
        "color_title_logger",
        "max_size_file",
        "compression",
        "_cont_write_log_file",
        "template_file",
        "template_console",
    ]

    #: Через сколько записей в лог файл, проверять его размер.
    CONT_CHECK_SIZE_LOG_FILE = 10

    #: Значение для фильтрации работы логгера
    required_level: int = 10

    def __init__(
            self,
            title_logger: str,
            int_level: int = 10,
            fileout: Optional[str] = None,
            console_out: bool = True,
            color_flag: str = "",
            color_title_logger: str = "",
            max_size_file: Optional[Union[int, str]] = "10mb",
            compression: Optional[Union[CompressionLog, Callable]] = None,
            template_file: str = "[{title_logger}][{flag}]:{data}\n",
            template_console: str = "{color_title_logger}[{title_logger}]{reset}{color_flag}[{flag}]{reset}:{data}",
    ):
        """
        Создать логгер

        :param title_logger: Название логгера
        :param int_level: Цифровое значение логгера
        :param fileout: Куда записать данные
        :param console_out: Нужно ли выводить данные в ``stdout``
        :param max_size_file: Максимальный размер(байтах), файла после которого происходит ``compression``.

        Также можно указать:

        - kb - Например 10kb
        - mb - Например 1mb
        - None - Без ограничений

        :param compression: Что делать с файлам после достижение ``max_size_file``

        :param template_file: Доступные аргументы в :meth:`allowed_template_loglevel`
        :param template_console: Доступные аргументы в :meth:`allowed_template_loglevel`
        """
        self.title_logger: str = title_logger
        self.fileout: Optional[str] = fileout
        self.console_out: bool = console_out
        self.color_flag: str = color_flag
        self.color_title_logger: str = color_title_logger
        self.max_size_file: Optional[int] = toBitSize(max_size_file) if max_size_file else None
        self.compression: Callable = compression if compression else CompressionLog.rewrite_file
        self.int_level: int = int_level
        self.template_file: str = template_file
        self.template_console: str = template_console

        #: Сколько раз было записей в лог файл, до выполнения
        #: условия ``self._cont_write_log_file < CONT_CHECK_SIZE_LOG_FILE``
        self._cont_write_log_file = 0

    def __call__(self, data: str, flag: str = ""):
        """
        Вызвать логгер

        :param data:
        :param flag:
        """
        # Если уровень доступа выше или равен требуемому
        if self.int_level >= self.required_level:
            self._base(data, flag)

    def _base(self, data: Any, flag: str):
        """
        Логика работы логера

        :param data:
        :param flag:
        """

        if self.fileout:
            # Формируем сообщение в файл
            log_formatted = allowed_template_loglevel(self.template_file, data, flag, self)
            # Записываем в файл
            _f = LogFile(self.fileout)
            _f.appendFile(log_formatted)
            # Проверить размер файла, если размер больше ``self.max_size_file`` то произойдет ``self.compression``
            self._check_size_log_file(_f)

        if self.console_out:
            # Формируем сообщение в консоль
            log_formatted = allowed_template_loglevel(self.template_console, data, flag, self)
            print(log_formatted)

    def _check_size_log_file(self, _file: LogFile):
        """
        Для оптимизации, проверка размера файла происходит
        при достижении условия определенного количества записи в файл

        :param _file: Файл
        """
        if self._cont_write_log_file > self.CONT_CHECK_SIZE_LOG_FILE or self._cont_write_log_file == 0:
            self._check_compression_log_file(size_file=_file.sizeFile())
        self._cont_write_log_file += 1

    def _check_compression_log_file(self, size_file: int):
        """
        Проверить размер файла.
        Если он превышает ``self.max_size_file`` то  выполнять  ``self.compression``

        :param size_file: Размер файла в байтах
        """
        if self.max_size_file is not None:
            if size_file > self.max_size_file:
                self.compression(self.fileout)


class allowed_template_loglevel:
    """
    Доступные ключи для шаблона лог сообщения в файл

    :Пример передачи:

    ``{level}{flag}{data}\n``
    ``{color_loglevel}{level}{reset}{color_flag}{flag}{reset}``
    """

    def __new__(
            cls,
            _template: str,
            data,
            flag,
            root_loglevel: loglevel
    ) -> str:
        """

        :param _template:
        :param flag:
        :param data:
        :param title_logger: Название логера
        :param reset: Закрыть цвет
        :param color_title_logger:  Цвет заголовка логера
        :param color_flag: Цвет флага
        :param date_now:  Дата создания сообщения
        """

        return _template.format(
            title_logger=root_loglevel.title_logger,
            flag=flag,
            data=data,
            date_now=datetime.datetime.now(),
            reset=MetaLogger.reset_,
            color_title_logger=root_loglevel.color_title_logger,
            color_flag=root_loglevel.color_flag,
        )


class logger:
    """
    Стандартные логгеры
    """
    info = loglevel(
        "INFO",
        int_level=20,
        color_title_logger=MetaLogger.blue,
        color_flag=MetaLogger.yellow,
    )
    success = loglevel(
        "SUCCESS",
        int_level=25,
        color_title_logger=MetaLogger.green,
        color_flag=MetaLogger.gray,
    )
    error = loglevel(
        "ERROR",
        int_level=40,
        color_title_logger=MetaLogger.read,
        color_flag=MetaLogger.yellow,
    )

    test = loglevel(
        'TEST',
        template_console="{color_title_logger}[{title_logger}]{reset}{color_flag}[{flag}]{reset}:\n{data}",
        color_flag=MetaLogger.gray,
        color_title_logger=MetaLogger.yellow
    )

    warning = loglevel(
        "WARNING",
        int_level=30,
        color_flag=MetaLogger.read,
        color_title_logger=MetaLogger.yellow,
    )

    #: Логгер для системных задач
    system_info: Final[loglevel] = loglevel(
        "SYSTEM",
        int_level=40,
        color_title_logger=MetaLogger.gray,
        color_flag=MetaLogger.gray,
        console_out=True
    )
    #: Логгер для системных задач
    system_error: Final[loglevel] = loglevel(
        "SYSTEM",
        int_level=45,
        color_title_logger=MetaLogger.gray,
        color_flag=MetaLogger.read,
        console_out=True
    )
