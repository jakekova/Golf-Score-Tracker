from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/get-golf-scores', methods=['GET'])
def get_golf_scores():
    url = "https://live-golf-data.p.rapidapi.com/leaderboard"
    querystring = {"orgId": "1", "tournId": "475", "year": "2024"}

    headers = {
        "x-rapidapi-key": "4b322936e8msha6d2fcc0a329ab0p1b9b8djsn568010d420d9",
        "x-rapidapi-host": "live-golf-data.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
