# File

FastApi nous permet de d’intéragir avec les fichier, les fichier sont stockés en byte et en mémoire, il ne faut qu’ils soient trop lourd.

[file.py](file/router/file.py)

```python
from fastapi import APIRouter, File, UploadFile
import shutil
from fastapi.responses import FileResponse


router = APIRouter(
  prefix='/file',
  tags=['file']
)

@router.post('/file')
def get_file(file: bytes = File(...)):
  content = file.decode('utf-8')
  lines = content.split('\n')
  return {'lines': lines}
```

cette fonction est simple, elle décode le code de byte au caractère (on suppose que l’encoding est utf-8, mais ce n’est pas toujours le cas !), \n sert à déterminer le saut de lignes, coupler à split, on crée une élément de liste par ligne.

vous pouvez utilisez le fichier [test.csv](file/test.csv)

## upload file

FastApi permet d’uploader des fichiers, les fichier sont stoker en mémoire puis sur disque les fichiers peuvent donc être plus large (image, videos, etc.).

[file.py](upload_file/router/file.py)

```python
from fastapi import APIRouter, File, UploadFile
import shutil


router = APIRouter(
  prefix='/file',
  tags=['file']
)

@router.post('/file')
def get_file(file: bytes = File(...)):
  content = file.decode('utf-8')
  lines = content.split('\n')
  return {'lines': lines}

@router.post('/uploadfile')
def get_uploadfile(upload_file: UploadFile = File(...)):
  path = f"files/{upload_file.filename}"
  with open(path, 'w+b') as buffer:
    shutil.copyfileobj(upload_file.file, buffer)

  return {
    'filename': path,
    'type': upload_file.content_type
  }
```

## File statically available

Quand on met un fichier (photos, son…) il n’est pas directement accessible au client ce qui peut dans certain cas être bloquant, pour régler ce problème, il faut tout d’abord installer la libraire aiofiles

[main.py](static_file/main.py)

```python
from typing import Optional
from fastapi import FastAPI, Request
from router import blog_get, blog_post, user, article, product, file
from auth import authentication
from db.database import engine
from db import models
from exceptions import StoryException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.include_router(authentication.router)
app.include_router(file.router)
app.include_router(user.router)
app.include_router(article.router)
app.include_router(product.router)
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

origins = [
  'http://localhost:3000'
]

app.add_middleware(
  CORSMiddleware,
  allow_origins = origins,
  allow_credentials = True,
  allow_methods = ["*"],
  allow_headers = ['*']
)

app.mount('/files', StaticFiles(directory="files"), name='files')
```

il y a deux choses importantes à retenir ici :

- ```from fastapi.staticfiles import StaticFiles``` qui va permettre d’apporter la librairie et de faire en sorte que nos fichiers soient disponibles au client
- ```app.mount('/files', StaticFiles(directory="files"), name='files')``` permet d’indiquer où les fichier sont.

Pour accéder au fichier de notre exemple avec le chemin http://localhost:8000/files/test.jpg

## Download file

Maintenant, nous allons nous pencher sur le fait de rendre des fichiers téléchargeables pour le client, contrairement au static file vu plus haut, nous pouvons ajouter une logique avant l’accès aux fichier et également augmenter la sécurité.

[file.py](static_file/router/file.py)

```python
from fastapi import APIRouter, File, UploadFile
import shutil


router = APIRouter(
  prefix='/file',
  tags=['file']
)

@router.post('/file')
def get_file(file: bytes = File(...)):
  content = file.decode('utf-8')
  lines = content.split('\n')
  return {'lines': lines}

@router.post('/uploadfile')
def get_uploadfile(upload_file: UploadFile = File(...)):
  path = f"files/{upload_file.filename}"
  with open(path, 'w+b') as buffer:
    shutil.copyfileobj(upload_file.file, buffer)

  return {
    'filename': path,
    'type': upload_file.content_type
  }
```

- from fastapi.responses import FileResponse permet de renvoyer un fichier en sortie du endpoint
- @router.get('/download/{name}', response_class=FileResponse) est le décorateur indique à FastApi que le endpoint devras retourner un fichier

Il suffit d’aller dans le endpoin correspondant et taper le nom du fichier que nous voulons télécharger (test.jpg ou le nom que vous avez donné à un fichier) pour le télécharger.
