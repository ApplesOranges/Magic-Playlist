from flask import Flask, request, jsonify
import spotipy
from prediction import genPlaylist

app = Flask(__name__)

app.secret_key = 'SOMETHING-RANDOM'


@app.route('/getAllPlaylists')
def getAllPlaylists():
    tk = request.headers.get('SpotifyToken')
    if tk is None:
        return jsonify({"msg": "token not found"}), 400
    sp = spotipy.Spotify(auth=tk)
    pLists = sp.current_user_playlists()
    pLists = pLists["items"]
    pLists = [{
        "url_playlist": element["external_urls"]["spotify"],
        "id": element["id"],
        "image":element["images"][0]["url"],
        "name": element["name"]
    }
        for element in pLists]
    return jsonify({"Playlists": pLists, "msg": "playlists obtained successfully"}), 200


@app.route("/infoPlaylist/<id>")
def infoPlaylist(id):
    tk = request.headers.get('SpotifyToken')
    if tk is None:
        return jsonify({"msg": "token not found"}), 400
    sp = spotipy.Spotify(auth=tk)
    pList = sp.playlist(id)
    playListInfo = {"url_playlist": pList["external_urls"]["spotify"],
                    "id": pList["id"],
                    "image": pList["images"][0]["url"],
                    "name": pList["name"]
                    }
    pList = pList["tracks"]["items"]
    songlist = [{
                "url": element["track"]["external_urls"]["spotify"],
                "id":element["track"]["id"],
                "name": element["track"]["name"],
                "album_image": element["track"]["album"]["images"][0]["url"],
                "artists":[artirst["name"] for artirst in element["track"]["artists"]]
                }
                for element in pList]
    return jsonify({"PlaylistInfo": playListInfo, "songList": songlist, "msg": "playlist obtained successfully"})


@app.route("/generatePlaylist/<int:num>/<name>")
def generatePlaylist(num, name):
    tk = request.headers.get('SpotifyToken')
    if tk is None:
        return jsonify({"msg": "token not found"}), 400
    sp = spotipy.Spotify(auth=tk)
    try:
        pList = genPlaylist(sp, num, str(name))
    except:
        return jsonify({"msg": "playlist not found"}), 400
    save = pList
    pList = [sp.track(element) for element in pList]
    songInfo = [{
        "url": element["external_urls"]["spotify"],
        "id":element["id"],
        "name": element["name"],
        "album_image": element["album"]["images"][0]["url"]
    }
        for element in pList]
    return jsonify({"songInfo": songInfo, "ids": save}), 200


@app.route("/savePlaylist/<name>", methods=["POST"])
def savePlaylist(name):
    tk = request.headers.get('SpotifyToken')
    if tk is None:
        return jsonify({"msg": "token not found"}), 400
    sp = spotipy.Spotify(auth=tk)
    ids = request.get_json()
    ids = ids["ids"]
    meId = sp.me()["id"]
    playlistInfo = sp.user_playlist_create(
        meId, name, description="Una playlist creada por Magic Playlist")
    playlistId = playlistInfo["id"]
    sp.user_playlist_add_tracks(meId, playlistId, ids)
    return jsonify({"msg": "Playlist created"}), 200


if __name__ == "__main__":
    app.run(port=8080, debug=True)
