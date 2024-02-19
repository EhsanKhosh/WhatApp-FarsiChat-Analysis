import re
import pandas as pd
from urlextract import URLExtract
from persian_wordcloud.wordcloud import PersianWordCloud, add_stop_words
from collections import Counter
from typing import List
import emoji

extractor = URLExtract()


def fetch_stats(selected_user, df):
    df = filter_users(df, selected_user)

    num_messages = df.shape[0]
    words = df.apply(lambda row: re.findall(r'\w+', row['message']), axis=1)
    all_words = words.explode().tolist()
    num_of_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    links = df.apply(lambda row: extractor.find_urls(row['message']), axis=1)
    links = links.explode().dropna().tolist()

    return num_messages, len(all_words), num_of_media_messages, len(links)


def most_busy_users(df):
    x = df['users'].value_counts().head()
    df = round((df['users'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'count': 'percent'})
    return x, df


def create_wordcloud(df, selected_user):
    df = filter_users(df, selected_user)
    temp = filter_unused_messages(df)

    stopwords = read_stop_words('persian_stop_words.txt')
    filtered_words = remove_stopwords(temp, stopwords)

    wc = PersianWordCloud(only_persian=True,
                          width=500,
                          height=500,
                          min_font_size=4,
                          collocations=False,
                          )

    df_wc = wc.generate(filtered_words.str.cat(sep=' '))
    return df_wc


def most_common_words(df, selected_user):
    df = filter_users(df, selected_user)
    temp = filter_unused_messages(df)
    stopwords = read_stop_words('persian_stop_words.txt')
    filtered_words = remove_stopwords(temp, stopwords)
    most_common_df = pd.DataFrame(Counter(filtered_words).most_common(20))
    return most_common_df


def filter_users(df, selected_user):
    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

    return df


def filter_unused_messages(df):
    temp = df[df['users'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    temp = temp[temp['message'] != 'This message was deleted\n']

    return temp


def read_stop_words(stopwords_file: str = None, stopwords_list: List = []):
    stopwords = []
    if stopwords_file:
        f_sw = open(stopwords_file, 'r', encoding='utf-8')
        data_sw = f_sw.read()
        stopwords = data_sw.split()

    if stopwords_list:
        stopwords.extend(stopwords_list)

    return stopwords


def remove_stopwords(df, stopwords_list: List):
    words = df.apply(lambda row: row['message'].split(), axis=1)
    filtered_words = words.explode().reset_index(drop=True)
    filtered_words = filtered_words.apply(lambda row: row if row not in stopwords_list else None).dropna()

    return filtered_words


def emoji_helper(df, selected_user):
    df = filter_users(df, selected_user)
    emojis = df.apply(lambda row: [c for c in row['message'] if emoji.is_emoji(c)], axis=1)
    emojis = emojis.explode().dropna().reset_index(drop=True)
    emojis_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emojis_df


def emoji_chart_helper(emoji_df):
    top_5 = emoji_df[1][:5]
    top_5_emoji = emoji_df[0][:5]
    top_5_sum = emoji_df[1].head().sum()
    total_sum = emoji_df[1].sum()
    others_sum = total_sum - top_5_sum
    percentages_top_5 = [(value / total_sum) * 100 for value in top_5]
    percentage_others = (others_sum / total_sum) * 100

    top_5_emoji.loc[len(top_5_emoji)] = 'others'
    return_df = pd.DataFrame({'emoji': top_5_emoji, 'percentage': percentages_top_5 + [percentage_others]})

    return return_df


def monthly_timeline(df, selected_user):
    df = filter_users(df, selected_user)
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    timeline['time'] = timeline.apply(lambda row: row.month + '-' + str(row.year), axis=1)

    return timeline


def daily_timeline(df, selected_user):
    df = filter_users(df, selected_user)
    d_timeline = df.groupby('only_date').count()['message'].reset_index()

    return d_timeline


def weekday_activity_map(df, selected_user):
    df = filter_users(df, selected_user)
    return df['day_name'].value_counts()


def month_activity_map(df, selected_user):
    df = filter_users(df, selected_user)
    return df['month'].value_counts()


def activity_heatmap(df, selected_user):
    df = filter_users(df, selected_user)
    return df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
