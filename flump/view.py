from .base_view import BaseFlumpView
from .methods import Put, Delete, GetMany, GetSingle, Post


class FlumpView(Put, Delete, GetMany, GetSingle, Post, BaseFlumpView):
    """
    A base view from which all views provided to `FlumpBlueprint` should
    inherit.

    If a client wishes to provide an API without any of the usual methods,
    they can inherit from BaseFlumpView, and mixin whichever methods they
    prefer.
    """
