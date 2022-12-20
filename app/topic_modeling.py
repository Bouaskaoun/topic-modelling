import base64
import numpy as np
import pandas as pd
from app.models import Data
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
import matplotlib.pyplot as plt
from sklearn.decomposition import TruncatedSVD
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.manifold import TSNE
import seaborn as sns
import nltk
try:
    nltk.download('all', quiet=True)
except:
    raise Exception("Couldn't download, nltk data")
sns.set_style('darkgrid')
sns.set_palette('muted')
sns.set_context("notebook", font_scale=1.5,
                rc={"lines.linewidth": 2.5})
colormaps = np.array([
    "#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c",
    "#98df8a", "#d62728", "#ff9896", "#9467bd", "#c5b0d5",
    "#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7f7f7f",
    "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5" ])
def fig2img(fig):
    import io
    buf = io.BytesIO()
    fig.savefig(buf)
    img_str = base64.b64encode(buf.getvalue())
    return img_str.decode()

def get_top_n_words(n_top_words, text_data:pd.Series):
    count_vectorizer = CountVectorizer(stop_words='english')
    vectorized_headlines = count_vectorizer.fit_transform(text_data)
    vectorized_total = np.sum(vectorized_headlines, axis=0)
    word_indices = np.flip(np.argsort(vectorized_total)[0,:], 1)
    word_values = np.flip(np.sort(vectorized_total)[0,:],1)
    
    word_vectors = np.zeros((n_top_words, vectorized_headlines.shape[1]))
    for i in range(n_top_words):
        word_vectors[i,word_indices[0,i]] = 1

    words = [word[0].encode('ascii').decode('utf-8') for 
             word in count_vectorizer.inverse_transform(word_vectors)]
 
    return (words, word_values[0,:n_top_words].tolist()[0])
def get_initial_report(top_n_words,data:Data,raw=True):
    if raw:
        text_col=data.raw_data_file.loc[:,data.text_column]
    else:
        text_col=data.clean_data_file.loc[:,data.text_column]
    text_col=text_col.fillna(' ')
    words, word_values = get_top_n_words(
        n_top_words=top_n_words,
        text_data=text_col
    )
    fig, ax = plt.subplots(figsize=(16,8))
    ax.bar(range(len(words)), word_values)
    ax.set_xticks(range(len(words)))
    ax.set_xticklabels(words, rotation='vertical')
    ax.set_title('Top 20 words in headlines')
    ax.set_xlabel('Word')
    ax.set_ylabel('Number of occurences')
    top_words_plot=fig2img(fig)
    return {
            "words":words,
            "values":word_values,
            "plot":top_words_plot,
        }
# Define helper functions
def get_mean_topic_vectors(keys, two_dim_vectors, n_topics):
    '''
    returns a list of centroid vectors from each predicted topic category
    '''
    mean_topic_vectors = []
    for t in range(n_topics):
        articles_in_that_topic = []
        for i in range(len(keys)):
            if keys[i] == t:
                articles_in_that_topic.append(two_dim_vectors[i])    
        
        articles_in_that_topic = np.vstack(articles_in_that_topic)
        mean_article_in_that_topic = np.mean(articles_in_that_topic, axis=0)
        mean_topic_vectors.append(mean_article_in_that_topic)
    return mean_topic_vectors
def get_keys(topic_matrix):
    '''
    returns an integer list of predicted topic 
    categories for a given topic matrix
    '''
    keys = topic_matrix.argmax(axis=1).tolist()
    return keys

def keys_to_counts(keys):
    '''
    returns a tuple of topic categories and their 
    accompanying magnitudes for a given list of keys
    '''
    count_pairs = Counter(keys).items()
    categories = [pair[0] for pair in count_pairs]
    counts = [pair[1] for pair in count_pairs]
    return (categories, counts)
