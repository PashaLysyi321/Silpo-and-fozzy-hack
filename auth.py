import ormar
from fastapi import Response, Request
from starlette.middleware.base import BaseHTTPMiddleware

from models import User
import settings


class FakeAuth(BaseHTTPMiddleware):

    async def dispatch(
        self, request: Request, call_next
    ) -> Response:
        user_id: str = request.cookies.get(settings.SESSION_COOKIE_NAME)
        if user_id:
            try:
                user = await User.objects.get(id=user_id)
            except ormar.NoMatch:
                user = await User.objects.create()
                request.scope.update({'authenticated_user': user})
                resp: Response = await call_next(request)
                resp.set_cookie(settings.SESSION_COOKIE_NAME, user.id)
                return resp
            request.scope.update({'authenticated_user': user})
        else:
            user = await User.objects.create()
            request.scope.update({'authenticated_user': user})

        resp: Response = await call_next(request)
        resp.set_cookie(settings.SESSION_COOKIE_NAME, user.id)
        return resp
