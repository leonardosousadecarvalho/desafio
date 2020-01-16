# Desafio

Desenvolvimento de aplicação web com Flask

## Tecnologias utilizadas

- Python 3.8
- Flask
- flask_sqlalchemy
- flask_mysqldb
- Docker (mysql)
- Docker-compose (mysql)

## Como rodar o projeto

- Instalar as depenências com o comando `pip install -r requirements.txt`
- Subir banco de dados com o comando do `docker docker-compose up -d`
- Rodar a aplicação com o comando `python app.py`

## Como configurar o projeto

Caso deseja configurar outra base de dados altere as constantes descritas abaixo no arquivo app.py

``` sh
DB_USER = 'root'
DB_PASS =  'passwd' 
DB_HOST = '127.0.0.1'
DATABASE = 'desafio'
``` 
No arquivo mysql.dump está contido a estrutura da base
*Não é necessário fazer o dump pois o SQLAlchemy já cria as estruturas a partir do Model ao iniciar a applicação*