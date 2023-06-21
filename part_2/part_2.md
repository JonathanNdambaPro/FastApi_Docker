# GET

Dans cette section, nous allons étudier la méthode get sous FastApi :²

- Path parameters
- Predifined values
- Query parameters

## Path parameters

Le path parameters (ou le endpoint) dans fastapi est le chemin qui est dans @app.get(“path/parameters”). Nous pouvons grâce à ce chemin récupérer des valeurs et les réutiliser dans la fonction.

[main.py](path_parameters/main.py)

Exemple :

```python
from fastapi import FastAPI


app = FastAPI()

@app.get('/hello')
def index():
  return {'message': 'Hello world!'}

@app.get('/blog/all')
def get_all_blogs():
  return {'message': 'All blogs provided'}

@app.get('/blog/{id}')
def get_blog(id: int):
  return {'message': f'Blog with id {id}'}
```


Ici id est récupéré et utilisé dans la fonction.

En plus de ça, fastapi utilise le typehint pour valider le type de notre variable, si ce n’est pas un entier (dans notre exemple) alors, il renverra une erreur
- <http://localhost:8000/blog/10>
- <http://localhost:8000/blog/10.5>

L’outil qui fait le check des type est pydantic, c’est une librairie très utilisée pour la validation des données.

## Predefined values

Imaginons que nous ayons un cas ou il y a uniquement un ensemble possible de valeur attendu par le endpoint sinon le code doit lever une erreur. Une des solutions est des solution est l’utilisation de Enum.

[main.py](predifined_values/main.py)

```python
from fastapi import FastAPI
from enum import Enum


app = FastAPI()

@app.get('/hello')
def index():
  return {'message': 'Hello world!'}

@app.get('/blog/all')
def get_all_blogs():
  return {'message': 'All blogs provided'}

class BlogType(str, Enum):
    short = 'short'
    story = 'story'
    howto = 'howto'

@app.get('/blog/type/{type}')
def get_blog_type(type: BlogType):
  return {'message': f'Blog type {type}'}

@app.get('/blog/{id}')
def get_blog(id: int):
  return {'message': f'Blog with id {id}'}
```

Ici, nous définissons une classe qui a un nombre limité de valeurs et doit avoir le type str

```python
class BlogType(str, Enum):
    short = 'short'
    story = 'story'
    howto = 'howto'
```

la fonction get_blog_type va prendre en entrée les valeurs de type BlogType (short, story, howto)

```python
@app.get('/blog/type/{type}')
def get_blog_type(type: BlogType):
  return {'message': f'Blog type {type}'}
```
## Query parameters

Les query parameters ont une syntaxe légèrement différente, au lieu que les parameters soit uniquement disposé dans le path, on va les ajouter à la fin.

[main.py](query_parameters/main.py)
```python
from typing import Optional
from fastapi import FastAPI
from enum import Enum


app = FastAPI()

@app.get('/hello')
def index():
  return {'message': 'Hello world!'}

@app.get('/blog/all')
def get_blogs(page = 1, page_size: Optional[int] = None):
  return {'message': f'All {page_size} blogs on page {page}'}

@app.get('blog/{id}/comments/{comment_id}')
def get_comment(id: int, comment_id: int, valid: bool = True, username: Optional[str] = None):
  return {'message': f'blog_id {id}, comment_id {comment_id}, valid {valid}, username {username}'}

class BlogType(str, Enum):
    short = 'short'
    story = 'story'
    howto = 'howto'

@app.get('/blog/type/{type}')
def get_blog_type(type: BlogType):
  return {'message': f'Blog type {type}'}

@app.get('/blog/{id}')
def get_blog(id: int):
  return {'message': f'Blog with id {id}'}
```
Exemple : <http://localhost:8000/blogs/all?page=2&page_size=10>

on voit qu’après le chemin il y d’abord un ? puis page=2 ainsi qu’un & puis un page_size=10 regardons la fonction dans notre code qui correspond à ce path
```python
@app.get('/blog/all')
def get_blogs(page = 1, page_size: Optional[int] = None):
    return {'message': f'All {page_size} blogs on page {page}'}
```
Comme on peut le voir les dans cette manière de rédiger, nous ne mettons pas les variables dans le path mais exclusivement en argument de fonction, cette redaction est celle utilisé de manière générale.

En plus de cette nouvelle syntaxe, on peut facilement intéger des valeurs par défaut (page est à 1 et page_size est à None), on peut aussi les rendre optionnel

(page_size: Optional[int]).

On peut aussi combiner les path parameters ainsi que les querys parameters.

```python
@app.get('blog/{id}/comments/{comment_id}')
def get_comment(id: int, comment_id: int, valid: bool = True, username: Optional[str] = None):
    return {'message': f'blog_id {id}, comment_id {comment_id}, valid {valid}, username {username}'}
```
