from flask import Flask, render_template, request
import pickle
import requests

app = Flask(__name__)

# In This Case, {} Is A Placeholder For The Movie_id, And When The Format Method Is Called, It Replaces {} With The Actual Value Of Movie_id
# Send an HTTP GET Request To The TMDb API
# Parse The Response as JSON
# Extract The Poster Path From The API Response
# Construct The Full Url For The Movie Poster Using The Poster Path
# Return The Full Url Of The Movie Poster


def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=f608954e117860a67fc14d53f644a85b&language=en-US".format(
        movie_id
    )
    data = requests.get(url)
    data = data.json()
    poster_path = data["poster_path"]
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path


def recommend(movie, movies, similarity):
    # Find The Index Of The Selected Movie In The Dataframe
    index = movies[movies["title"] == movie].index[0]
    # Calculate Distances (Similarity Scores) Between The Selected Movie And All Other Movies
    distances = sorted(
        list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1]
    )
    # Initialize Lists To Store Recommended Movie Names And Posters
    recommended_movie_names = []
    recommended_movie_posters = []
    # Iterate Through The Top 5 Similar Movies (Excluding The Selected Movie Itself)
    for i in distances[1:6]:
        # Fetch The Movie Poster
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters


@app.route("/", methods=["GET", "POST"])
def movie_recommender():
    # Load Precomputed Data: Movie_list And Similarity Matrix
    movies = pickle.load(open("movie_list.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))

    # Initialize Lists To Store Recommended Movie Names And Posters
    recommended_movie_names = []
    recommended_movie_posters = []

    # Check If The Request Method IS POST
    if request.method == "POST":
        # Get The Selected Movie From The Form Data
        selected_movie = request.form.get("selected_movie")
        # Check If A Movie IS Selected
        if selected_movie is not None:
            # Call The Recommend Function To Get Movie Recommendations
            recommended_movie_names, recommended_movie_posters = recommend(
                selected_movie, movies, similarity
            )

    # Render The HTML Template With Relevant Data
    return render_template(
        "index.html",
        movie_list=movies["title"].values,
        selected_movie=request.form.get("selected_movie"),
        recommended_movie_names=recommended_movie_names,
        recommended_movie_posters=recommended_movie_posters,
        zip=zip,  # The Zip Function In This Context Is Used To Iterate Over Multiple Iterables (In This Case, Two Lists) In Parallel.
    )


if __name__ == "__main__":
    app.run(debug=True)