def preprocessing(text_data:pd.Series,samples_length:int):
    text_data=text_data.fillna(' ')
    small_count_vectorizer = CountVectorizer(stop_words='english', max_features=40000)
    small_text_sample=None
    if samples_length==0:
        small_text_sample=text_data
    else:
        small_text_sample = text_data.sample(n=samples_length, random_state=0).values
    small_document_term_matrix = small_count_vectorizer.fit_transform(small_text_sample)
    return small_count_vectorizer,small_document_term_matrix
def get_top_n_words_vectorized(n, keys, document_term_matrix, count_vectorizer,n_topics):
    '''
    returns a list of n_topic strings, where each string contains the n most common 
    words in a predicted category, in order
    '''
    top_word_indices = []
    for topic in range(n_topics):
        temp_vector_sum = 0
        for i in range(len(keys)):
            if keys[i] == topic:
                temp_vector_sum += document_term_matrix[i]
        temp_vector_sum = temp_vector_sum.toarray()
        top_n_word_indices = np.flip(np.argsort(temp_vector_sum)[0][-n:],0)
        top_word_indices.append(top_n_word_indices)   
    top_words = []
    for topic in top_word_indices:
        topic_words = []
        for index in topic:
            temp_word_vector = np.zeros((1,document_term_matrix.shape[1]))
            temp_word_vector[:,index] = 1
            the_word = count_vectorizer.inverse_transform(temp_word_vector)[0][0]
            topic_words.append(the_word.encode('ascii').decode('utf-8'))
        top_words.append(" ".join(topic_words))         
    return top_words
def generate_report(data:Data,n_topics,method:str,samples_length:int):
    data.get_clean_data()
    text_data=data.clean_data_file.loc[:,data.text_column]
    small_count_vectorizer,small_document_term_matrix=preprocessing(text_data,samples_length)
    model,topic_matrix=None,None
    if method.lower()=='lsa':
        model = TruncatedSVD(n_components=n_topics)
        topic_matrix = model.fit_transform(small_document_term_matrix)
    elif method.lower()=='lda':
        model = LatentDirichletAllocation(n_components=n_topics, learning_method='online',random_state=0, verbose=0)
        topic_matrix = model.fit_transform(small_document_term_matrix)
    keys = get_keys(topic_matrix)
    categories, counts = keys_to_counts(keys)
    top_10_words = get_top_n_words_vectorized(10, keys, small_document_term_matrix, small_count_vectorizer,n_topics)
    topics_words=[]
    for i in range(len(top_10_words)):
        topics_words.append( [f"Topic {i+1}: " ,top_10_words[i].split(' ')] )
    top_3_words = get_top_n_words_vectorized(3, keys, small_document_term_matrix, small_count_vectorizer,n_topics)
    labels = ['Topic {}: \n'.format(i+1) + top_3_words[i] for i in categories]
    try:
        fig, ax = plt.subplots(figsize=(16,8))
    except:
        fig, ax = plt.subplots(figsize=(16,8))
    ax.bar(categories, counts)
    ax.set_xticks(categories)
    ax.set_xticklabels(labels)
    ax.set_title( method.upper()+' topic counts')
    ax.set_ylabel('Number of headlines')
    topic_counts_plot=fig2img(fig)
    fig, ax = plt.subplots(figsize=(16,8))
    tsne_model = TSNE(n_components=2, perplexity=50, learning_rate=100,n_iter=2000, verbose=1, random_state=0, angle=0.75)
    tsne_vectors = tsne_model.fit_transform(topic_matrix)
    #top_3_words
    mean_topic_vectors = get_mean_topic_vectors(keys, tsne_vectors,n_topics)
    a=sns.scatterplot(x=tsne_vectors[:,0], y=tsne_vectors[:,1], hue=keys,palette=sns.color_palette("hls", n_topics),data=tsne_vectors)
    for t in range(n_topics):
        plt.text(mean_topic_vectors[t][0],mean_topic_vectors[t][1]-0.2, top_3_words[t],horizontalalignment='left', size='medium',)
    a.set(title="data T-SNE projection")
    fig = a.get_figure()
    tsne_plot=fig2img(fig)
    return {"topic_words":top_10_words,"plot":topic_counts_plot,"tsne":tsne_plot}