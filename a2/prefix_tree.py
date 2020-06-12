"""CSC148 Assignment 2: Autocompleter classes

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===
This file contains the design of a public interface (Autocompleter) and two
implementation of this interface, SimplePrefixTree and CompressedPrefixTree.
You'll complete both of these subclasses over the course of this assignment.

As usual, be sure not to change any parts of the given *public interface* in the
starter code---and this includes the instance attributes, which we will be
testing directly! You may, however, add new private attributes, methods, and
top-level functions to this file.
"""
from __future__ import annotations
from typing import Any, List, Optional, Tuple


################################################################################
# The Autocompleter ADT
################################################################################
class Autocompleter:
    """An abstract class representing the Autocompleter Abstract Data Type.
    """

    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""
        raise NotImplementedError

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        raise NotImplementedError

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        raise NotImplementedError

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        raise NotImplementedError


################################################################################
# SimplePrefixTree (Tasks 1-3)
################################################################################
class SimplePrefixTree(Autocompleter):
    """A simple prefix tree.

    This class follows the implementation described on the assignment handout.
    Note that we've made the attributes public because we will be accessing them
    directly for testing purposes.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.
    _count:
        The number of leaves in this prefix tree.
    _weight_type:
        The weighting type of the prefix tree.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - ("prefixes grow by 1")
      If len(self.subtrees) > 0, and subtree in self.subtrees, and subtree
      is non-empty and not a leaf, then

          subtree.value == self.value + [x], for some element x

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Any
    weight: float
    subtrees: List[SimplePrefixTree]
    _count: int
    _weight_type: str
    _before: Optional[SimplePrefixTree]

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty simple prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """
        self.value = []
        self.subtrees = []
        self._weight_type = weight_type
        self.weight = 0.0
        self._count = 0
        self._before = None

    def is_empty(self) -> bool:
        """Return whether this simple prefix tree is empty."""
        return self.weight == 0.0

    def is_leaf(self) -> bool:
        """Return whether this simple prefix tree is a leaf."""
        return self.weight > 0 and self.subtrees == []

    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter.
        >>> tree = SimplePrefixTree("sum")
        >>> tree.insert("car", 20, ['c','a','r'])
        >>> tree.insert('care', 30, ['c', 'a', 'r', 'e'])
        >>> tree.__len__()
        2
        """
        # meaning count number of leaves
        if self._before is None and len(self.subtrees) == 0:
            return 0
        if self.is_leaf():
            return 1
        else:
            # inner node case
            total_leaf = 0
            for subtree in self.subtrees:
                total_leaf += subtree.__len__()
            return total_leaf

    def _update_weight(self, weight: float) -> None:
        """
        Update the weight of the tree.
        >>> tree = SimplePrefixTree("average")
        >>> tree.insert("car", 30, ['c','a','r'])
        >>> tree.subtrees[0].subtrees[0].weight
        30.0
        >>> tree.insert('care', 20, ['c','a','r','e'])
        >>> tree.weight
        25.0
        >>> print(tree.__str__())
        >>> tree.insert('cat', 22, ['c','a','t'])
        >>> tree.weight
        24.0
        >>> print(tree.__str__())
        >>> tree.insert('care', 20, ['c','a','r','e'])
        >>> print(tree.__str__())
        """
        temp = self
        while temp._before is not None:
            if temp._weight_type == "sum":
                temp._before._count = temp._before.__len__()
                temp._before.weight += weight
            elif temp._weight_type == "average":
                if temp._before.__len__() == 0:
                    temp._before.weight = 0
                else:
                    total = temp._before.weight * temp._before._count + weight
                    temp._before.weight = total / temp._before.__len__()
                    temp._before._count = temp._before.__len__()
            temp._before._sort_weight()
            temp = temp._before

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        >>> tree = SimplePrefixTree("average")
        >>> tree.is_empty()
        True
        >>> tree.value
        []
        >>> tree.weight
        0
        >>> tree.subtrees
        []
        >>> tree.insert("car", 30, ['c','a','r'])
        >>> tree.subtrees[0].value == ['c']
        True
        >>> tree.insert('care', 20, ['c', 'a', 'r', 'e'])
        >>> tree.subtrees[0].value == ['c']
        True
        >>> tree.insert('cat', 22, ['c','a','t'])
        >>> tree.weight
        0
        >>> len(tree.subtrees[0].subtrees)
        1
        >>> tree.__len__()
        2
        >>> tree.subtrees[0].subtrees[0].__len__()
        2
        >>> print(tree.__str__())
        []
        >>> tree.weight
        25.0
        >>> tree.subtrees[0].subtrees[0].subtrees[0].value
        ['c', 'a', 'r']
        >>> tree.subtrees[0].subtrees[0].subtrees[0].subtrees[0].weight
        30
        >>> tree.subtrees[0].subtrees[0].subtrees[0].subtrees[0].value
        'car'
        >>> wangjie = SimplePrefixTree("sum")
        >>> wangjie.insert("car", 20, [])
        >>> wangjie.__len__()
        1
        >>> cutewang = SimplePrefixTree("sum")
        >>> cutewang.insert("car", 20, ['c'])
        >>> cutewang.subtrees[0].value
        ['c']
        >>> cutewang.subtrees[0].subtrees[0].value
        'car'
        """
        if prefix == self.value:
            # base case
            flag1 = True
            for subtree in self.subtrees:
                if subtree.value == value:
                    subtree.weight += weight
                    subtree._update_weight(weight)
                    flag1 = False
            # leaf not exist
            if flag1:
                new_leave = SimplePrefixTree(self._weight_type)
                new_leave.value, new_leave.weight = value, weight
                new_leave._before = self
                self.subtrees.append(new_leave)
                new_leave._update_weight(weight)
                new_leave._count += 1
        elif prefix != self.value:
            # have not find the subtree that match entirely with prefix yet
            flag2 = True
            for subtree in self.subtrees:
                if prefix[0:len(subtree.value)] == subtree.value:
                    subtree.insert(value, weight, prefix)
                    flag2 = False
            # does not exist a subtree that match the current prefix
            # create a subtree that match the current prefix
            if flag2:
                self.insert_subtree(prefix[len(self.value)])
                self.subtrees[-1].insert(value, weight, prefix)

    def __lt__(self, other: SimplePrefixTree) -> bool:
        return self.weight < other.weight

    def _sort_weight(self) -> None:
        """Sort the subtrees of the SimplePrefixTree into non-increasing order
        >>> tree = SimplePrefixTree("average")
        >>> tree.insert("car", 20, ['c','a','r'])
        >>> tree.insert('care', 30, ['c', 'a', 'r', 'e'])
        >>> tree.subtrees[0].subtrees[0].subtrees[0].value
        ['c', 'a', 'r']
        >>> len(tree.subtrees[0].subtrees[0].subtrees[0].subtrees)
        2
        >>> tree.subtrees[0].subtrees[0].subtrees[0].subtrees[0].weight
        20
        >>> tree.subtrees[0].subtrees[0].subtrees[0]._sort_weight()
        >>> tree.subtrees[0].subtrees[0].subtrees[0].subtrees[0].weight
        30.0
        """
        self.subtrees.sort(reverse=True)

    def insert_subtree(self, first_prefix: str) -> None:
        """
        Insert a subtree path to new value
        """
        new_subtree = SimplePrefixTree(self._weight_type)
        new_subtree.value = self.value + [first_prefix]
        new_subtree._before = self
        self.subtrees.append(new_subtree)

    def _get_all_match(self) -> List[Tuple[Any, float]]:
        """
        Return the list of matches for the given prefix.
        """
        result = []
        if self.is_empty():
            return []
        elif self.is_leaf():
            # self.subtree == []
            leaf = (self.value, self.weight)
            result.append(leaf)
            return result
        else:
            for subtree in self.subtrees:
                result += subtree._get_all_match()
            return sorted(result, key=lambda x: x[1], reverse=True)

    def _find_tree(self, prefix: List) -> Optional[SimplePrefixTree]:
        """
        Find a SimplePrefixTree that matches with the given prefix.
        Return None if cannot find such tree.
        >>> tree = SimplePrefixTree('sum')
        >>> tree.insert("car", 20, ['c','a','r'])
        >>> tree.insert('care', 30, ['c', 'a', 'r', 'e'])
        >>> tree.insert('cat', 22, ['c','a','t'])
        >>> tree.insert('d', 10, ['d'])
        >>> subtree = tree._find_tree(['c','a','r'])
        >>> subtree.value
        ['c', 'a', 'r']
        >>> subtree.subtrees[0].value
        ['c', 'a', 'r', 'e']
        >>> subtree2 = tree._find_tree([])
        >>> subtree2.value
        []
        >>> subtree3 = tree._find_tree(['c'])
        >>> subtree3.value
        ['c']
        >>> tree.insert('carep', 40, ['c','a','r','e','p'])
        >>> subtree4 = tree._find_tree([])
        """
        if self.value[0:len(prefix)] == prefix or self.is_leaf():
            # find prefix
            return self
        else:
            # len(prefix) != 0:
            for subtree in self.subtrees:
                if prefix[0:len(subtree.value)] == subtree.value:
                    return subtree._find_tree(prefix)
            return None

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        >>> tree2 = SimplePrefixTree("average")
        >>> tree2.insert('Alice', 5, ['a', 'c', 'b', 'b'])
        >>> tree2.insert('Jacky', 10, ['a', 'c', 'b', 'f'])
        >>> tree2.insert('Bob', 10, ['a', 'd'])
        >>> tree2.insert('K', 9, ['a', 'd'])
        >>> tree2.autocomplete(['a'], 3)
        []
        assert the tree we want to return leaf is found
        >>> tree = SimplePrefixTree("average")
        >>> tree.insert("car", 20, ['c','a','r'])
        >>> tree.insert('care', 30, ['c', 'a', 'r', 'e'])
        >>> tree.insert('cat', 22, ['c','a','t'])
        >>> tree.insert('danger', 10, ['d','a','n','g','e','r'])
        >>> tree.autocomplete(['e'])
        []
        >>> tree.autocomplete(['c','a','r'],4)
        [('care', 30), ('car', 20)]
        >>> tree.autocomplete(['c'], 1)
        [('care', 30)]
        >>> tree.autocomplete(['c'], 2)
        [('care', 30), ('car', 20)]
        >>> tree.autocomplete([], 2)
        [('care', 30), ('car', 20)]
        >>> tree.autocomplete([], 3)
        [('care', 30), ('cat', 22), ('car', 20)]
        >>> tree.insert('carep', 40, ['c','a','r','e','p'])
        >>> tree.autocomplete(['c'], 2)
        [('carep', 40), ('care', 30)]
        >>> tree.autocomplete(['c','a','r','e','p'], 2)
        [('carep', 40)]
        >>> tree.insert('cared', 5, ['c', 'a', 'r', 'e', 'd'])
        >>> tree.autocomplete(['c'], 2)
        [('carep', 40), ('care', 30)]
        """
        if self._find_tree(prefix) is not None:
            if limit is None or limit >= self._find_tree(prefix)._count:
                return self._find_tree(prefix)._get_all_match()
            else:
                # limit < self._count
                acc = []
                for subtree in self._find_tree(prefix).subtrees:
                    acc += subtree.autocomplete(prefix, limit)
                    # print(acc)
                    if len(acc) >= limit:
                        return sorted(acc[: limit], key=lambda x: x[1],
                                      reverse=True)
        else:
            return []

    def __str__(self) -> str:

        """Return a string representation of this tree.

        You may find this method helpful for debugging.
        """

        return self._str_indented()

    def _str_indented(self, depth: int = 0) -> str:

        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """

        if self.is_empty():
            return ''
        else:
            s = '  ' * depth + f'{self.value} ({self.weight})\n'
            for subtree in self.subtrees:
                s += subtree._str_indented(depth + 1)
            return s

    def remove(self, prefix: List) -> None:

        """Remove all values that match the given prefix.
        >>> tree = SimplePrefixTree('sum')
        >>> tree.insert("car", 20, ['c','a','r'])
        >>> tree.insert('care', 30, ['c', 'a', 'r', 'e'])
        >>> tree.insert('cat', 22, ['c','a','t'])
        >>> tree.remove(['c', 'a', 'r'])
        """
        current = self._find_tree(prefix)
        if current == self:
            self.subtrees = []
            self.weight = 0.0
        elif current is not None:
            for subtree in current._before.subtrees:
                if subtree.value == prefix:
                    current._before.subtrees.remove(subtree)
                    if self._weight_type == 'average':
                        current._update_weight(-current.weight * current._count)
                    else:
                        current._update_weight(-current.weight)
                    # sum of self.leave weight instead of self.weight
            if len(current._before.subtrees) == 0:
                if current._before._before is not None:
                    current._before._before.remove(current._before.value)
            # do we really need else here?


