from fastapi import FastAPI, HTTPException, Depends, Cookie, Response
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

users_db = {}


class User(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None


class UserInDB(User):
    hashed_password: str


def get_user(username: str):
    if username in users_db:
        user_dict = users_db[username]
        return UserInDB(**user_dict)


def create_user(user: User):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="User already registered")
    hashed_password = user.password 
    user_data = user.dict(exclude={'password'}) 
    user_data['hashed_password'] = hashed_password
    users_db[user.username] = user_data
    return user


@app.post("/register", response_model=User)
async def register(user: User):
    return create_user(user)


@app.post("/login")
async def login(username: str, password: str, response: Response):
    user = get_user(username)
    if not user or user.hashed_password != password:  
        raise HTTPException(status_code=401, detail="Invalid credentials")

    response.set_cookie(key="username", value=username)
    return {"message": "Login successful"}


@app.get("/profile")
async def profile(username: str = Depends(get_user)):
    if not username:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return {"full_name": username.full_name}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
