# Parameters

Dans ce cours, nous allons voir les paramètres de FastApi que nous avons déjà vu mais plus en profondeur.

## Request Body

Pour certaines requêtes, nous devons être capables de retrouver certaines informations dans le body, ce type de requêtes sont faites par des POST. Dans les méthodes POST nous ne stockons pas toutes les informations dans les query parameters mais les détails dans le body de la requête, dans FastApi nous utilisons Pydantic une librairie python.

[blog_post.py](request_body/router/blog_post.py)

```python
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix='/blog',
    tags=['blog']
)

class BlogModel(BaseModel):
  title: str
  content: str
  nb_comments: int
  published: Optional[bool]

@router.post('/new')
def create_blog(blog: BaseModel):
  return {'data': blog}
```

## Path and query parameters

Lac combinaison de path parameter, query parameter et post parameters (avec pydantic) fonction très bien ensemble, il faut juste bien s’assurer que les post parameters est bien une instance de BaseModel de pydantic.

[blog_post.py](request_body/router/blog_post.py)

```python
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix='/blog',
    tags=['blog']
)

class BlogModel(BaseModel):
  title: str
  content: str
  nb_comments: int
  published: Optional[bool]

@router.post('/new/{id}')
def create_blog(blog: BaseModel, id: int, version: int = 1):
  return {
    'id': id,
    'data': blog,
    'version': version
    }
```

## Parameters metadata

Les métadata sont des données sur des données qui servent le plus souvent rendre les choses plus simples pour les nouveaux utilisateurs.

Dans FastApi, nous pouvons utiliser des metadata sur nous paramètre pour simplifier leurs utilisation.

[blog_post.py](parameter_metadata/router/blog_post.py)

```python
from typing import Optional
from typing import Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(
    prefix='/blog',
    tags=['blog']
)

class BlogModel(BaseModel):
  title: str
  content: str
  nb_comments: int
  published: Optional[bool]

@router.post('/new/{id}')
def create_blog(blog: BaseModel, id: int, version: int = 1):
  return {
    'id': id,
    'data': blog,
    'version': version
    }

@router.post('/new/{id}/comment')
def create_comment(blog: BlogModel, id: int, 
        comment_id: int = Query(None,
            title='Id of the comment',
            description='Some description for comment_id',
            alias='commentId',
            deprecated=True
        )
    ):
    return {
        'blog': blog,
        'id': id,
        'comment_id': comment_id
    }
```
## Validator

Les validators permettent de vérifier si les parametres d’une requête respectent bien les régles que nous lui impossons

[blog_post.py](validators/router/blog_post.py)

```python
from typing import Optional
from fastapi import APIRouter, Query, Body
from pydantic import BaseModel

router = APIRouter(
    prefix='/blog',
    tags=['blog']
)

class BlogModel(BaseModel):
  title: str
  content: str
  nb_comments: int
  published: Optional[bool]

@router.post('/new/{id}')
def create_blog(blog: BaseModel, id: int, version: int = 1):
  return {
    'id': id,
    'data': blog,
    'version': version
    }

@router.post('/new/{id}/comment')
def create_comment(blog: BlogModel, id: int, 
        comment_id: int = Query(None,
            title='Id of the comment',
            description='Some description for comment_id',
            alias='commentId',
            deprecated=True
        ),
        content: str = Body(...,
            min_length=10,
            max_length=50,
            regex='^[a-z\s]*$'
        )
    ):
    return {
        'blog': blog,
        'id': id,
        'comment_id': comment_id,
        'content': content
    }
```

## Number validator

Les number validator sont des validator spécifique au nombres

[blog_post.py](number_validator/router/blog_post.py)

```python
from typing import Optional, List
from fastapi import APIRouter, Query, Body, Path
from pydantic import BaseModel

router = APIRouter(
    prefix='/blog',
    tags=['blog']
)

class BlogModel(BaseModel):
  title: str
  content: str
  nb_comments: int
  published: Optional[bool]

@router.post('/new/{id}')
def create_blog(blog: BaseModel, id: int, version: int = 1):
  return {
    'id': id,
    'data': blog,
    'version': version
    }

@router.post('/new/{id}/comment/{comment_id}')
def create_comment(blog: BlogModel, id: int, 
        comment_title: int = Query(None,
            title='Title of the comment',
            description='Some description for comment_title',
            alias='commentTitle',
            deprecated=True
        ),
        content: str = Body(...,
            min_length=10,
            max_length=50,
            regex='^[a-z\s]*$'
        ),
        v: Optional[List[str]] = Query(['1.0', '1.1', '1.2']),
        comment_id: int = Path(..., le=5)
    ):
    return {
        'blog': blog,
        'id': id,
        'comment_title': comment_title,
        'content': content,
        'version': v,
        'comment_id': comment_id
    }
```
