from typing import List


def split_list(lst: List, separators: List) -> List[List]:
    """
    :return: splits list on element and returns a list of the sub-lists created.
    """
    sub_lists = []
    curr_acc = []

    for elem in lst:
        if elem in separators:
            if curr_acc != []:
                sub_lists.append(curr_acc)
                curr_acc = []
        else:
            curr_acc.append(elem)

    if curr_acc != []:
        sub_lists.append(curr_acc)

    return sub_lists
