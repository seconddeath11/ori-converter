# Конвертер данных

Представленные скрипты конвертируют данные об изображениях в различные форматы.

На данный момент поддерживаются следующие форматы:

- int (Internal)
- int_csv (InternalCSV)
- pascal_voc (PascalVOC)

## Использование
1. Необходимо создать образ с помощью docker:

```
$ docker build -t image-name /path/to/folder
```
2. Затем запустить скрипт создания контейнера с необходимыми аргументами:

```
$ bash start.sh --in-dir /path/to/data --out-dir /path/to/dir --in-format "int_csv" --out-format "pascal_voc" -i image-name
```

Подробнее про аргументы можно прочитать, используя команду:

```
$ bash start.sh --help
```
