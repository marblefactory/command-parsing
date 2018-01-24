
class EquatableMixin:
    """
    Overrides equality defined using references to using the contents of the object.
    """

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False