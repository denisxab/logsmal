name_bin_file = "logsmal.bin"
proj_name = "logsmal"

# Генерировать документацию
auto_doc:
	sphinx-autobuild -b html ./docs/source ./docs/build/html

# Создать файл зависимостей для Read The Docs
req_doc:
	poetry export -f requirements.txt --output ./docs/requirements.txt --dev --without-hashes;

# Скомпилировать проект
compile:
	python -m nuitka --follow-imports $(proj_name)/log_file.py -o $(name_bin_file)

debug:
	python -m nuitka --follow-imports $(proj_name)/log_file.py -o $(name_bin_file) --remove-output

init:
	pip install poetry && poetry install && mkdir docs && sphinx-quickstart -p "logsmal" -a "Denis Kustov <denis-kustov@rambler.ru>" -v "0.0.2" -l "ru"  -r "0.0.2" --sep

