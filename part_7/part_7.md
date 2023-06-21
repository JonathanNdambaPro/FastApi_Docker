# Concept

## Error handling

La gestion des erreurs permet au développeur de lever une exception si certaines conditions ne sont pas respectées pour stopper le code de continuer avec des valeurs fausses. FastApi permet de gérer des erreurs spécifiques aux Apis comme nous allons le voir.

![](Aspose.Words.91a941bd-09cf-4a95-98dd-6b5b322cb1a3.001.jpeg)

[db_article.py](error_handling/db/db_article.py)

```python
from exceptions import StoryException
from sqlalchemy.orm.session import Session
from db.models import DbArticle
from schemas import ArticleBase
from fastapi import HTTPException, status


def create_article(db: Session, request: ArticleBase):
  if request.content.startswith('Once upon a time'):
    raise StoryException('No stories please')
  new_article = DbArticle(
    title = request.title,
    content = request.content,
    published = request.published,
    user_id = request.creator_id
  )
  db.add(new_article)
  db.commit()
  db.refresh(new_article)
  return new_article

def get_article(db: Session, id: int):
  article = db.query(DbArticle).filter(DbArticle.id == id).first()
  if not article:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Article with id {id} not found')
  return article
```

Dans cet exemple nous avons modifier la fonction get_article, on peut voir que cette fonction n’est pas

il y a plusieurs élément à approfondir :

- HTTPException qui est un type d’exception propre à fastapi
- status.HTTP_404_NOT_FOUND : qui sont les status propres à fastapi, on pourrait utiliser diretement mais taper status. + tab pour avoir l’auto-implémentation nous permettra de ne pas à se souvenir de tous les status et d’en sélectionner un.
- detail permet de renvoyer le message que nous voulons au développeur, en effet en tant que codeur nous pourrions facilement le débugger avec les logs de notre application, mais l’utilisateur n’as pas accès à ces logs et ne comprendra pas l’erreur.

On peut faire la même chose pour db_user.py

[db_user.py](error_handling/db/db_user.py)

```python
from db.hash import Hash
from sqlalchemy.orm.session import Session
from schemas import UserBase
from db.models import DbUser
from fastapi import HTTPException, status


def create_user(db: Session, request: UserBase):
  new_user = DbUser(
    username = request.username,
    email = request.email,
    password = Hash.bcrypt(request.password)
  )
  db.add(new_user)
  db.commit()
  db.refresh(new_user)
  return new_user

def get_all_users(db: Session):
  return db.query(DbUser).all()

def get_user(db: Session, id: int):
  user = db.query(DbUser).filter(DbUser.id == id).first()
  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  return user

def update_user(db: Session, id: int, request: UserBase):
  user = db.query(DbUser).filter(DbUser.id == id)
  if not user.first():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  user.update({
    DbUser.username: request.username,
    DbUser.email: request.email,
    DbUser.password: Hash.bcrypt(request.password)
  })
  db.commit()
  return 'ok'

def delete_user(db: Session, id: int):
  user = db.query(DbUser).filter(DbUser.id == id).first()
  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  db.delete(user)
  db.commit()
  return 'ok'
```

Nous pouvons si besoin, nous pouvons implémenter nos propre exception. 

[exception.py](error_handling/exceptions.py)

```python
class StoryException(Exception):
  def __init__(self, name: str):
    self.name = name
```

C’est la manière standard de créer une exception il faut maintenant l’appeler dans le code pour qu’elle se lève quand nous en avons besoin.

[db_artcles.py](error_handling/db/db_article.py)

```python
from exceptions import StoryException
from sqlalchemy.orm.session import Session
from db.models import DbArticle
from schemas import ArticleBase
from fastapi import HTTPException, status


def create_article(db: Session, request: ArticleBase):
  if request.content.startswith('Once upon a time'):
    raise StoryException('No stories please')
  new_article = DbArticle(
    title = request.title,
    content = request.content,
    published = request.published,
    user_id = request.creator_id
  )
  db.add(new_article)
  db.commit()
  db.refresh(new_article)
  return new_article

def get_article(db: Session, id: int):
  article = db.query(DbArticle).filter(DbArticle.id == id).first()
  if not article:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Article with id {id} not found')
  return article
```

Nous avons placé notre exception, cependant comme ce n’est pas une exception inhérente à FastApi, l’erreur ne seras pas explicite (500 internal error) nous devons connecter l’erreur à notre application pour que l’utilisateur ai une erreur explicite.

[main.py](error_handling/main.py)

