# Routers

Comme nous l’avons vu, nous pouvons ajouter beaucoup de endpoints dans notre application en fonction de nos besoins, cependant dans des cas réels, notre code peut atteindre la centaines de lignes, dans le meilleur des cas à des millions.

Les tags peuvent nous aider à ajouter de la sémantique pour faciliter la compréhension de l’utilisateur, mais pas des développeur qui travailleront avec vous dans le développement de l’application.

Pour augmenter la lisibilité du code et faire en sorte que tout le monde puisse travailler ensemble, FastApi à ce qu’on appelle des routers.

Les routers permettent de séparer le code en plusieurs fichiers

![](Aspose.Words.bc22e1cd-4633-451e-972d-310fe5c427a3.001.png)

[main.py](router_1/main.py)

```python
from fastapi import FastAPI
from router import blog_get


app = FastAPI()
app.include_router(blog_get.router)

@app.get('/hello')
def index():
  return {'message': 'Hello world!'}
```
Dans la partie main, on peut appeler le fichier blog_get qui contient l’essentiel de la logique du code et l’ajouter grâce à deux ligne from router import blog_get et app.include_router(blog_get.router).

Exemple router :
```python
from fastapi import APIRouter, Response, status
from enum import Enum
from typing import Optional

router = APIRouter(
    prefix='/blog',
    tags=['blog']
)

# @app.get('/all')
# def get_all_blogs():
#   return {'message': 'All blogs provided'}

@router.get(
  '/all',
  summary='Retrieve all blogs',
  description='This api call simulates fetching all blogs',
  response_description="The list of available blogs"
  )
def get_blogs(page = 1, page_size: Optional[int] = None):
  return {'message': f'All {page_size} blogs on page {page}'}

@router.get('/{id}/comments/{comment_id}', tags=['comment'])
def get_comment(id: int, comment_id: int, valid: bool = True, username: Optional[str] = None):
  """
    Simulates retrieving a comment of a blog
    - **id** mandatory path parameter
    - **comment_id** mandatory path parameter
    - **bool** optional query parameter
    - **username** optional query parameter
    """
  return {'message': f'blog_id {id}, comment_id {comment_id}, valid {valid}, username {username}'}

class BlogType(str, Enum):
  short = 'short'
  story = 'story'
  howto = 'howto'

@router.get('/type/{type}')
def get_blog_type(type: BlogType):
  return {'message': f'Blog type {type}'}

@router.get('/{id}', status_code=status.HTTP_200_OK)
def get_blog(id: int, response: Response):
  if id > 5:
    response.status_code = status.HTTP_404_NOT_FOUND
    return {'error': f'Blog {id} not found'}
  else : 
    response.status_code = status.HTTP_200_OK
    return {'message': f'Blog with id {id}'}
```

Cette partie du code est celle que nous avons développé précédemment.

```python
router = APIRouter(
    prefix='/blog',
    tags=['blog']
)
```

permet de connecter cette partie à main (app.include_router(blog_get.router) dans main.py). Le tags quant à lui tag de la même manière les préfixes.

[blog_get.py](router_1/router/blog_get.py)

```python
@router.get(
  '/all',
  summary='Retrieve all blogs',
  description='This api call simulates fetching all blogs',
  response_description="The list of available blogs"
  )
def get_blogs(page = 1, page_size: Optional[int] = None):
  return {'message': f'All {page_size} blogs on page {page}'}

@router.get('/{id}/comments/{comment_id}', tags=['comment'])
def get_comment(id: int, comment_id: int, valid: bool = True, username: Optional[str] = None):
  """
    Simulates retrieving a comment of a blog
    - **id** mandatory path parameter
    - **comment_id** mandatory path parameter
    - **bool** optional query parameter
    - **username** optional query parameter
    """
  return {'message': f'blog_id {id}, comment_id {comment_id}, valid {valid}, username {username}'}

class BlogType(str, Enum):
  short = 'short'
  story = 'story'
  howto = 'howto'

@router.get('/type/{type}')
def get_blog_type(type: BlogType):
  return {'message': f'Blog type {type}'}

@router.get('/{id}', status_code=status.HTTP_200_OK)
def get_blog(id: int, response: Response):
  if id > 5:
    response.status_code = status.HTTP_404_NOT_FOUND
    return {'error': f'Blog {id} not found'}
  else : 
    response.status_code = status.HTTP_200_OK
    return {'message': f'Blog with id {id}'}
```

Le prefixe indique que tous les endpoints utilisant la syntaxe router.get (ou autre verbe http) commencera le prefix (ici blog) de manière implicite.

## Second router

Pour la prochaine section qui sera sur le verbe http post nous allons en amont préparer un second router.

[main.py](router_1/main.py)

```python
from fastapi import FastAPI
from router import blog_get
from router import blog_post


app = FastAPI()
app.include_router(blog_get.router)
app.include_router(blog_post.router)

@app.get('/hello')
def index():
  return {'message': 'Hello world!'}
```

La partie main.py contient ele nouvel import from router import blog_post, pour l’inclure il suffit d’utiliser la même syntaxe que vu précédemment.

Le nouveau fichier à la même syntaxe que le premier router quasiment : 

[blog_post.py](router_2/router/blog_post.py)

```python
from fastapi import APIRouter

router = APIRouter(
    prefix='/blog',
    tags=['blog']
)

@router.post('/new')
def create_blog():
  pass
```