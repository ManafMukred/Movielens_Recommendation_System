from math import sqrt
import streamlit as st


def get_pearson(subset,movies):
    pearsonCorrelationDict = {}

    #For every user group in our subset
    for ID, group in subset:
        #Let's start by sorting the input and current user group so the values aren't mixed up later on
        group = group.sort_values(by='movieId')
        inputMovies = movies.sort_values(by='movieId')
        #Get the N for the formula
        nRatings = len(group)
        #Get the review scores for the movies that they both have in common
        temp_df = inputMovies[inputMovies['movieId'].isin(group['movieId'].tolist())]
        #store them in a temporary buffer variable in a list format to facilitate future calculations
        tempRatingList = temp_df['rating'].tolist()
        #Let's also put the current user group reviews in a list format
        tempGroupList = group['rating'].tolist()
        #Now let's calculate the pearson correlation between two users, so called, x and y
        Sxx = sum([i**2 for i in tempRatingList]) - pow(sum(tempRatingList),2)/float(nRatings)
        Syy = sum([i**2 for i in tempGroupList]) - pow(sum(tempGroupList),2)/float(nRatings)
        Sxy = sum( i*j for i, j in zip(tempRatingList, tempGroupList)) - sum(tempRatingList)*sum(tempGroupList)/float(nRatings)
        
        #If the denominator is different than zero, then divide, else, 0 correlation.
        if Sxx != 0 and Syy != 0:
            pearsonCorrelationDict[ID] = Sxy/sqrt(Sxx*Syy)
        else:
            pearsonCorrelationDict[ID] = 0


    return pearsonCorrelationDict

def backgound_img():
    img = '''
    <style>
    .stApp {
    background-image: url("https://media.istockphoto.com/vectors/abstract-background-of-ones-and-zeros-vector-id962532570?k=20&m=962532570&s=612x612&w=0&h=6OFSdIFgI508TwhnaJRCHMdNqWIjsU8oMS-bgBaZ7mk=");
    background-size: cover;
    }
    </style>
    '''
    return st.markdown(img, unsafe_allow_html=True)
