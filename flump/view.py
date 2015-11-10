from .base_view import BaseFlumpView
from .methods import Patch, Delete, GetMany, GetSingle, Post


class FlumpView(Patch, Delete, GetMany, GetSingle, Post, BaseFlumpView):
    """
    A base view from which all views provided to `FlumpBlueprint` should
    inherit.

    If a client wishes to provide an API without any of the usual methods,
    they can inherit from BaseFlumpView, and mixin whichever methods they
    prefer.

    View classes which inherit from this must provide `get_entity` and
    `delete_entity` methods.
    """
