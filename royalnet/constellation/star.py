from typing import Type, TYPE_CHECKING, List, Union
from starlette.requests import Request
from starlette.responses import Response
if TYPE_CHECKING:
    from .constellation import Constellation


class Star:
    """A Star is a class representing a part of the website.

    It shouldn't be used directly: please use :class:`PageStar` and :class:`ExceptionStar` instead!"""
    tables: set = {}
    """The set of :class`Alchemy` :class:`Table` classes required by this Star to function."""

    def __init__(self, constellation: "Constellation"):
        self.constellation: "Constellation" = constellation

    async def page(self, request: Request) -> Response:
        """The function generating the :class:`Response` to a web :class:`Request`.

        If it raises an error, the corresponding :class:`ExceptionStar` will be used to handle the request instead."""
        raise NotImplementedError()

    @property
    def alchemy(self):
        return self.constellation.alchemy

    @property
    def Session(self):
        return self.constellation.alchemy.Session

    @property
    def session_acm(self):
        return self.constellation.alchemy.session_acm


class PageStar(Star):
    """A PageStar is a class representing a single route of the website (for example, ``/api/user/get``).

    To create a new website route you should create a new class inheriting from this class with a function overriding
    :meth:`page` and changing the values of :attr:`path` and optionally :attr:`methods` and :attr:`tables`."""
    path: str = NotImplemented
    """The route of the star.
    
    Example:
        ::
        
            path: str = '/api/user/get'
        
    """

    methods: List[str] = ["GET"]
    """The HTTP methods supported by the Star, in form of a list.
    
    By default, a Star only supports the ``GET`` method, but more can be added.
    
    Example:
        ::
        
            methods: List[str] = ["GET", "POST", "PUT", "DELETE"]
            
    """


class ExceptionStar(Star):
    """An ExceptionStar is a class that handles an :class:`Exception` raised by another star by returning a different
    response than the one originally intended.

    The handled exception type is specified in the :attr:`error`.

    It can also handle standard webserver errors, such as ``404 Not Found``:
    to handle them, set :attr:`error` to an :class:`int` of the corresponding error code.

    To create a new exception handler you should create a new class inheriting from this class with a function
    overriding :meth:`page` and changing the values of :attr:`error` and optionally :attr:`tables`."""
    error: Union[Type[Exception], int]
    """The error that should be handled by this star. It should be either a subclass of :exc:`Exception`, 
    or the :class:`int` of an HTTP error code."""
