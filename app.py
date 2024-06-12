from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

api_key = "4b322936e8msha6d2fcc0a329ab0p1b9b8djsn568010d420d9"
api_host = "live-golf-data.p.rapidapi.com"
base_url = "https://live-golf-data.p.rapidapi.com/leaderboard"

headers = {
    "x-rapidapi-key": api_key,
    "x-rapidapi-host": api_host
}

# Function to fetch leaderboard data for a specific round
def fetch_leaderboard(round_id):
    querystring = {"orgId": "1", "tournId": "033", "year": "2024", "roundId": round_id}
    response = requests.get(base_url, headers=headers, params=querystring)
    return response.json()

# Function to convert score to integer
def convert_score_to_int(score):
    try:
        return int(score)
    except ValueError:
        if score == 'E':
            return 0  # Even par is considered 0
        elif score == "-":
            return None  # Indicates the player was cut
        else:
            raise

# Function to calculate total score with bonus points and penalties
def calculate_score_with_bonus(golfer, rounds_data):
    cumulative_score = 0
    print(f"\nCalculating total score for {golfer}...")

    for round_id in range(1, 5):  # Rounds 1 to 4
        leaderboard = rounds_data[round_id]
        player_data = next((player for player in leaderboard if f"{player['firstName']} {player['lastName']}" == golfer), None)

        if player_data:
            # Check for cut players
            round_score_change = convert_score_to_int(player_data['currentRoundScore'])
            if round_score_change is None:
                # Ensure the round exists in the player's rounds data
                if round_id - 1 < len(player_data['rounds']):
                    round_score_change = convert_score_to_int(player_data['rounds'][round_id - 1]['scoreToPar'])
                else:
                    print(f"No data for round {round_id} for {golfer}")
                    break

            position = player_data['position']
            print(f"Round {round_id} score change for {golfer}: {round_score_change}, Position: {position}")

            # Apply bonus points based on position
            if position in ['1', 'T1']:
                if round_id == 1:
                    round_score_change -= 1
                    print("Applying -1 bonus points for Round 1 lead!")
                elif round_id == 2:
                    round_score_change -= 2
                    print("Applying -2 bonus points for Round 2 lead!")
                elif round_id == 3:
                    round_score_change -= 3
                    print("Applying -3 bonus points for Round 3 lead!")
                elif round_id == 4:
                    round_score_change -= 5
                    print("Applying -5 bonus points for tournament win!")

            cumulative_score += round_score_change
            print(f"Score at the end of Round {round_id} for {golfer}: {cumulative_score}")

            # Apply a 10-stroke penalty if the player is cut after Round 2
            if round_id == 2 and player_data['status'] == 'cut':
                print(f"Applying +10 stroke penalty for cut after Round 2 for {golfer}")
                cumulative_score += 10
                break  # Stop processing further rounds since the player is cut
        else:
            print(f"{golfer} not found in Round {round_id} data.")
            break
    
    print(f"Total score for {golfer} with bonus points and penalties: {cumulative_score}\n")
    return cumulative_score

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate_scores', methods=['POST'])
def calculate_scores():
    data = request.get_json()
    golfers = data['golfers']

    # Fetch leaderboard data for all rounds
    rounds_data = {}
    for round_id in range(1, 5):
        rounds_data[round_id] = fetch_leaderboard(round_id).get("leaderboardRows", [])

    combined_score = 0
    for golfer in golfers:
        combined_score += calculate_score_with_bonus(golfer, rounds_data)

    return jsonify(combined_score=combined_score)

if __name__ == '__main__':
    app.run(debug=True)

