import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori


def read_file():
    temp_df = pd.read_csv("../datasets/keyword_GLA.csv")
    temp_df["keywords"] = temp_df["keywords"].apply(lambda x: x[2:-2].split("', '"))
    return temp_df


def main():
    temp_df = read_file()
    temp_array = temp_df["keywords"].to_list()
    te = TransactionEncoder()
    temp_array = te.fit(temp_array).transform(temp_array)
    df = pd.DataFrame(temp_array, columns=te.columns_)
    frequent_itemsets = apriori(df, min_support=0.1, use_colnames=True)
    frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(lambda x: len(x))
    frequent_itemsets.to_csv("../datasets/result.csv", index=False)


if __name__ == '__main__':
    main()
