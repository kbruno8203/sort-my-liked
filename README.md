# SortMyLiked Project Documentation

***The app requires authentication from a Spotify user profile and is still in current development***

Build an app app called "SortMyLiked" that uses the Spotify API to display information about a user's music profile. The app is intended to function as follows:
- user visits the webpage
- Authentication - user logs in with their Spotify account information and allows permissions
- a loading page is displayed while the program runs the necessary functions
- Once loaded, the dashboard is displayed to the user

## Dashboard
The dashboard contains the following elements:
#### 1. Number of Liked Songs
The number of songs in the account's "Liked Songs"
#### 2. Number of Duplicates
The number of songs that appear in the account's "Liked Songs" more than once
- to be considered a duplicate, a song must have the same title, artist(s), and release year; what may vary is the album because some songs are released as singles. 
#### 3. Top 3 Artists
Displays the name and profile picture for the artists that appear in "Liked Songs" the most often - i.e. have the highest song count
- the artists should be numbered 1, 2, and 3 and appear in order from most liked songs (artist 1) to least liked songs (artist 3)
- the display should also include the liked song count for each artist
- For example, 

| Ranking | Profile Picture | Artist Name   | Number of Liked Songs by this artist |
| ------- | --------------- | ------------- | ------------------------------------ |
| 1       | img             | Maggie Rogers | 24                                   |
| 2       | img             | Clairo        | 17                                   |
| 3       | img             | The Marías    | 11                                   |

#### 4.Release Year Graph
A histogram with song release year on the x-axis and the count of songs in Liked Songs with that release year on the y-axis.