```python
from typing import Optional
from fastapi import FastAPI, Request
from router import blog_get
from router import blog_post
from router import user
from router import article
from db.database import engine
from db import models
from exceptions import StoryException
from fastapi.responses import JSONResponse


app = FastAPI()
app.include_router(user.router)
app.include_router(article.router)
app.include_router(blog_get.router)
app.include_router(blog_post.router)

@app.get('/hello')
def index():
  return {'message': 'Hello world!'}

@app.exception_handler(StoryException)
def story_exception_handler(request: Request, exc: StoryException):
  return JSONResponse(
    status_code=418,
    content={'detail': exc.name}
  )

# @app.exception_handler(HTTPException)
# def custom_handler(request: Request, exc: StoryException):
#   return PlainTextResponse(str(exc), status_code=400)

models.Base.metadata.create_all(engine)
```

- @app.exception_handler(StoryException) permet de connecter la nouvelle exception à notre application
- story_exception_handler est la fonction qui permet d’indiquer à notre application comment se compoerter quand cette exception se lève.

Point d’attention : le décorateur est la fonction fonctionne de concert.

## Custom Response

FastAPi prend en charge de mettre sous le format json les données native de python (dictionnaire, list, texte, etc.), cependant il peut arriver que le format que nous voulons soit différent du format classic json, dans ce cas il faut utiliser une custom response

[product.py](custom_response/router/product.py)

```python
from fastapi import APIRouter, Header, Cookie, Form
from fastapi.responses import Response, HTMLResponse, PlainTextResponse

router = APIRouter(
  prefix='/product',
  tags=['product']
)

products = ['watch', 'camera', 'phone']


@router.get('/all')
def get_all_products():
  # return products
  data = " ".join(products)
  return Response(content=data, media_type="text/plain")


@router.get('/{id}', responses={
  200: {
    "content": {
      "text/html": {
        "example": "<div>Product</div>"
      }
    },
    "description": "Returns the HTML for an object"
  },
  404: {
    "content": {
      "text/plain": {
        "example": "Product not available"
      }
    },
    "description": "A cleartext error message"
  }
})
def get_product(id: int):
  if id > len(products):
    out = "Product not available"
    return PlainTextResponse(status_code=404, content=out, media_type="text/plain")
  else:
    product = products[id]
    out = f"""
    <head>
      <style>
      .product {{
        width: 500px;
        height: 30px;
        border: 2px inset green;
        background-color: lightblue;
        text-align: center;
      }}
      </style>
    </head>
    <div class="product">{product}</div>
    """
    return HTMLResponse(content=out, media_type="text/html")
```

Le principal élément ici est ```Response(content=data, media_type="text/plain")```

- content est le contenu que nous voulons renvoyer à l’utilisateur, il n’y a pas d’auto-convertion ici donc il faut faire attention à prétréter la données pour quelle soit en texte (data = " ".join(products) dans notre exemple)
- media_type permet de choisir quel type de sortie, ici, nous indiquons que nous voulons un texte

les raisons de faire des customs response sont multiples :

- ajouter des paramètre : Headers, Cookies
- gérer le type de réponse
  - plain text
  - xml
  - html
  - fichiers
  - streaming
- Créer des logiques plus complexes (choisir le type de sortie en fonction e certaines conditions)
- Meilleure documentation dans la réponse

Regardons en détail la deuxième fonction :
```python
@router.get('/{id}', responses={
  200: {
    "content": {
      "text/html": {
        "example": "<div>Product</div>"
      }
    },
    "description": "Returns the HTML for an object"
  },
  404: {
    "content": {
      "text/plain": {
        "example": "Product not available"
      }
    },
    "description": "A cleartext error message"
  }
})
def get_product(id: int):
  if id > len(products):
    out = "Product not available"
    return PlainTextResponse(status_code=404, content=out, media_type="text/plain")
  else:
    product = products[id]
    out = f"""
    <head>
      <style>
      .product {{
        width: 500px;
        height: 30px;
        border: 2px inset green;
        background-color: lightblue;
        text-align: center;
      }}
      </style>
    </head>
    <div class="product">{product}</div>
    """
    return HTMLResponse(content=out, media_type="text/html")
```

il y a trois parties:

