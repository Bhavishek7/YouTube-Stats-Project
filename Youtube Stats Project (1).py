#!/usr/bin/env python
# coding: utf-8

# # Data Cleaning
# 
# ### Importing Libraries

# In[1]:


import numpy as np
import re
import pandas as pd
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
import seaborn as sns
from matplotlib import cm
from datetime import datetime
import glob
import os
import json
import pickle
import six
sns.set()
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.options.mode.chained_assignment = None


# ###  Importing all CSV files

# In[3]:


path = r"C:\Users\BHAVISHEK\Downloads\archive (1)"
extension = 'csv'
os.chdir(r"C:\Users\BHAVISHEK\Downloads\archive (1)")
result = glob.glob('*.{}'.format('csv'))
print(result)


# ###  Reading all CSV Files

# In[4]:


all_dataframes = [] # list to store each data frame separately
for csv in result:
    df = pd.read_csv(csv)
    df['country'] = csv[0:2] # adding column 'country' so that each dataset could be identified uniquely
    all_dataframes.append(df)
all_dataframes[0].head() # index 0 to 9 for [CA, DE, FR, GB, IN, JP, KR, MX, RU, US] datasets


# ### Fixing Datatypes

# In[5]:


for df in all_dataframes:
    # video_id 
    df['video_id'] = df['video_id'].astype('str') 
    
    # trending date 
    df['trending_date'] = df['trending_date'].astype('str') 
    date_pieces = (df['trending_date']
                   .str.split('T')
                  )
    df['DATE1'] = date_pieces.str[0].astype(str)
    df['DATE2'] = date_pieces.str[1].astype(str)   
    
    #title
    df['title'] = df['title'].astype('str')
    #channel_title
    df['channelTitle'] = df['channelTitle'].astype('str')
    #category_id
    df['categoryId'] = df['categoryId'].astype(str) 
    
    #tags
    df['tags'] = df['tags'].astype('str')
    
    # views, likes, dislikes, comment_count are already in correct data types i.e int64
    
    #thumbnail_link
    df['thumbnail_link'] = df['thumbnail_link'].astype('str') 
    
    #description
    df['description'] = df['description'].astype('str')
    
    # Changing comments_disabled, ratings_disabled, video_error_or_removed from bool to categorical
    df['comments_disabled'] = df['comments_disabled'].astype('category') 
    df['ratings_disabled'] = df['ratings_disabled'].astype('category') 
    
    # publish_time 
    df['publishedAt']=df['publishedAt'].astype('str')
    
    published_pieces=(df['publishedAt'].str.split('T'))
    
    df['Published_Date']=published_pieces.str[0].astype(str)
    df['Published_Time']=published_pieces.str[1].astype(str)
    df['Published_Date'] = pd.to_datetime(df['Published_Date'], errors='coerce', format='%Y-%m-%d')


# In[6]:


# We can use any index from 0 to 9 inclusive (for each of the 10 dataframes
all_dataframes[1].dtypes


# In[7]:


for df in all_dataframes:
    df.set_index('video_id', inplace=True)


# ### Examining Missing Values

# In[8]:


for df in all_dataframes:
    sns.heatmap(df.isnull(), cbar=False)
    plt.figure()


# ### Combining Every Dataframe Into One Huge Dataframe
# 

# In[9]:


combined_df = pd.concat(all_dataframes)


# In[10]:


# Making copy of original dataframe
backup_df = combined_df.reset_index().sort_values('trending_date', ascending=False).set_index('video_id')
# Sorting according to latest trending date while removing duplicates
combined_df = combined_df.reset_index().sort_values('trending_date', ascending=False).drop_duplicates('video_id',keep='first').set_index('video_id')
# Doing the same above operation for each of the individual dataframes in the list we created earlier
for df in all_dataframes:
    df = df.reset_index().sort_values('trending_date', ascending=False).set_index('video_id')
# Printing results
combined_df[['Published_Date','Published_Time','DATE1', 'country']].head()
# It can be seen that latest publications and trending information is at the top now


# In[11]:


categoryId = {}
with open(r"C:\Users\BHAVISHEK\Downloads\archive (1)\DE_category_id.json", 'r') as f:
    d = json.load(f)
    for category in d['items']:
        categoryId[category['id']] = category['snippet']['title']
combined_df.insert(2, 'category', combined_df['categoryId'].map(categoryId))
backup_df.insert(2, 'category', backup_df['categoryId'].map(categoryId))
for df in all_dataframes:
    df.insert(2, 'category', df['categoryId'].map(categoryId))
# Printing cleaned combined dataframe
combined_df.head(3)


# In[12]:


combined_df['category'].unique()


# # Exploratory Data Analysis
# 
# ### Ratio of likes-dislikes in different categories

# In[13]:


# calculating total likes for each category
likesdf = combined_df.groupby('category')['likes'].agg('sum')
# calculating total dislikes for each category
dislikesdf = combined_df.groupby('category')['dislikes'].agg('sum')
# calculating ratios of likes to dislikes
ratiodf = likesdf/dislikesdf 
# most liked category to appear on top
ratiodf = ratiodf.sort_values(ascending=False).reset_index()
# plotting bar chart
ratiodf.columns = ['category','ratio']
plt.subplots(figsize=(10, 15))
sns.barplot(x="ratio", y="category", data=ratiodf,
            label="Likes-Dislikes Ratio", color="b")


