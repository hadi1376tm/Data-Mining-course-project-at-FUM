import pandas as pd
from keybert import KeyBERT


def read_file():
    temp_df = pd.read_pickle("../datasets/clean_GLA.pkl")
    return temp_df


def main():
    temp_df = read_file()
    kw_model = KeyBERT()
    temp_df["sentences"] = temp_df["words"].apply(lambda x: " ".join(x))
    temp_df["keywords"] = temp_df["sentences"].apply(kw_model.extract_keywords)
    temp_df["keywords"] = temp_df["keywords"].apply(lambda x: [y[0] for y in x])
    temp_df[['keywords']].to_csv("./drive/MyDrive/keyword_GLA.csv", index=False)


if __name__ == '__main__':
    main()
