import sys
from itertools import combinations
from utils import *

# this needs to be set since Python will raise max depth recursion limit
# when the data set size is about 500k instances.
# This can be customized for your data set, as well,
# though it is a dangerous option.
sys.setrecursionlimit(1500)


class FPNode(object):
    def __init__(self, item_name):
        self.__item_name = item_name
        self.__count = 1
        self.node_link = None
        self.parent = None
        self.children = []

    def reset(self):
        self.__count = 1
        self.node_link = None
        self.parent = None
        self.children = []

    def __eq__(self, value):
        return self.__item_name == value

    def __repr__(self):
        return str(self.__item_name)

    def incrementCount(self):
        self.__count += 1

    @property
    def count(self):
        return self.__count

    @property
    def item_name(self):
        return self.__item_name


class FPTree(object):
    def __init__(self, min_sup):
        """constructor

        Args:
            min_sup (int): minimum support
        """
        self.root = FPNode(None)
        self.min_sup = min_sup
        self.header_table = {}
        self.__latest_itemlink = {}
        self.frequent_item = []

    def reset(self):
        """empty the tree
        """
        self.header_table = {}
        self.__latest_itemlink = {}
        self.frequent_item = []
        self.root.reset()

    def __insert_new_node(self, parent_node, child_node):
        """insert new node to FP tree

        Args:
            parent_node (FPNode): parent node of node that needs inserting
            child_node (FPNode): node that needs inserting
        """
        parent_node.children.append(child_node)
        child_node.parent = parent_node

    def __setup_nodelink_structure(self, node):
        """setting up header table when a new node is inserted to FPTree

        Args:
            node (FPNode): new inserted node
        """
        if node.item_name not in self.header_table:
            self.header_table[node.item_name] = node
            self.__latest_itemlink[node.item_name] = node
        else:
            self.__latest_itemlink[node.item_name].node_link = node
            self.__latest_itemlink[node.item_name] = node

    def __insert_tree(self, transactions, node):
        """insert new transaction to FPTree

        Args:
            transactions (list): a list of items in a transaction
            node (FPNode): node that needs inserting
        """
        same_node = None
        current_item_name = transactions.pop(0)

        try:
            sameNodeIdx = node.children.index(current_item_name)
            node.children[sameNodeIdx].incrementCount()

            if len(transactions) != 0:
                self.__insert_tree(transactions, node.children[sameNodeIdx])

        except ValueError as e:
            child_node = FPNode(current_item_name)
            self.__insert_new_node(node, child_node)
            self.__setup_nodelink_structure(child_node)

            if len(transactions) != 0:
                self.__insert_tree(transactions, child_node)

    def buildTreeFromData(self, transactions):
        """build FP-tree from a set of transactions

        Args:
            transactions (list): list of transactions. Each transaction should be a list of item.
            For example, here is a valid list of transactions
                [['a', 'b', 'c'], ['c']]
        """
        self.reset()
        item2freq = get_sorted_frequent_item_from_data(
            transactions, self.min_sup)
        if len(item2freq) > 0:
            for transaction in transactions:
                filtered_transaction = list(
                    filter(lambda item: item in item2freq, transaction))
                if len(filtered_transaction) > 0:
                    self.__insert_tree(
                        sorted(filtered_transaction,
                               key=lambda item: item2freq[item]
                               ),
                        self.root
                    )

    def isSinglePathTree(self):
        """check whether FP-tree has only one path

        Returns:
            bool: True if tree has only one path, False otherwise
        """
        for item in self.header_table:
            if self.header_table[item].node_link is not None:
                return False
        return True

    def __get_header_pattern(self, node):
        """get header-prefix pattern

        Args:
            node (FPNode): prefix of a pattern

        Returns:
            list: a list contains of tuples, each of which has item name and item count
        """
        current_node = node
        conditional_pattern_base = []
        while current_node is not None and current_node.item_name is not None:
            conditional_pattern_base.append(
                (current_node.item_name, node.count))
            current_node = current_node.parent

        return conditional_pattern_base if len(conditional_pattern_base) > 0 else []

    def __get_conditional_pattern_base_of_item(self, item):
        """get conditional pattern base of an item in header table

        Args:
            item (str): item name

        Returns:
            list[tuple[str, int]]: conditional pattern base of an item
        """
        current_header = self.header_table[item]
        conditional_pattern_bases = []
        while current_header is not None:
            current_header_pattern = self.__get_header_pattern(current_header)
            if len(current_header_pattern) > 1:
                conditional_pattern_bases.append(current_header_pattern)
            current_header = current_header.node_link

        return conditional_pattern_bases

    def get_condition_pattern_base(self):
        """generate conditional pattern base of all item in header table

        Returns:
            dict[str, list[tuple[str, int]]]: conditional pattern base
            with key being item name
            and values being its corresponding conditional pattern base
        """
        conditional_pattern_base = {}
        for item in self.header_table:
            if len(self.__get_conditional_pattern_base_of_item(
                    item)) > 0:
                conditional_pattern_base[item] = self.__get_conditional_pattern_base_of_item(
                    item)
        return conditional_pattern_base

    def isEmptyTree(self):
        """check if a tree is empty

        Returns:
            bool: True if yes, False if not
        """
        return len(self.root.children) == 0

    def grow(self):
        """grow an FP-Tree

        Returns:
            list[tuple[list, int]]: frequent itemsets
        """
        frequent_items = []
        FPTree.__grow(self, frequent_items)
        return frequent_items

    @ staticmethod
    def __getItemListFromSinglePathTree(fp_tree):
        """get all items of a single-path tree

        Args:
            fp_tree (FPTree): object of FPTree

        Returns:
            list[tuple[str, int]]: a list of tuples, each of which has item name and item count
        """
        current_node = fp_tree.root
        items = []
        support = None

        while len(current_node.children) == 1:
            items.append(
                (current_node.children[0].item_name, current_node.children[0].count))
            current_node = current_node.children[0]

        return items

    @ staticmethod
    def __grow_single_path_tree(fp_tree, dest, frequent_set):
        """mine a single-path tree

        Args:
            fp_tree (FPTree): object of FPTree. This object should have only one path
            dest (list): destination array where items are stored
            frequent_set (list): potential frequent itemset
        """
        tree_nodes = FPTree.__getItemListFromSinglePathTree(fp_tree)
        for i in range(len(tree_nodes)):
            item_combinations = combinations(tree_nodes, i+1)
            for item_combination in item_combinations:
                frequent_items = frequent_set + list(item_combination)
                min_sup = min(map(lambda item: item[1], frequent_items))
                frequent_items = (
                    [item for item, _ in frequent_items], min_sup)
                dest.append(frequent_items)

    @ staticmethod
    def __grow(fp_tree, dest, frequent_set=[]):
        """mine an FP Tree

        Args:
            fp_tree (FPTree): an object of FPTree
            dest (list): destination array where frequent itemsets are stored
            frequent_set (list, optional): potential frequent itemsets. Defaults to [].
        """
        if fp_tree.isSinglePathTree():
            FPTree.__grow_single_path_tree(fp_tree, dest, frequent_set)
        else:
            conditional_pattern_base = fp_tree.get_condition_pattern_base()
            for header in conditional_pattern_base:
                header_support = 0
                transactions = []
                for pattern in conditional_pattern_base[header]:
                    header_support += pattern.pop(0)[1]
                    transactions += itemfreq2transactions(pattern)

                tree = FPTree(fp_tree.min_sup)
                tree.buildTreeFromData(transactions)
                if not tree.isEmptyTree():
                    FPTree.__grow(tree, dest, [(item, header_support) for item,
                                               _ in frequent_set + [(header, header_support)]])
