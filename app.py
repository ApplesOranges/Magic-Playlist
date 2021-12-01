from flask import Flask, request, redirect,jsonify
from spotipy.oauth2 import SpotifyOAuth
import spotipy.util as util
import spotipy
from prediction import genPlaylist

app = Flask(__name__)

app.secret_key = 'SOMETHING-RANDOM'

#Esta funcion si la tienes en flutter te puede servir solo para obtener el token, !no funciona en web solo funciono 1 vez xd
@app.route("/getTokenSpot")
def getTokenSpot():
    client_id="31aa0e52bc444791bd5e4ca52a1674c5"
    client_secret="30ac3631080340a180a8767274bc598d"
    scope='playlist-modify-public user-library-read playlist-modify-public'
    token = util.prompt_for_user_token(scope, client_id= client_id, client_secret=client_secret, redirect_uri='http://localhost:8080/callback')
    return jsonify({"token":token}),200

#esta no mas es para poder acceder a la de abajo xd
@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)
    return redirect(auth_url)

#esta es la ruta de autorizacion que te devuelve la info del token
@app.route('/authorize')
def authorize():
    sp_oauth = create_spotify_oauth()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code,check_cache=False)
    return jsonify({"token_info":token_info}),200


@app.route('/getAllPlaylists')
def getAllPlaylists():
    tk=request.headers.get('SpotifyToken')
    if tk is None:
        return jsonify({"msg":"token not found"}),400
    sp = spotipy.Spotify(auth=tk)
    pLists= sp.current_user_playlists()
    pLists=pLists["items"]
    pLists=[{
                "url_playlist":element["external_urls"]["spotify"],
                "id": element["id"],
                "image":element["images"][0]["url"],
                "name": element["name"]
            }
            for element in pLists]
    return jsonify({"Playlists":pLists,"msg":"playlists obtained successfully"}),200

@app.route("/infoPlaylist/<id>")
def infoPlaylist(id):
    tk=request.headers.get('SpotifyToken')
    if tk is None:
       return jsonify({"msg": "token not found"}), 400 
    sp = spotipy.Spotify(auth=tk)
    pList=sp.playlist(id)
    playListInfo={"url_playlist":pList["external_urls"]["spotify"],
                "id":pList["id"],
                "image":pList["images"][0]["url"],
                "name":pList["name"]
                }
    pList=pList["tracks"]["items"]
    songlist= [{
                "url":element["track"]["external_urls"]["spotify"],
                "id":element["track"]["id"],
                "name": element["track"]["name"],
                "album_image": element["track"]["album"]["images"][0]["url"]
                }
                for element in pList]
    return jsonify({"PlaylistInfo":playListInfo,"songList":songlist, "msg": "playlist obtained successfully"})

@app.route("/generatePlaylist/<int:num>/<name>")
def generatePlaylist(num,name):
    tk=request.headers.get('SpotifyToken')
    if tk is None:
       return jsonify({"msg": "token not found"}), 400 
    sp = spotipy.Spotify(auth=tk)
    try:
        pList=genPlaylist(sp,num,str(name))
    except:
        return jsonify({"msg":"playlist not found"}),400
    save=pList
    pList=[sp.track(element) for element in pList]
    songInfo=[{
            "url":element["external_urls"]["spotify"],
            "id":element["id"],
            "name": element["name"],
            "album_image": element["album"]["images"][0]["url"]
            } 
            for element in pList]
    return jsonify({"songInfo":songInfo,"ids":save}),200

@app.route("/savePlaylist/<name>",methods=["POST"])
def savePlaylist(name):
    tk=request.headers.get('SpotifyToken')
    if tk is None:
       return jsonify({"msg": "token not found"}), 400 
    sp = spotipy.Spotify(auth=tk)
    ids=request.get_json()
    ids=ids["ids"]
    meId=sp.me()["id"]
    playlistInfo=sp.user_playlist_create(meId,name,description="Una playlist creada por Magic Playlist")
    playlistId=playlistInfo["id"]
    sp.user_playlist_add_tracks(meId,playlistId,ids)
    return jsonify({"msg":"Playlist created"}),200

#funciones backend
def create_spotify_oauth():
    return SpotifyOAuth(
            client_id="31aa0e52bc444791bd5e4ca52a1674c5",
            client_secret="30ac3631080340a180a8767274bc598d",
            redirect_uri="http://localhost:8080/authorize",
            scope="user-library-read playlist-modify-public")



if __name__ == "__main__":
    app.run(port=8080, debug=True)