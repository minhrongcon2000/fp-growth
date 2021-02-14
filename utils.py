from collections import Counter


def itemfreq2transactions(item_freq):
    """convert conditional pattern base to pattern set

    Args:
        item_freq (list): conditional pattern base

    Returns:
        list: pattern set
    """
    return [list(map(lambda item: item[0], item_freq)) for i in range(item_freq[0][1])]


def get_sorted_frequent_item_from_data(transactions, min_sup):
    """an item is frequent if and only if 
    the number of transactions containing that item is greater than min_sup

    Args:
        transactions (list): list of transactions
        min_sup (int): the minimum threshhold for a frequent item

    Returns:
        dict: a dictionary whose keys are items and values are their frequency
    """
    item2freq = Counter()
    for transaction in transactions:
        for item in transaction:
            item2freq[item] += 1

    item2freq_list = [(item, item2freq[item])
                      for item in item2freq if item2freq[item] >= min_sup]
    item2freq_list.sort(key=lambda item: item[1], reverse=True)
    item2index = [(item2freq_list[i][0], i)
                  for i in range(len(item2freq_list))]
    return dict(item2index)
