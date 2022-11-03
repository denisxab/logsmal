import pytest

from logsmal import loglevel, CompressionLog, logger, LogFile, ZippFile

file_name = "./test.log"


class TestCompressionLog:

    def setup(self):  # Выполнятся перед вызовом каждого метода
        ...

    @pytest.mark.parametrize(
        ('_loger', "_len"),
        [
            (loglevel('TEST',
                      fileout=file_name,
                      console_out=False,
                      max_size_file=30,
                      compression=CompressionLog.rewrite_file),
             92,
             ),
            (loglevel('TEST',
                      fileout=file_name,
                      console_out=False,
                      max_size_file=30,
                      compression=CompressionLog.zip_file),
             92,
             )
        ]
    )
    def test_compression(self, _loger, _len):
        """
        Проверка компрессии

        :param _loger:
        :param _len:
        """
        logger.test = _loger
        _f = LogFile(file_name)
        _f.deleteFile()
        for x in range(_len):
            logger.test(str(x))
        assert _f.readFile() == '[TEST][]:90\n[TEST][]:91\n'
        assert _f.sizeFile() == 24
        _f.deleteFile()
        ZippFile(f"{file_name}.zip").deleteFile()

    def test_int_log_level(self):
        """
        Проверка работы логера при разном уровни фильтрации
        """
        """
        Уровень доступа разрешен
        логгер должен выполняться
        """
        _f = LogFile(file_name)
        _f.deleteFile()
        logger.test = loglevel("TEST", fileout=file_name,
                               console_out=False, int_level=10)
        logger.test("ТЕСТ")
        assert _f.readFile() == '[TEST][]:ТЕСТ\n'
        _f.deleteFile()
        """
        Уровень доступа ЗАПРЕЩЕН
        логгер не должен выполняться
        """
        _f.createFileIfDoesntExist()
        loglevel.required_level = 20
        logger.test("ТЕСТ")
        assert _f.readFile() == ''

    def teardown(self):  # Выполнятся после **успешного** выполнения каждого теста
        _f = LogFile(file_name)
        _f.deleteFile()

    def test_форматирование_сообщения(self):
        ...

    def test_style(self):
        print()
        logger.debug("Привет вселенная", 'От землян')
        logger.info("Привет вселенная", 'От землян')
        logger.success("Привет вселенная", 'От землян')
        logger.warning("Привет вселенная", 'От землян')
        logger.error("Привет вселенная", 'От землян')
        logger.test("Привет вселенная", 'От землян')

