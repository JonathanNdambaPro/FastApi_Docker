# Dependencies

## Simple dependency

Les dépendances permettent de déclarer des fonctionnalité requise au bon fonctionnement d’une fonction/module/etc, par exemple dans le contexte de FastApi un certain endpoint qui dépendrait d’une sortie d’une fonction python.

Exemple :

- fonctionnalité partager sur plusieurs endpoints
- les connexions vers des bases de données ou autres ressources
- l’authentification
- réduire la duplication de code (DRY)

Une des dépendance que nous avons créé lors du projet était vers la base de données : 

[database.py](simple_dependency/db/database.py)

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./fastapi-practice.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
```

le fonction get_db est une dépendance qui sera utilisé dans article 

[article.py](simple_dependency/router/article.py)

```python
from typing import List
from schemas import ArticleBase, ArticleDisplay, UserBase
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_article
from auth.oauth2 import get_current_user, oauth2_scheme

router = APIRouter(
  prefix='/article',
  tags=['article']
)

# Create article
@router.post('/', response_model=ArticleDisplay)
def create_article(request: ArticleBase, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
  return db_article.create_article(db, request)

# Get specific article
@router.get('/{id}') #, response_model=ArticleDisplay)
def get_article(id: int, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
  return {
    'data': db_article.get_article(db, id),
    'current_user': current_user
  }
```

dans les endpoints create_article et get_article dépendent de get_db (db: Session = Depends(get_db)) s’il venait à avoir un problème au niveau de la base de données ce endpoint ne fonctionnerait pas, en plus de ça nous n’avons pas à dupliquer du code.

regardons un autre exemple : 

[dependencies.py]()

```python
from fastapi import APIRouter
from fastapi.param_functions import Depends
from fastapi.requests import Request

router = APIRouter(
  prefix='/dependencies',
  tags=['dependencies']
)

def convert_headers(request: Request, separator: str = '--'):
  out_headers = []
  for key, value in request.headers.items():
    out_headers.append(f"{key} {separator} {value}")
  return out_headers

@router.get('')
def get_items(separator: str = '--', headers = Depends(convert_headers)):
  return {
    'items': ['a', 'b', 'c'],
    'headers': headers
  }

@router.post('/new')
def create_item(headers = Depends(convert_headers)):
  return {
    'result': 'new item created',
    'headers': headers
  }
```

convert_headers est une fonction python qui convertira les headers avec une certaines logique.

point d’attention : request est disponible uniquement au niveau endpoint. Cependant, toute dépendance a automatiquement accès à tous les paramètres du endpoint au quelle elles eqt coupler, donc convert_headers à accès à request

## Class dependencies

les dépendances par classes sont quelque peu différentes, elles permettent 

[dependencies.py](class_dependancies/router/dependencies.py)

```python
from fastapi import APIRouter
from fastapi.param_functions import Depends
from fastapi.requests import Request

router = APIRouter(
  prefix='/dependencies',
  tags=['dependencies']
)

def convert_headers(request: Request, separator: str = '--'):
  out_headers = []
  for key, value in request.headers.items():
    out_headers.append(f"{key} {separator} {value}")
  return out_headers

@router.get('')
def get_items(separator: str = '--', headers = Depends(convert_headers)):
  return {
    'items': ['a', 'b', 'c'],
    'headers': headers
  }

@router.post('/new')
def create_item(headers = Depends(convert_headers)):
  return {
    'result': 'new item created',
    'headers': headers
  }


class Account:
  def __init__(self, name: str, email: str):
    self.name = name
    self.email = email

@router.post('/user')
def create_user(name: str, email: str, password: str, account: Account = Depends()):
  # account - perform whatever operations
  return {
    'name': account.name,
    'email': account.email
  }
```

Comme on le sait toutes dépendance à accès au dépendances avec laquelle elle est couplé, pour une classe qui sert de dépendance les paramètres vont servir à l’instancier.

## Multi level dependencies

C’est tout simplement une dépendance dans une dépendance très simple à implémenter dans FastApi

[dependencies.py](multi_level_dependencies/router/dependencies.py)

````python
from fastapi import APIRouter
from fastapi.param_functions import Depends
from fastapi.requests import Request

router = APIRouter(
  prefix='/dependencies',
  tags=['dependencies']
)

def convert_params(request: Request, separator: str):
  query = []
  for key, value in request.query_params.items():
    query.append(f"{key} {separator} {value}")
  return query

def convert_headers(request: Request, separator: str = '--', query = Depends(convert_params)):
  out_headers = []
  for key, value in request.headers.items():
    out_headers.append(f"{key} {separator} {value}")
  return {
    'headers': out_headers,
    'query': query
  }

@router.get('')
def get_items(test: str, separator: str = '--', headers = Depends(convert_headers)):
  return {
    'items': ['a', 'b', 'c'],
    'headers': headers
  }

@router.post('/new')
def create_item(headers = Depends(convert_headers)):
  return {
    'result': 'new item created',
    'headers': headers
  }


class Account:
  def __init__(self, name: str, email: str):
    self.name = name
    self.email = email

@router.post('/user')
def create_user(name: str, email: str, password: str, account: Account = Depends()):
  # account - perform whatever operations
  return {
    'name': account.name,
    'email': account.email
  }
````

- convert_headers est une dépendance des endpoints que nous avons déjà étudié
- convert_params est une dépendance dans de convert_headers qui est elle même une dépendance c’est de la que vient le “multi level”

## Global dependencies

Les dépendances globales s’appliquent à tous les endpoints d’un router ou de toute l’application.

[dependencies.py](global_dependencies/router/dependencies.py)

```python
from fastapi import APIRouter
from fastapi.param_functions import Depends
from fastapi.requests import Request
from custom_log import log

router = APIRouter(
  prefix='/dependencies',
  tags=['dependencies'],
  dependencies=[Depends(log)]
)

def convert_params(request: Request, separator: str):
  query = []
  for key, value in request.query_params.items():
    query.append(f"{key} {separator} {value}")
  return query

def convert_headers(request: Request, separator: str = '--', query = Depends(convert_params)):
  out_headers = []
  for key, value in request.headers.items():
    out_headers.append(f"{key} {separator} {value}")
  return {
    'headers': out_headers,
    'query': query
  }

@router.get('')
def get_items(test: str, separator: str = '--', headers = Depends(convert_headers)):
  return {
    'items': ['a', 'b', 'c'],
    'headers': headers
  }

@router.post('/new')
def create_item(headers = Depends(convert_headers)):
  return {
    'result': 'new item created',
    'headers': headers
  }


class Account:
  def __init__(self, name: str, email: str):
    self.name = name
    self.email = email

@router.post('/user')
def create_user(name: str, email: str, password: str, account: Account = Depends()):
  # account - perform whatever operations
  return {
    'name': account.name,
    'email': account.email
  }
```

une fois mis en place la dépendance est partout
