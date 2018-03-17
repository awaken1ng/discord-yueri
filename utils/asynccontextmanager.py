from contextlib import wraps
import abc
# import sys
import _collections_abc

""" Slight modification of contextlib.contextmanager """


class AbstractAsyncContextManager(abc.ABC):
    """An abstract base class for context managers."""

    async def __aenter__(self):
        """Return `self` upon entering the runtime context."""
        return self

    @abc.abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback):
        """Raise any exception triggered within the runtime context."""
        return None

    @classmethod
    def __subclasshook__(cls, C):
        if cls is AbstractAsyncContextManager:
            return _collections_abc._check_methods(C, "__enter__", "__exit__")
        return NotImplemented


class AsyncContextDecorator(object):
    "A base class or mixin that enables context managers to work as decorators."

    def _recreate_cm(self):
        """Return a recreated instance of self.

        Allows an otherwise one-shot context manager like
        _GeneratorContextManager to support use as
        a decorator via implicit recreation.

        This is a private interface just for _GeneratorContextManager.
        See issue #11647 for details.
        """
        return self

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwds):
            with self._recreate_cm():
                return func(*args, **kwds)

        return inner


class _AsyncGeneratorContextManager(AsyncContextDecorator, AbstractAsyncContextManager):
    """Helper for @contextmanager decorator."""

    def __init__(self, func, args, kwds):
        self.gen = func(*args, **kwds)
        self.func, self.args, self.kwds = func, args, kwds
        # Issue 19330: ensure context manager instances have good docstrings
        doc = getattr(func, "__doc__", None)
        if doc is None:
            doc = type(self).__doc__
        self.__doc__ = doc
        # Unfortunately, this still doesn't provide good help output when
        # inspecting the created context manager instances, since pydoc
        # currently bypasses the instance docstring and shows the docstring
        # for the class instead.
        # See http://bugs.python.org/issue19404 for more details.

    def _recreate_cm(self):
        # _GCM instances are one-shot context managers, so the
        # CM must be recreated each time a decorated function is
        # called
        return self.__class__(self.func, self.args, self.kwds)

    async def __aenter__(self):
        try:
            return await self.gen.__anext__()
        except StopIteration:
            raise RuntimeError("generator didn't yield") from None

    async def __aexit__(self, type, value, traceback):
        pass
        # if type is None:
        #     try:
        #         next(self.gen)
        #     except StopIteration:
        #         return False
        #     else:
        #         raise RuntimeError("generator didn't stop")
        # else:
        #     if value is None:
        #         # Need to force instantiation so we can reliably
        #         # tell if we get the same exception back
        #         value = type()
        #     try:
        #         self.gen.athrow(type, value, traceback)
        #     except StopIteration as exc:
        #         # Suppress StopIteration *unless* it's the same exception that
        #         # was passed to throw().  This prevents a StopIteration
        #         # raised inside the "with" statement from being suppressed.
        #         return exc is not value
        #     except RuntimeError as exc:
        #         # Don't re-raise the passed in exception. (issue27122)
        #         if exc is value:
        #             return False
        #         # Likewise, avoid suppressing if a StopIteration exception
        #         # was passed to throw() and later wrapped into a RuntimeError
        #         # (see PEP 479).
        #         if type is StopIteration and exc.__cause__ is value:
        #             return False
        #         raise
        #     except:
        #         # only re-raise if it's *not* the exception that was
        #         # passed to throw(), because __exit__() must not raise
        #         # an exception unless __exit__() itself failed.  But throw()
        #         # has to raise the exception to signal propagation, so this
        #         # fixes the impedance mismatch between the throw() protocol
        #         # and the __exit__() protocol.
        #         #
        #         if sys.exc_info()[1] is value:
        #             return False
        #         raise
        #     raise RuntimeError("generator didn't stop after throw()")


def asynccontextmanager(func):
    # FIXME doesn't execute code after yielding
    @wraps(func)
    def helper(*args, **kwds):
        return _AsyncGeneratorContextManager(func, args, kwds)

    return helper
