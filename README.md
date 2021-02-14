# fp-growth
implement FP-growth for frequent data mining

## Dependencies
No dependencies are needed, except Python!

## Usage

Example code is shown here!

```python
from fp_growth import FPTree
transactions = loadDataset() # load your dataset
tree = FPTree(min_sup=3) # min_sup means minimum support. This can be customized for your problem
tree.buildTreeFromData(transactions)

print(tree.grow()) # this will print frequent itemsets
```

## References
[1] Han, Jiawei, Jian Pei, and Yiwen Yin. "Mining frequent patterns without candidate generation." ACM sigmod record 29.2 (2000): 1-12.
