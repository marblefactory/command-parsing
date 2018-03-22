from functools import partial
from typing import List, Callable


def split_list(lst: List, separators: List) -> List[List]:
    """
    :return: splits list on element and returns a list of the sub-lists created.
    """

    # The indices of where to split the list.
    indices = [i for i, x in enumerate(lst) if x in separators]

    if len(indices) == 0:
        return []

    # Defines the slices of lst we want. From just after the occurrence of a separator, to just before the next separator.
    slices = [(start + 1, end) for start, end in list(zip(indices, indices[1:]))]
    # Add the starts and ends of the list to the slices.
    start_ends = [(0, indices[0])] + slices + [(indices[-1] + 1, len(lst))]
    # Removes cases where the start and end are the same.
    filtered = [(start, end) for start, end in start_ends if start != end]

    chunks = [lst[start:end] for start, end in filtered]

    return chunks


class PartialClassMixin:
    @classmethod
    def partial_init(cls) -> Callable:
        def f(*args, **kwargs):
            return cls(*args, **kwargs)

        return partial(f)
