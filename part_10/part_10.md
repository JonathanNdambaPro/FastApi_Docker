# Task

## Testing

Dans FastApi les test sont très simples à effectuer, les tests et une des parties la plus importante dans le développement logiciel et aussi souvent la plus ignorée, cependant quand le projet devient trop grand, ne pas avoir mis de test, la maintenabilité du code décroit pour qu’à la fin le projet tout entier ne puisse plus évoluer ce qui conduit souvent à l’abandon de ce dernier.

Le coverage de test doit souvent être entre 80-100%, on utilise ```pytest test_main.py```

[test_main.py](test/test_main.py)

```python
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)

def test_get_all_blogs():
  response = client.get("/blog/all")
  assert response.status_code == 200

def test_auth_error():
  response = client.post("/token",
    data={"username": "", "password": ""}
  )
  access_token = response.json().get("access_token")
  assert access_token == None
  message = response.json().get("detail")[0].get("msg")
  assert message == "field required"

def test_auth_success():
  response = client.post("/token",
    data={"username": "cat", "password": "cat"}
  )
  access_token = response.json().get("access_token")
  assert access_token

def test_post_article():
  auth = client.post("/token",
    data={"username": "cat", "password": "cat"}
  )
  access_token = auth.json().get("access_token")

  assert access_token

  response = client.post(
    "/article/",
    json={
      "title": "Test article",
      "content": "Test content",
      "published": True,
      "creator_id": 1
    },
    headers= {
      "Authorization": "bearer " + access_token
    }
  )

  assert response.status_code == 200
  assert response.json().get("title") == "Test article"
```

- from fastapi.testclient import TestClient permet de simuler une app pour pouvoir la tester
- client = TestClient(app) permet de définir qu’elle application simuler (du coup la nôtre)

Regardons un exemple :
```python
def test_get_all_blogs():
    response = client.get("/blog/all") assert response.status_code == 200
```
Ici, nous tester le endpoint /blog/all, nous savons que le status code de sortie doit être de 200 si l’appel api est bien fonctionnel

L’idée générale est de tester le plus de scénario possible que nous pourrions imaginer et vérifier si les résultat obtenu sont ceux que nous expierions, si ce n’est pas le cas alors notre application ne fonctionne pas comme nous l’avions imaginé et nous devons revoir la logique de développement.

Une fois tous les scénario imaginé tester, il faut vérifier que nous ayons un bon coverage. pour vérifier le coverage il faudra installer pytest-cov et lancer la commande suivante :

```pytest --cov=router```

## Logging

Les logs sont les information issue de l’application pour avoir un détails sur tout ce qui s'est passé, c’est un excellent moyen de debugger l’application, car pour rappel le client ne verra que le status 500, ce qui n’est pas d’une grande aide s'il y a une problème de logique que nous n’avions pas vu en amont et que nous devons corriger.

[custom_log.py](logging/custom_log.py)

```python
def log(tag="", message=""):
  with open("log.txt", "w+") as log:
    log.write(f"{tag}: {message}\n")
```

Ici, on a un fichier qui va écrire tous les logs dans le fichier log.txt 

[product.py](logging/router/product.py)

```python
from typing import Optional, List
from fastapi import APIRouter, Header, Cookie, Form
from fastapi.responses import Response, HTMLResponse, PlainTextResponse
from custom_log import log

router = APIRouter(
  prefix='/product',
  tags=['product']
)

products = ['watch', 'camera', 'phone']

@router.post('/new')
def create_product(name: str = Form(...)):
  products.append(name)
  return products


@router.get('/all')
def get_all_products():
  log("MyAPI", "Call to get all products")
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

- from custom_log import log nous permet d’importer la fonction que nous venons de coder
- log("MyAPI", "Call to get all products") va enregistrer le log que nous avons créer et le rendre accessible par la lecture du fichier log.txt
