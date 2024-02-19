import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display
from matplotlib.font_manager import FontProperties
import seaborn as sns

prop = FontProperties(fname='/home/ehsan/PycharmProjects/WhatApp_chat_analysis/Fonts/NotoColorEmoji.ttf')
plt.rcParams['font.family'] = prop.get_family()

st.sidebar.title("WhatApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode('utf-8')
    df = preprocessor.preprocess(data)

    user_list = df['users'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show analysis"):
        num_messages, words, num_media_msg, num_links = helper.fetch_stats(selected_user, df)

        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)

        with col2:
            st.header("Total Words")
            st.title(words)

        with col3:
            st.header("Media Shared")
            st.title(num_media_msg)

        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(df, selected_user)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'])
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # daily timeline
        st.title("Daily Timeline")
        d_timeline = helper.daily_timeline(df, selected_user)
        fig, ax = plt.subplots()
        ax.plot(d_timeline['only_date'], d_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # activity map
        st.title('Activity Map')
        col1, col2 = st.columns(2)

        with col1:
            st.header('Most Busy Day')
            busy_day = helper.weekday_activity_map(df, selected_user)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values)

            st.pyplot(fig)

        with col2:
            st.header('Most Busy Month')
            busy_month = helper.month_activity_map(df, selected_user)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # activity hourly period heatmap
        st.title('Hourly Activity Heatmap')
        heatmap = helper.activity_heatmap(df, selected_user)
        fig = plt.figure(figsize=(20, 6))
        sns.heatmap(heatmap)
        st.pyplot(fig)

        if selected_user == 'Overall':
            st.title('Most Busy User')
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots(figsize=(18, 10))
            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values, color='green')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)

        # WordCloud
        st.title("Word Distribution")
        df_wc = helper.create_wordcloud(df, selected_user)
        fig, ax = plt.subplots()
        plt.imshow(df_wc)
        st.pyplot(fig)

        # Most common words
        st.title("Most Common Words")
        most_common_words = helper.most_common_words(df, selected_user)

        fig, ax = plt.subplots()
        # for persian word we should reshape them to bidirectional string and then split it
        reshaped_text = arabic_reshaper.reshape(most_common_words[0].str.cat(sep=' '))
        bidi_text = get_display(reshaped_text)
        ax.barh(bidi_text.split()[::-1], most_common_words[1], color='red')

        st.pyplot(fig)
        st.dataframe(most_common_words)

        # emoji analysis
        emoji_df = helper.emoji_helper(df, selected_user)
        st.title('Emoji Analysis')
        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)
        with col2:
            emoji_pct_df = helper.emoji_chart_helper(emoji_df)
            fig, ax = plt.subplots()

            ax.pie(emoji_pct_df['percentage'], labels=emoji_pct_df['emoji'], autopct='%.2f')
            st.pyplot(fig)