# ## Observations:
# We see that videos belonging to the pets and animals categories have the highest ratio of likes to dislikes videos among the trending categories whereas new and politics videos have the least. From this we can infer that people are less divided on the content of videos based on entertainment than compared to topics such as new, whose content can lead to a division of opinions among the user.
# 

# ### Users like videos from which category more?

# In[14]:


# Getting names of all countries
countries = []
result = [i for i in glob.glob('*.{}'.format('csv'))]
for csv in result:
    c = csv[0:2]
    countries.append(c)
for country in countries:
    if country == 'US':
        tempdf = combined_df[combined_df['country']==country]['category'].value_counts().reset_index()
        ax = sns.barplot(y=tempdf['index'], x=tempdf['category'], data=tempdf, orient='h')
        plt.xlabel("Number of Videos")
        plt.ylabel("Categories")
        plt.title("Catogories of trend videos in " + country)
    else:
        tempdf = combined_df[combined_df['country']==country]['category'].value_counts().reset_index()
        ax = sns.barplot(y=tempdf['index'], x=tempdf['category'], data=tempdf, orient='h')
        plt.xlabel("Number of Videos")
        plt.ylabel("Categories")
        plt.title("Catogories of trend videos in " + country)
        plt.figure()


# ## Observations
# Apart from RU and GB, category most liked by the users in each of the other countries is ‘Entertainment’.
# Viewers from RU prefer the category ‘People and Blogs’ the most.
# Viewers from GB prefer the category ‘Sports’ the most.
# Categories ‘Pets & Animals’, ‘Travel & Events’ were the least liked ones in almost all of the countries.

# ### Top 5 videos that are on trending in each country?

# In[15]:


temporary = []
for df in all_dataframes:
    temp = df
    temp = temp.reset_index().sort_values(by = ['view_count'], ascending=False)
    temp.drop_duplicates(subset ="video_id", keep = 'first', inplace = True)
    temp.set_index('video_id', inplace=True)
    temp = temp.head(5) # top 5 that are on trending
    temporary.append(temp)
# Printing 3 randomly selected countries
temporary[3][['title', 'channelTitle', 'category', 'view_count', 'likes']]


# In[16]:


temporary[5][['title', 'channelTitle', 'category', 'view_count', 'likes']]


# In[17]:


temporary[1][['title', 'channelTitle', 'category', 'view_count', 'likes']]


# ## Observations
# Users from every country mostly prefer videos belonging to the categories of ‘Music’ and ‘Entertainment’, potentially meaning users usually use the platform for recreational purposes in comparisons to other uses.

# ### Is the most liked video also the most trending video?

# In[18]:


temporary = [] # to store results for each country
for df in all_dataframes:
    temp = df
    temp = temp.reset_index().sort_values(by = ['likes'], ascending=False)
    temp.drop_duplicates(subset ="video_id", keep = 'first', inplace = True)
    temp.set_index('video_id', inplace=True)
    temp = temp.head(5) # top 5 that are most liked
    temporary.append(temp)
# Printing 3 randomly selected results
temporary[3][['view_count', 'likes']]


# In[19]:


temporary[5][['view_count', 'likes']]


# In[20]:


temporary[1][['view_count', 'likes']]


# ## Observation
# We can see that the most liked videos in different countries are also the videos with the most view count

# ### Users like videos from which category more?

# In[21]:


temp = combined_df
temp = temp.groupby('category')['view_count', 'likes'].apply(lambda x: x.astype(int).sum())
temp = temp.sort_values(by='likes', ascending=False).head()
temp


# ## Observation
# As we can see, most liked category is ‘Entertainment’ for all countries. This shows user preference to use YouTube as an entertainment platform.

# ### Users comment on which category the most?

# In[22]:


temp = combined_df
temp = temp.groupby('category')['view_count','likes', 'comment_count'].apply(lambda x: x.astype(int).sum())
temp = temp.sort_values(by='comment_count', ascending=False).head()
temp


# ## Observation
# As we can see, 'Music' and 'Entertainment' category videos have the highest comment_count and also likes. This shows user preference to use YouTube as an entertainment platform.

# ### Correlation between views, likes, dislikes, and comments

# In[24]:


col = ['view_count', 'likes', 'dislikes', 'comment_count']
corr = combined_df[col].corr()
corr


# ## Observation
# When evaluating the correlation between all the variables, the correlation of each feature with itself is also included, which is always 1
# 
# We can see from the results, there is a positive relation between views and likes, likes and comment_count, dislikes and comment_count. We came to this conclusion as anytime the correlation coefficient, denoted as corr, is greater than zero, it’s a positive relationship.
# 

# # Conclusion
# 
# In conclusion, the statistics gathered and analyzed throughout this YouTube project provide valuable insights into the platform's dynamics, trends, and user behaviors. Through meticulous data collection and comprehensive analysis, we have gained a deeper understanding of the factors that contribute to a video's success, the preferences of YouTube viewers, and the strategies employed by successful content creators.

# In[ ]:




