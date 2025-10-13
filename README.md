# Сбор данных по звонкам с платформы Twin


### Migration Database

```sh
alembic init migrations
docker-compose -f development-compose.yaml exec twin_call_statistic bash -c 'cd /usr/src/ && alembic revision --autogenerate -m "init"'
docker-compose -f development-compose.yaml exec twin_call_statistic bash -c 'cd /usr/src/ && alembic upgrade head'
docker-compose -f development-compose.yaml exec twin_call_statistic bash -c 'cd /usr/src/ && alembic downgrade -1'
```