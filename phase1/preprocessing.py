import matplotlib.pyplot as plt
# nltk
import nltk
import numpy as np
import pandas as pd
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import *
from wordcloud import WordCloud

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('omw-1.4')


def save_statistical_features(temp_df: pd.DataFrame):
    course_count = temp_df[["Department", "Course title"]].groupby("Department").count()
    course_count["average"] = course_count.mean()["Course title"]
    course_count["ratio"] = course_count["Course title"] / course_count["average"]
    course_count.to_csv("../outputs/statistical_features.csv")
    course_count = course_count.sort_values("Course title")

    plt.bar(course_count.index.map(lambda x: x[:20]), course_count["Course title"])
    plt.xticks(rotation=90)
    plt.xlabel("department")
    plt.ylabel("course count")
    plt.tight_layout()
    plt.savefig("../outputs/course_count_bar_chart.png")
    plt.close()

    plt.hist(course_count["Course title"])
    plt.ylabel("department count")
    plt.xlabel("course count")
    plt.tight_layout()
    plt.savefig("../outputs/course_count_histogram.png")


def clean_data(temp_df: pd.DataFrame):
    temp_df = temp_df.copy()
    for col in temp_df.columns:
        # upper case to lower case
        temp_df[col] = temp_df[col].map(lambda x: x.lower())
        # remove number
        temp_df[col] = temp_df[col].map(lambda x: re.sub(r'\d+', '', x))
        # remove punctuation
        temp_df[col] = temp_df[col].map(lambda x: re.sub(r'[^a-zA-Z]', ' ', x))
        # remove whitespace
        temp_df[col] = temp_df[col].map(lambda x: x.strip())
        # remove url
        url_cleaner = 'http\S+'
        temp_df[col] = temp_df[col].map(lambda x: re.sub(url_cleaner, ' ', x))
        # removing short words
        temp_df[col] = temp_df[col].apply(lambda x: ' '.join([w for w in x.split() if len(w) > 3]))
    return temp_df


def tokenization(temp_df: pd.DataFrame):
    for col in temp_df.columns:
        temp_df[col] = temp_df[col].apply(lambda x: x.split())
    return temp_df


# Lemmatizing the words using WordNet
def lemmatizing(temp_df: pd.DataFrame):
    lemmatizer = WordNetLemmatizer()
    wordnet_map = {"N": wordnet.NOUN, "V": wordnet.VERB, "J": wordnet.ADJ, "R": wordnet.ADV}

    def lemmatize_words(text):
        pos_tagged_text = nltk.pos_tag(text)
        # pos_tagged_text = text.apply(lambda x: nltk.pos_tag(x))
        return [lemmatizer.lemmatize(word, wordnet_map.get(pos[0], wordnet.NOUN)) for word, pos in pos_tagged_text]

    for col in temp_df.columns:
        temp_df[col] = temp_df[col].apply(lambda text: lemmatize_words(text))
    return temp_df


# stemming
def stemming(temp_df: pd.DataFrame):
    stemmer = PorterStemmer()
    for col in temp_df.columns:
        temp_df[col] = temp_df[col].apply(lambda x: [stemmer.stem(i) for i in x])
    return temp_df


# Removing stop words
def remove_stop_word(temp_df: pd.DataFrame):
    stop_words = set(stopwords.words('english'))
    for col in temp_df.columns:
        temp_df[col] = temp_df[col].apply(lambda text: [word for word in text if word not in stop_words])
    return temp_df


def visualise(input_list, index):
    sentences = ' '.join(input_list)
    wordcloud = WordCloud(width=800, height=500, random_state=21, max_font_size=110).generate(sentences)
    plt.figure(figsize=(10, 7))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    plt.savefig(f"../outputs/word_cloud_{index}.png")


def read_file():
    temp_df = pd.read_csv("../datasets/GLA.csv")
    # dropping nan columns
    temp_df = temp_df.drop(columns=["Professor Homepage", "Projects", "Scores",
                                    "References", "Prerequisite", "Professor", "Unit"])
    # dropping useless columns
    temp_df = temp_df.drop(columns=["University", "Abbreviation", "University Homepage", "Course Homepage"])
    # dropping nan rows
    temp_df = temp_df.dropna()
    return temp_df


def main():
    temp_df = read_file()
    save_statistical_features(temp_df)
    # selecting useful columns
    temp_df = temp_df[['Objective', 'Outcome', 'Description']]
    # preprocessing texts
    temp_df = clean_data(temp_df)
    temp_df = tokenization(temp_df)
    temp_df = remove_stop_word(temp_df)
    temp_df = stemming(temp_df)
    temp_df = lemmatizing(temp_df)
    temp_df["words"] = temp_df["Objective"] + temp_df["Outcome"] + temp_df["Description"]
    temp_df = temp_df[["words"]]
    for index in np.random.choice(temp_df.shape[0], 5, replace=False):
        visualise(temp_df['words'][index], index)
    temp_df.to_pickle("../datasets/clean_GLA.pkl")


if __name__ == '__main__':
    main()
