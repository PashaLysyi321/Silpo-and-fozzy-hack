from fastapi import FastAPI, Request, Response
from db import database

from starlette.middleware import Middleware

from auth import FakeAuth
from views import router

middlewares = [
    Middleware(FakeAuth)
]

app = FastAPI(middleware=middlewares)
app.state.database = database

app.include_router(router)


@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()


@app.get('/check-auth')
async def check_auth(request: Request):
    return {'user': request.scope.get('authenticated_user').id}
