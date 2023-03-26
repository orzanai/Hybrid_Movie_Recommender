
#############################################
# Business Problem
#############################################

# Make predictions using item-based and user-based recommender methods for the user with the given ID.
# Consider 5 recommendations from the user-based model and 5 recommendations from the item-based model,
# and ultimately provide 10 recommendations from both models.


#############################################
# Data Preperation
#############################################
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.expand_frame_repr', False)


movie_df = pd.read_csv("/Case Studies/HybridRecommender-221114-235254/datasets/movie.csv")

rating_df = pd.read_csv("/Case Studies/HybridRecommender-221114-235254/datasets/rating.csv")

merged_df = rating_df.merge(movie_df, on="movieId", how = "left")

# Calculating total rating of movies and drop rare movies for efficiency and accuracy

rating_count = merged_df.groupby("title").agg({"rating":"count"})
rating_count.reset_index(inplace=True)

rare_movies = rating_count[rating_count["rating"] <= 1000]["title"]
common_movies = merged_df[~merged_df["title"].isin(rare_movies)]

# creating user_movie_df

user_movie_df = common_movies.pivot_table(index=["userId"], columns=["title"], values="rating")

# function for directly create user-movie dataframe

def create_user_movie_df():
    movie_df = pd.read_csv("/Case Studies/HybridRecommender-221114-235254/datasets/movie.csv")
    rating_df = pd.read_csv("/Case Studies/HybridRecommender-221114-235254/datasets/rating.csv")
    merged_df = movie_df.merge(rating_df, how=left, on="movieId")
    rating_count = merged_df.groupby("title").agg({"rating":"count"})
    rare_movies = merged_df[merged_df["count"] < 1000]
    common_movies = merged_df[~df["title"].isin(rare_movies)]
    user_movie_df = common_movies.pivot_table(index=["userId"], columns=["title"], values="rating")
    return user_movie_df

#############################################
# Determining the movies watched by the user to whom recommendations will be made.
#############################################

# creating random user for testing

random_user = int(pd.Series(user_movie_df.index).sample(1, random_state=45).values)

# creating a new dataframe called random_user_df consisting of observation units belonging to the selected user

random_user_df = user_movie_df[user_movie_df.index == random_user]

# creating movies_watched list that consist of ratings of the selected user

movies_watched = random_user_df.columns[random_user_df.any().notna()].tolist()

#############################################
# Accessing the data and IDs of other users who have watched the same movies
#############################################

movies_watched_df = user_movie_df[movies_watched]

# we are creating a new dataframe called user_movie_count that contains information on
# how many of the selected user's watched movies each user has watched.

user_movie_count = movies_watched_df.T.notnull().sum()
user_movie_count = user_movie_count.reset_index()

# we consider users who have watched 60% or more of the movies rated by the selected user as similar users

user_movie_count.columns= ["userid", "movie_count"]
perc = len(movies_watched)*60/100
user_same_movies = user_movie_count[user_movie_count["movie_count"] >= perc]["userid"]

#############################################
# Determining the most similar users to the user for whom recommendations will be made
#############################################

final_df = pd.concat([movies_watched_df[movies_watched_df.index.isin(user_same_movies)],
                     random_user_df[movies_watched]])

# creating correlation dataframe

corr_df = final_df.T.corr().unstack().sort_values().drop_duplicates()
corr_df = pd.DataFrame(corr_df, columns=["corr"])
corr_df.index.names = ["user_id_1", "user_id_2"]
corr_df.reset_index(inplace=True)


top_users = corr_df[(corr_df["user_id_1"] == random_user) & (corr_df["corr"] > 0.65)]
top_users.sort_values("corr", ascending=False)

top_users.rename(columns={"user_id_2": "userId"}, inplace=True)
top_users_rating = top_users.merge(rating[["userId", "movieId", "rating"]], how='inner')

#############################################
# calculation of Weighted Average Recommendation Score and selection of the top 5 recommended movies
#############################################


top_users_rating["weighted_rating"] = top_users_rating["rating"] * top_users_rating["corr"]

recommendation_df = top_users_rating.groupby("movieId").agg({"weighted_rating":"mean"})
recommendation_df.reset_index(inplace=True)


movies_to_be_recommend = recommendation_df[recommendation_df["weighted_rating"] > 3.5].sort_values("weighted_rating", ascending=False).head()

# title of the five movies that we will recommend

movies_to_be_recommend.merge(movie_df[["movieId","title"]])["title"].head()


#############################################
# Item-Based Recommendation
#############################################

user = 108170

movie = pd.read_csv("/Case Studies/HybridRecommender-221114-235254/datasets/movie.csv")

rating = pd.read_csv("/Case Studies/HybridRecommender-221114-235254/datasets/rating.csv")


movie_id = merged_df.loc[(merged_df["userId"] == 108170) & (merged_df["rating"] == 5), ["movieId","timestamp"]].sort_values(by="timestamp", ascending=False).iloc[0,0]


movie[movie["movieId"] == movie_id]["title"].values[0]
movie_df = user_movie_df[movie[movie["movieId"] == movie_id]["title"].values[0]]


user_movie_df.corrwith(movie_df).sort_values(ascending=False).head(10)

# create five recommendations

user_movie_df.corrwith(movie_df).sort_values(ascending=False)[1:6].index
movies_from_item_based = item_based_recommender(movie[movie["movieId"] == movie_id]["title"].values[0], user_movie_df)
movie_df = user_movie_df[movie[movie["movieId"] == movie_id]["title"].values[0]]

def item_based_recommender(movie_name, user_movie_df):
    movie = user_movie_df[movie_name]
    return user_movie_df.corrwith(movie).sort_values(ascending=False).head(10)
    
item_based_recs = item_based_recommender(movie[movie["movieId"] == movie_id]["title"].values[0], user_movie_df)
item_based_recs[1:6].index