################################################################################
# CompressedPrefixTree (Task 6)
################################################################################
def common_prefix(prefix1: Any, prefix2: Any) -> List:
    """
    Return a list of the common prefix of two prefix lists.
    >>> tree = CompressedPrefixTree('sum')
    >>> common_prefix(['c', 'a', 'r'], ['c', 'a', 't'])
    ['c', 'a']
    """
    if not isinstance(prefix1, list) or not isinstance(prefix2, list):
        return []
    i = 0
    while i < len(prefix1) and i < len(prefix2) and prefix1[i] == \
            prefix2[i]:
        i += 1
    if i == len(prefix1):
        return prefix1
    elif i == len(prefix2):
        return prefix2
    else:
        return prefix1[0:i]


class CompressedPrefixTree(SimplePrefixTree):
    """A compressed prefix tree implementation.

    While this class has the same public interface as SimplePrefixTree,
    (including the initializer!) this version follows the implementation
    described on Task 6 of the assignment handout, which reduces the number of
    tree objects used to store values in the tree.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - **NEW**
      This tree does not contain any compressible internal values.
      (See the assignment handout for a definition of "compressible".)

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Optional[Any]
    weight: float
    subtrees: List[CompressedPrefixTree]
    _count: int
    _weight_type: str
    _before: Optional[CompressedPrefixTree]

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty compressed prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """
        SimplePrefixTree.__init__(self, weight_type)

    def common_tree(self, prefix: List) -> Optional[CompressedPrefixTree]:
        """
        Return the internal value in the compressed tree that has the longest
        common prefix with prefix.
        >>> tree = CompressedPrefixTree("average")
        >>> tree.insert("car", 30.0, ['c','a','r'])
        >>> tree.insert('care', 20.0, ['c', 'a', 'r', 'e'])
        >>> t = tree.common_tree(['c', 'a', 't'])
        >>> t.value
        """
        if len(prefix) == 0:
            return self
        elif self.is_leaf():
            return self._before
        # elif len(self.common_prefix(self.value, prefix)) != 0:
        #     longest = len(self.common_prefix(self.value, prefix))
        #     for subtree in self.subtrees:
        #       if len(subtree.common_prefix(subtree.value, prefix)) > longest:
        #           longest = len(subtree.common_prefix(subtree.value, prefix))
        #     if longest == len(self.common_prefix(self.value, prefix)):
        #         return self
        #     else:
        #         return subtree
        else:
            i = 0
            flag = False
            while i < len(self.subtrees) and len(common_prefix(
                    self.subtrees[i].value,
                    prefix)) == 0:
                if self.subtrees[i].is_leaf():
                    flag = True
                i += 1
            if i == len(self.subtrees):
                if flag and common_prefix(self.value, prefix) != []:
                    return self
                else:
                    return None
            com_b = common_prefix(self.value, prefix)
            for subtree in self.subtrees:
                if com_b != common_prefix(subtree.value, prefix):
                    return subtree.common_tree(prefix)
            return self

    def add_leaf(self, value: Any, weight: float) -> None:
        """
        Add a leaf with value and weight to an internal value of
        the prefix tree and update the weight.
        """
        leaf = CompressedPrefixTree(self._weight_type)
        leaf.value, leaf.weight = value, weight
        leaf._before = self
        self.subtrees.append(leaf)
        leaf._count += 1
        leaf._update_weight(weight)

    def insert_root(self) -> CompressedPrefixTree:
        """
        Insert root.
        """
        tree = CompressedPrefixTree(self._weight_type)
        tree.weight = self.weight
        tree._count = self._count
        for i in self.value:
            tree.value.append(i)
        for j in self.subtrees:
            tree.subtrees.append(j)
        return tree

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """
        Insert the given value into this Autocompleter.

            The value is inserted with the given weight, and is associated with
            the prefix sequence <prefix>.

            If the value has already been inserted into this prefix tree
            (compare values using ==), then the given weight should be *added*
             to the existing weight of this value.

            Preconditions:
                weight > 0
                The given value is either:
                    1) not in this Autocompleter
                    2) was previously inserted with the SAME prefix sequence
        >>> tree2 = CompressedPrefixTree("average")
        >>> tree2.insert('Alice', 5, ['a', 'c', 'b', 'b'])
        >>> tree2.insert('Jacky', 10, ['a', 'c', 'b', 'f'])
        >>> tree2.insert('Bob', 10, ['a', 'd'])
        >>> tree2.insert('K', 9, ['a', 'd'])
        >>> tree2.insert('g', 8, ['e'])
        >>> tree2.insert('p', 8, ['c'])
        >>> print(tree2.__str__())
        """
        common = self.common_tree(prefix)
        # common = self
        if common is not None:
            # common = self
            common_pre = common_prefix(prefix, common.value)
            # self.value partial ['a,'b']
            if len(common_pre) == len(common.value):
                if common_pre == prefix:
                    flag = True
                    for subtree in common.subtrees:
                        if subtree.value == value:
                            subtree.weight += weight
                            subtree._update_weight(weight)
                            flag = False
                    if flag:
                        common.add_leaf(value, weight)
                else:
                    inter = CompressedPrefixTree(self._weight_type)
                    common.subtrees.append(inter)
                    inter._before = common
                    inter.value = prefix
                    inter.add_leaf(value, weight)
            elif len(common_pre) < len(common.value):
                tree = common.insert_root()
                common.value = common_pre
                common.subtrees = [tree]
                tree._before = common
                # [c,a]
                inter3 = CompressedPrefixTree(common._weight_type)
                inter3.value = prefix
                common.subtrees.append(inter3)
                inter3._before = common
                inter3.add_leaf(value, weight)
        else:
            if self.is_empty():
                self.value = prefix
                self.add_leaf(value, weight)
            elif self.value != []:
                # self.is not empty
                tree = self.insert_root()
                self.subtrees = [tree]
                self.value = []
                tree._before = self
                inter2 = CompressedPrefixTree(self._weight_type)
                inter2._before = self
                inter2.value = prefix
                self.subtrees.append(inter2)
                inter2.add_leaf(value, weight)
            else:
                inter3 = CompressedPrefixTree(self._weight_type)
                inter3._before = self
                inter3.value = prefix
                self.subtrees.append(inter3)
                inter3.add_leaf(value, weight)

    def _compressed_find_tree(self, prefix: List) -> Optional[
        CompressedPrefixTree]:
        """
        Find a SimplePrefixTree that matches with the given prefix.
        Return None if cannot find such tree.
        >>> tree = CompressedPrefixTree('average')
        >>> tree.insert('car', 100.0, ['c', 'a', 'r'])
        >>> tree.insert('door', 4.0, ['d', 'o', 'o', 'r'])
        >>> tree.insert('danger', 6.0, ['d', 'a', 'n', 'g', 'e', 'r'])
        >>> tree.insert('cat', 20.0, ['c', 'a', 't'])
        >>> tree.insert('care', 30.0, ['c', 'a', 'r', 'e'])
        >>> tree._compressed_find_tree(['d', 'a']).value
        >>> tree2 = CompressedPrefixTree("average")
        >>> tree2.insert('Alice', 5, ['a', 'c', 'b', 'b'])
        >>> tree2.insert('Jacky', 10, ['a', 'c', 'b', 'f'])
        >>> tree2.insert('Bob', 10, ['a', 'd'])
        >>> tree2.insert('K', 9, ['a', 'd'])
        >>> tree2._compressed_find_tree(['a']).value
        []
        """
        if self.value[0:len(prefix)] == prefix or self.is_leaf():
            # find prefix
            return self
        else:
            # len(prefix) != 0:
            for subtree in self.subtrees:
                if len(subtree.value) < len(prefix):
                    if subtree.value == prefix[0:len(subtree.value)]:
                        return subtree._compressed_find_tree(prefix)
                elif len(subtree.value) >= len(prefix):
                    if subtree.value[0:len(prefix)] == prefix:
                        return subtree._compressed_find_tree(prefix)
            return None

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        >>> tree2 = CompressedPrefixTree("sum")
        >>> tree2.insert('Alice', 5, [1,2,3])
        >>> tree2.insert('Jacky', 10, [2,3,4])
        >>> tree2.insert('Bob', 10, [1,2])
        >>> tree2.insert('K', 9, [1,2,4])
        >>> tree2.insert('t', 3, [1,2,6])
        >>> tree2.insert('ha', 5, [1,2,5])
        >>> tree2.insert('xixi', 30, [1,2,8])
        >>> tree2.insert('haha', 19, [1,2,0,8])
        >>> tree2.insert('K', 60, [3,4,8])
        >>> tree2.insert('89', 9, [3,6])
        >>> tree2.insert('40', 9, [3,3])
        >>> tree2.insert('68', 30, [1,2,6.4])
        >>> print(tree2.__str__())
        """
        # assert the tree we want to return leaf is found
        if self._compressed_find_tree(prefix) is not None:
            if limit is None or limit >= self._compressed_find_tree(prefix)._count:
                return self._compressed_find_tree(prefix)._get_all_match()
            else:
                # limit < self._count
                acc = []
                for subtree in self._compressed_find_tree(prefix).subtrees:
                    acc += subtree.autocomplete(prefix, limit)
                    # print(acc)
                    if len(acc) >= limit:
                        return sorted(acc[: limit], key=lambda x: x[1],
                                      reverse=True)
        else:
            return []

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        >>> tree = CompressedPrefixTree("sum")
        >>> tree.insert('car', 100.0, ['c', 'a', 'r'])
        >>> tree.insert('door', 4.0, ['d', 'o', 'o', 'r'])
        >>> tree.insert('danger', 6.0, ['d', 'a', 'n', 'g', 'e', 'r'])
        >>> tree.insert('cat', 20.0, ['c', 'a', 't'])
        >>> tree.insert('care', 30.0, ['c', 'a', 'r', 'e'])
        >>> tree.remove(['c', 'a', 'r'])
        >>> print(tree.__str__())
        >>> len(tree.subtrees)
        2
        >>> tree.subtrees[0].value
        ['c', 'a', 't']
        >>> tree = CompressedPrefixTree('sum')
        >>> tree.insert('Hello', 2.0, ['a', 'b', 'c', 'd'])
        >>> tree.insert('Hey', 2.0, ['a', 'b', 'c', 'q'])
        >>> tree.insert('bye', 4.0, ['a', 'b', 'f', 'c'])
        >>> tree.remove(['a', 'b', 'f'])
        >>> print(tree.__str__())
        """
        current = self._compressed_find_tree(prefix)
        # ['c',a,r]
        if current == self:
            self.subtrees = []
            self.weight = 0.0
            self.value = []
        elif current is not None:
            # # find the prefix tree
            # for subtree in current._before.subtrees:
            #     if subtree.value[0:len(prefix)] == prefix:
            #         current._before.subtrees.remove(subtree)
            current._before.subtrees.remove(current)
            if self._weight_type == 'average':
                current._update_weight(-current.weight * current._count)
            else:
                current._update_weight(-current.weight)
                # sum of self.leave weight instead of self.weight
            if len(current._before.subtrees) == 1 and not \
                    current._before.subtrees[0].is_leaf():
                if current._before._before is not None:
                    current._before.subtrees[
                        0]._before = current._before._before
                    current._before._before.subtrees.remove(current._before)
                    current._before._before.subtrees.append(
                        current._before.subtrees[0])
                    current._before._before._sort_weight()
                else:
                    current._before.value = current._before.subtrees[0].value
                    for i in current._before.subtrees[0].subtrees:
                        current._before.subtrees.append(i)
                    current._before.weight = current._before.subtrees[0].weight
                    current._before.subtrees.pop(0)

            # do we really need else here?


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'max-nested-blocks': 4
    })
