import re
import pandas as pd


def preprocess(data):
    pattern = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y, %H:%M - ')
    df.rename(columns={'message_date': 'date'}, inplace=True)
    pattern2 = '([\w\W]+?):\s'
    df[['users', 'message']] = df.apply(lambda row: pd.Series(match_username(row, pattern2)), axis=1)
    df.drop(columns=['user_message'], inplace=True)
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['month_num'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['period'] = df.apply(lambda row: str(row.hour) + '-' + str('00') if row.hour == 23 else
                                        str('00') + '-' + str(row.hour + 1) if row.hour == 0 else
                                        str(row.hour) + '-' + str(row.hour + 1), axis=1)

    return df


def match_username(row, pattern):
    entry = re.split(pattern, row['user_message'])
    if entry[1:]:
        return entry[1], entry[2]
    else:
        return 'group_notification', entry[0]
