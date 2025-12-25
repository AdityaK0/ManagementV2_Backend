from fastapi import Response
from functools import wraps
from fastapi import Response

def public_cache(
    max_age: int = 300,
    stale_while_revalidate: int = 600,
):
    """
    Adds Cache-Control headers for Cloudflare edge caching.

    Usage:
        @public_cache(max_age=300, stale_while_revalidate=600)
        async def endpoint(...)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            response: Response | None = None

            # Try to find Response object in kwargs
            for v in kwargs.values():
                if isinstance(v, Response):
                    response = v
                    break

            # If Response not explicitly passed, FastAPI injects one
            if response is None:
                response = Response()

            response.headers["Cache-Control"] = (
                f"public, max-age={max_age}, "
                f"stale-while-revalidate={stale_while_revalidate}"
            )

            return result
        return wrapper
    return decorator


def apply_public_cache(
    response: Response,
    max_age: int = 300,
    stale_while_revalidate: int = 600,
):
    response.headers["Cache-Control"] = (
        f"public, max-age={max_age}, "
        f"stale-while-revalidate={stale_while_revalidate}"
    )