- ```PlainTextResponse``` permettra de renvoyer out sous forme de texte.
- out est composer de code html et css, vous n’avez pas besoins de comprendre tout en détail mais à la place de renvoyer un json, nous allons renvoyer une page web en réponse au client, pour se faire il faut absolument coupler out avec ```HTMLResponse``` de cette manière return ```HTMLResponse(content=out, media_type="text/html")```
- ```@router.get``` on à ajouter les l’argument response pour indiquer à l’utilisateur le type de réponse qu’il peut avoir (par défaut elle n’y sont pas toutes

## Headers

Les headers sont des information complémentaire transmise avec le json/response au client. Avec FastApi nous pouvons intégrer facilement un custom header.

[product.py](headers/router/product.py)

```python
from typing import Optional, List
from fastapi import APIRouter, Header, Cookie, Form
from fastapi.responses import Response, HTMLResponse, PlainTextResponse

router = APIRouter(
  prefix='/product',
  tags=['product']
)

products = ['watch', 'camera', 'phone']


@router.get('/all')
def get_all_products():
  # return products
  data = " ".join(products)
  return Response(content=data, media_type="text/plain")


@router.get('/withheader')
def get_products(
  response: Response,
  custom_header: Optional[List[str]] = Header(None)
  ):
  if custom_header:
    response.headers['custom_response_header'] = " and ".join(custom_header)
  return {
    'data': products,
    'custom_header': custom_header
  }


@router.get('/{id}', responses={
  200: {
    "content": {
      "text/html": {
        "example": "<div>Product</div>"
      }
    },
    "description": "Returns the HTML for an object"
  },
  404: {
    "content": {
      "text/plain": {
        "example": "Product not available"
      }
    },
    "description": "A cleartext error message"
  }
})
def get_product(id: int):
  if id > len(products):
    out = "Product not available"
    return PlainTextResponse(status_code=404, content=out, media_type="text/plain")
  else:
    product = products[id]
    out = f"""
    <head>
      <style>
      .product {{
        width: 500px;
        height: 30px;
        border: 2px inset green;
        background-color: lightblue;
        text-align: center;
      }}
      </style>
    </head>
    <div class="product">{product}</div>
    """
    return HTMLResponse(content=out, media_type="text/html")
```

on peut voir que ```custom_header: Optional[List[str]] = Header(None)``` permet de fournir le header en entré, pour ajouter le header dans la response on vérifie qu’il est pas nulle et nous utilisons response.```headers['custom_response_header'] = " and ".join(custom_header)```

pour voir les headers il faut faire dans le swagger un clic droit -> inspect -> networt puis exécuter la requête dans le swagger

## Cookies

les cookies servent à stocker un certain type d’informations du browser qui pourront être utilisé plus tard. (Dans le monde réel, ils sont utilisés pour "se souvenir" de votre activité ou de vos préférences sur le site sur une certaine période de temps.).

Dans FastApi, nous avons des méthode simple pour les utilisateurs. 

[product.py](cookies/router/product.py)

```python
from typing import Optional, List
from fastapi import APIRouter, Header, Cookie, Form
from fastapi.responses import Response, HTMLResponse, PlainTextResponse

router = APIRouter(
  prefix='/product',
  tags=['product']
)

products = ['watch', 'camera', 'phone']


@router.get('/all')
def get_all_products():
  # return products
  data = " ".join(products)
  response = Response(content=data, media_type="text/plain")
  response.set_cookie(key="test_cookie", value="test_cookie_value")
  return response


@router.get('/withheader')
def get_products(
  response: Response,
  custom_header: Optional[List[str]] = Header(None),
  test_cookie: Optional[str] = Cookie(None)
  ):
  if custom_header:
    response.headers['custom_response_header'] = " and ".join(custom_header)
  return {
    'data': products,
    'custom_header': custom_header,
    'my_cookie': test_cookie
  }


@router.get('/{id}', responses={
  200: {
    "content": {
      "text/html": {
        "example": "<div>Product</div>"
      }
    },
    "description": "Returns the HTML for an object"
  },
  404: {
    "content": {
      "text/plain": {
        "example": "Product not available"
      }
    },
    "description": "A cleartext error message"
  }
})
def get_product(id: int):
  if id > len(products):
    out = "Product not available"
    return PlainTextResponse(status_code=404, content=out, media_type="text/plain")
  else:
    product = products[id]
    out = f"""
    <head>
      <style>
      .product {{
        width: 500px;
        height: 30px;
        border: 2px inset green;
        background-color: lightblue;
        text-align: center;
      }}
      </style>
    </head>
    <div class="product">{product}</div>
    """
    return HTMLResponse(content=out, media_type="text/html")
```

Pour utiliser les cookies dans FastApi il suffit d’utiliser une méthode dans une instance de Response comme suit response.set_cookie(key="test_cookie", value="test_cookie_value")

installer ce détecteur de cookies dans la page [chrome](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)

en exécutant le product/all dans le swagger (endpoint qui correspond à get_all_products) on pourra voir grâce à l’extension que le cookies est bien utilisé.

Par la suite on peut utiliser le cookies dans une seconde fonction (endpoint /product/withheader) on pourra voir le cookies présent en sortie.
