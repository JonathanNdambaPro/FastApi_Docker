# Authentication

L’authentification et la sécurité d’une api est un sujet complexe, il n’est pas rare d’avoir des équipe dédiée dessus, nous n’allons pas couvrir tous les sujet mais uniquement sur trois sujets

- sécurisation d’une endpoint
- la génération de token
- l’authentification d’utilisateur

Nous allons explorer toutes ces méthode du plus simple au plus compliqué

## Securiting

[oauth2.py](securiting/auth/oauth2.py)

```python
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```

Cette partie est la partie qui fait nous aidera à sécuriser notre application

[article.py](securiting/router/article.py)

```python
from typing import List
from schemas import ArticleBase, ArticleDisplay, UserBase
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_article
from auth.oauth2 import oauth2_scheme

router = APIRouter(
  prefix='/article',
  tags=['article']
)

# Create article
@router.post('/', response_model=ArticleDisplay)
def create_article(request: ArticleBase, db: Session = Depends(get_db)):
  return db_article.create_article(db, request)

# Get specific article
@router.get('/{id}', response_model=ArticleDisplay)
def get_article(id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
  return {
    'data': db_article.get_article(db, id)
  }
```

En intégrant ```token: str = Depends(oauth2_scheme)``` que nous avons implémenté plus haut, nous imposons que l’utilisateur est un token valide, étant donné que nous n’en n’avons pas encore implément une fonction qui en génère il ne sera pas possible de lancer le endpoint article.

Maintenant que nous avons créer une dépendance vers oauth2 on peut voir en haut de la page du swagger un Authorize ou l’utilisateur pourra s’identifier

## Generating acess token

[ouath2.py](generation_acess_token/auth/oauth2.py)

```python
from fastapi.param_functions import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from datetime import datetime, timedelta
from jose import jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = 'fba012a2a0c9c3d884fdf15843f2aa438bac1b5e8527875ecd7187e3ce494158'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
  to_encode = data.copy()
  if expires_delta:
    expire = datetime.utcnow() + expires_delta
  else:
    expire = datetime.utcnow() + timedelta(minutes=15)
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  return encoded_jwt
```

- la secret keys et ce qui nous permet de signer notre token, elle doit être unique et est généralement généré en pseudo hasard. On peut en généré une en utilisant la commande suivante dans le terminal :

```bash
openssl rand -hex 32
```

- ALGORITHM est l’algorithme de hachage
- ACCESS_TOKEN_EXPIRE_MINUTES est le temps pendant lequel notre token est valide

la fonction create_access_token vérifie si le token envoyé est toujours valide, si c’est le cas, il le renvoie sinon il en renvoie un nouveau.

[authentification.py]()

```python
from fastapi import APIRouter, HTTPException, status
from fastapi.param_functions import Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session
from db.database import get_db
from db import models
from db.hash import Hash
from auth import oauth2

router = APIRouter(
  tags=['authentication']
)

@router.post('/token')
def get_token(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
  user = db.query(models.DbUser).filter(models.DbUser.username == request.username).first()
  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
  if not Hash.verify(user.password, request.password):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect password")
  
  access_token = oauth2.create_access_token(data={'sub': user.username})

  return {
    'access_token': access_token,
    'token_type': 'bearer',
    'user_id': user.id,
    'username': user.username
  }
```

nous avons créé un nouvel endpoint qui va généré les tokens si l’utilisateur est bien dans la base de données, le endpoint doit avoir la même nom que OAuth2PasswordBearer (ici token).

request doit être de type OAuth2PasswordRequestForm pour que FastApi comprenne que nous voulons identifier un utilisateur

les deux argument sont des dépendance pour être sur que notre code ne démarre pas tant que les valeur ne sont pas fournie pas ouath2 et la base de donnée.

La fonction get_token vérifie que l’utilisateur existe bien avant de lui fournir un token.

nous allons maintenant créer un utilisateur valide.

Dans le endpoint user (la méthode post avec en description Create User) entrer un username,email et password, une fois effectuer, entrer ces valeur dans authentification.

maintenant les méthode sont authentifié, vous pouvez utiliser les méthode lock créer un article et utiliser le endpoint get

## User Authentification

en plus de générer un token, nous devons également vérifier si ce token (bien émis par l’application), retrouver les utilisateur associé au token et sécuriser plus de endpoint.

[oauth2.py](user_authentification/auth/oauth2.py)

```python
from fastapi.param_functions import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from datetime import datetime, timedelta
from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy.orm import Session
from db.database import get_db
from fastapi import HTTPException, status
from db import db_user


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = 'fba012a2a0c9c3d884fdf15843f2aa438bac1b5e8527875ecd7187e3ce494158'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
  to_encode = data.copy()
  if expires_delta:
    expire = datetime.utcnow() + expires_delta
  else:
    expire = datetime.utcnow() + timedelta(minutes=15)
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Could not validate credentials',
    headers={"WWW-Authenticate": "Bearer"}
  )
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    if username is None:
      raise credentials_exception
  except JWTError:
    raise credentials_exception
  
  user = db_user.get_user_by_username(db, username)

  if user is None:
    raise credentials_exception

  return user
```

la nouvelle fonction get_current_user détermine si le token est bien associer à un utilisateur.

maintenant que nous avons un moyen d’identification des utilisateur nous pouvons utiliser l’user pour article.py

[article.py](user_authentification/router/article.py)
```python
from typing import List
from schemas import ArticleBase, ArticleDisplay, UserBase
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_article
from auth.oauth2 import get_current_user

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
