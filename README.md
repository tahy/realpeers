# realpeers

Установка пакета: pip install -e .

---

Запуск эмулятора анкора: 

ID анкора и путь к файлу с декавейвовскими логами задается либо через 
переменные окружения
или через параметры коммандной строки (параметры имеют приоритет)

> export CLE_ANCHOR_ID=1
>
> export CLE_ANCHOR_SOURCE_FILE=/path/to/source.log
> 
> cle-anchor
>
> или через параметры 
> 
> cle-anchor --anchor-id=2 --source-file=/path/to/source.log 
>
> cle-anchor -a 2 -s /path/to/source.log 

CLE_ANCHOR_ID нужно устанавливать всегда, 

source.log по умолчанию ищется 
в workdir по имени source.log

стандартные способы вспомнить: cle-anchor -h или cle-anchor --help

---

Запуск поллера:

путь к конфигу аналогично, либо через переменные окружения, либо через параметры

> export CLE_POLLER_CONFIG=/path/to/poller-config.yml
>
>cle-poller
>
>или
>
>cle-poller --config=/path/to/poller-config.yml
>
>или
>
>cle-poller -c /path/to/poller-config.yml

стандартные способы вспомнить: cle-poller -h или cle-poller --help

по умолчанию конфиг ищется в workdir по имени poller-config.yml