import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from Helper import get_pearson, backgound_img



backgound_img()
engine = create_engine('sqlite:///E:\MAID\ADSA_pro\code\movielens_all.db', echo=False)

intro = st.container()
overview = st.container()
movies_search = st.container()
best_rated_movies = st.container()
recommendation = st.container()

@st.cache  #  to avoid reloading the table everytime
def call_table():
    popular_movies = pd.read_sql("SELECT * FROM popular_movies ",con=create_engine('sqlite:///E:\MAID\ADSA_pro\code\movielens_all.db', echo=False))

    return popular_movies
@st.cache  #  to avoid reloading the table everytime
def call_table2():
    movies_stats = pd.read_sql("SELECT * FROM movies_stats ",con=create_engine('sqlite:///E:\MAID\ADSA_pro\code\movielens_all.db', echo=False))

    return movies_stats

@st.cache  #  to avoid reloading the table everytime
def call_table3():
    movies_list = pd.read_sql("SELECT * FROM movies_list ",con=create_engine('sqlite:///E:\MAID\ADSA_pro\code\movielens_all.db', echo=False))
    movies_list.movieId = movies_list.movieId.astype(int)

    return movies_list

popular_movies = call_table()
movies_stats = call_table2()
movies_list = call_table3()


total_users = 162342





with intro:
    st.title("Movies Time")
    st.subheader("A project of Advanced Data Storage and Analysis subject at the University of South Bohemia. ")
    st.text(" By Manaf Ahmed\n")
    st.header("Overview:")
    st.subheader("This application utilizes the Movielens 25 Million dataset to create an easy access for the  users to:  ")
    st.text("1) View a list of movies.\n")
    st.text("2) Search for a movie by title or part of the title.\n")
    st.text("3) Search for the best rated films by genre.\n")





with overview:
    st.header("List of movies in our database:")
    st.text("There are more than 62,000 movies listed in our database (based on movie ID):  ")
    sel_col,disp_col = st.columns(2)
    paged_list = pd.read_sql("SELECT title,genres FROM movies_list",con=engine)

    gb = GridOptionsBuilder.from_dataframe(paged_list)
    gb.configure_pagination()
    gridOptions = gb.build()
    
    AgGrid(paged_list, gridOptions=gridOptions)


with movies_search:
    st.header("Looking for a specific movie?")
    sel_col1,disp_col1 = st.columns(2)
    search = sel_col1.text_input("write the full or partial movie name")
    st.write(pd.read_sql("SELECT movieId,title,genres,average FROM movies_stats where title like '%{}%'".format(search),con=engine))

with best_rated_movies:
    st.header("Top-rated movies by genre")
    sel_col2,disp_col2 = st.columns(2)
    select_genre = sel_col2.selectbox("Select genre from the drop down menu:",options=['Action','Adventure','Animation','Children','Comedy','Crime','Documentary','Drama','Fantasy','Film-Noir','Horror','Musical','Mystery','Romance','Sci-Fi','Thriller','War','Western','(no genres listed)'])
    st.text("Top 10 rated movies in {} are:".format(select_genre))
    depth = disp_col2.slider("select ow many movies do you want to view?",min_value=5,max_value=50,value=10,step=5)
    st.write(pd.read_sql("SELECT title,genres,average FROM movies_stats where genres like '%{}%' order by average desc".format(select_genre),con=engine).head(depth))
##########################################################


with recommendation:
    st.header("Recommendation System")
    st.subheader("Here we find users with a similar taste to a selected user (A), and accordingly suggest movies similar to his taste")

    col1,col2 = st.columns(2)
    recommend_userid = int ( col1.number_input("choose users between 1 and {}".format(total_users),min_value= 0 ,max_value=total_users)  )

    if recommend_userid != 0:
        # inputMovies = pd.read_sql("SELECT movieId,rating FROM popular_movies where userId =={}".format(recommend_userid),con=engine)
        
        #Filtering out the movies by movieId
        #Then merging it so we can get the movieId. It's implicitly merging it by title.
        inputMovies = popular_movies.loc[popular_movies['userId'] == recommend_userid]
        inputMovies = pd.merge(inputMovies, movies_list, how='inner', on=['movieId'])
        #Filtering out users that have watched movies that the input has watched and storing it
        userSubset = popular_movies[popular_movies['movieId'].isin(inputMovies['movieId'].tolist())]
        #Groupby creates several sub dataframes where they all have the same value in the column specified as the parameter
        userSubsetGroup = userSubset.groupby(['userId'])
        #Sorting it so users with movie most in common with the input will have priority
        userSubsetGroup = sorted(userSubsetGroup,  key=lambda x: len(x[1]), reverse=True)
        userSubsetGroup = userSubsetGroup[1:100]

        pearsonCorrelationDict = get_pearson(userSubsetGroup,inputMovies)
        pearsonDF = pd.DataFrame.from_dict(pearsonCorrelationDict, orient='index')
        pearsonDF.columns = ['similarityIndex']
        pearsonDF['userId'] = pearsonDF.index
        pearsonDF.drop(pearsonDF.index[0], inplace=True)
        pearsonDF.index = range(len(pearsonDF))
        similar_users = pearsonDF.head(5)
        
        topUsers=pearsonDF.sort_values(by='similarityIndex', ascending=False)[0:50]
        topUsers.reset_index(drop=True, inplace=True)
        #Getting  the most similar users to the selected user
        st.subheader("The most 5 similar users to you are:")
        st.table(topUsers.head(5))
        #Get the ratings of the selected users to their movies
        topUsersRating=topUsers.merge(popular_movies, left_on='userId', right_on='userId', how='inner')
        # multiply the movie rating by its weight and sum up new ratings then divide it by the sum of the weights (normalize the ratings).
        topUsersRating['weightedRating'] = topUsersRating['similarityIndex']*topUsersRating['rating']
        tempTopUsersRating = topUsersRating.groupby('movieId').sum()[['similarityIndex','weightedRating']]
        tempTopUsersRating.columns = ['sum_similarityIndex','sum_weightedRating']

        #Creates an empty dataframe
        recommendation_df = pd.DataFrame()
        #Now we take the weighted average
        recommendation_df['weighted average recommendation score'] = tempTopUsersRating['sum_weightedRating']/tempTopUsersRating['sum_similarityIndex']
        recommendation_df['movieId'] = tempTopUsersRating.index
        recommendation_df = recommendation_df.sort_values(by='weighted average recommendation score', ascending=False)
        recommendation_df = movies_list.loc[movies_list['movieId'].isin(recommendation_df.head(10)['movieId'].tolist())]
        # recommendation_df = movies_stats.loc[movies_stats['movieId'].isin(recommendation_df.head(10)['movieId'].tolist())]
        recommendation_df.reset_index(drop=True, inplace=True)
        recommendation_df = recommendation_df.drop(columns='index')
        st.subheader("Top 10 Recommended movies for you:")
        st.write(recommendation_df)

