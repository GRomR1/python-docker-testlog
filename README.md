# python-docker-testlog

Приложение для запуска тестов парсинга и отправки логов в Graylog из простого типичного приложения на Python с помощью fluentd

# Running

Запустить все сервисы локально
```
docker-compose up --build fluentd app logrotate
```

# Описание 

## локальная инсталляция, через docker-compose

Система состоит из трех сервисов (см. [docker-compose.yaml](./docker-compose.yaml)):
- **app** - непосредственно приложение
- **fluentd** - обработчик, сохранение в файл и отправка на сервер graylog логов приложения
- **logrotate** - ротация сохраненных ранее файлов-логов

## app

Приложение app использует модуль [`logging`](https://docs.python.org/3/howto/logging.html) для работы с логами. Все логи как это обычно принято отправляются в stdout/stderr. 

Требуется обязательно изменить форматирование строки лога. Поле времени должно содержать миллисекунды. Другие поля опциональны, но рекомендуется придерживаться данной структуры (т.к. под нее написан парсер): 
```python
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03dZ - %(name)s - %(levelname)s - %(message)s',
                    datefmt="%Y-%m-%dT%H:%M:%S"
                    )
```

Таким образом строка логов будет следующей (например):
```
2021-06-23T15:04:59.128Z - __main__ - DEBUG - Time is 2021-06-23 18:04:59.128938
2021-06-23T15:04:59.129Z - __main__ - DEBUG - Time is 2021-06-23 18:04:59.129056. With multiline (first):
new line (second)
another line (third)
```

Многострочные логи также поддерживаются.

Контейнер с приложением запускается через `docker-compose` с опцией драйвера логов [`fluentd`](https://docs.docker.com/config/containers/logging/fluentd/). По этой причине команда `docker logs` не будет возвращать результаты.
```
logging:
    driver: "fluentd"
    options:
    fluentd-address: localhost:24224
    tag: docker.app
    fluentd-async-connect: "true"
```
Таким образом докер будет отправлять все логи приложения на `localhost:24224`, этот порт слушает сервис **fluentd**.

## fluentd

Сервис [`fluentd`](https://docs.fluentd.org/) также запускается в контейнере рядом с приложением, и в него прокидываются настройки [fluent.conf](fluentd/fluent.conf) и локальная папка `./logs`, которая будет использоваться для долгострочного хранения логов приложения **app**.

Сервис `fluentd`  настроен таким образом, что сообщение поступающее на вход (`0.0.0.0:24224`) проходит несколько стадий:
1. `@CONCAT` - этап объединения мультистрочных логов, для этого используется модуль `concat` и регулярное выражение `multiline_start_regexp /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z.+$/` (это начало строки - timestamp).
2. `@PARSER` - этап обработки сообщения, разделения сложной строки лога на логические поля. Для этого была написана следующая регулярка - `expression /^(?<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z) - (?<name>[\w\.\_\-]+) - (?<log_level>\w+) - (?<message>[\s\S]*)/`.
3. `@OUTPUT` - заключительный этап - отправка в stdout, в graylog (через gelf udp, каждые 5 сек), в файл (каждые 10 сек).

Так как обработанное сообщение отправляется сервисом `fluentd` в stdout, то весь поток логов приложения **app** может быть прочитан через команду `docker logs fluentd`

Сервис `fluentd` не умеет делать ротацию создаваемых им файлов, поэтому необходим следующий сервис - **logrotate**.

## logrotate

Для защиты от переполнения сохраняемых на диске логов приложения используется сервис [`logrotate`](https://github.com/blacklabelops/logrotate). Его настройки производятся через переменные окружения, а именно:
```
LOGS_DIRECTORIES: /var/log/fluentd
LOGROTATE_PARAMETERS: vf # commandline parameters: v: Verbose, f: Force
LOGROTATE_COMPRESSION: compress # default: nocompress
LOGROTATE_INTERVAL: daily
LOGROTATE_COPIES: 14
LOGROTATE_SIZE: 100M
LOGROTATE_STATUSFILE: /logrotate/logrotate.status # remember when files have been rotated when using time intervals
LOGROTATE_DATEFORMAT: ".%Y-%m-%d"
```

Таким образом, будут сохранено не больше 14 копий файлов: ротация логов каждый день, максимальный объем одного лог-файла 100М.

## облачная инсталляция, через kubernetes

В разработке...

# Замечания

- Для определения хоста - места, откуда отсылаются логи можно использовать поле `tag` в опциях сервиса в `docker-compose.yaml` (`service.app.logging.options.tag`), это же поле потом можно прокинуть в `fluetnd` через `record_transformer`, а именно `source_tag ${tag}`.
- 



---


Deploy in K8S

```
docker-compose build

docker tag python-docker-testlog_app:latest registry.example.com/python-testlog

docker push registry.example.com/python-testlog

k apply -f python-testlog.k8s.yaml

k -n default delete po -l name=python-testlog
```

Get logs
```
kl -n default -l name=python-testlog
```
