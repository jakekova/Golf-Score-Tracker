from flask import Flask, request, jsonify, render_template
import requests
import pandas as pd

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
    querystring = {"orgId": "1", "tournId": "026", "year": "2024", "roundId": round_id}
    response = requests.get(base_url, headers=headers, params=querystring)

    try:
        data = response.json()
        return data
    except requests.exceptions.JSONDecodeError as e:
        print(f"Error decoding JSON for round {round_id}: {e}")
        print(f"Response text: {response.text}")
        return {}

# Function to convert score to integer
def convert_score_to_int(score):
    try:
        return int(score)
    except ValueError:
        if score == 'E':
            return 0  # Even par is considered 0
        elif score == "-":
            return None  # Indicates the player was cut or no score available
        else:
            raise

# Function to calculate total score with bonus points and penalties
def calculate_score_with_bonus(golfer, rounds_data):
    cumulative_score = 0
    rounds_scores = ["N/A"] * 4
    rounds_positions = ["N/A"] * 4
    total_scores = [0] * 4  # To store cumulative scores after each round
    print(f"\nCalculating total score for {golfer}...")

    for round_id in range(1, 5):  # Rounds 1 to 4
        leaderboard = rounds_data.get(round_id, [])
        player_data = next(
            (player for player in leaderboard
            if f"{player['firstName']} {player['lastName']}".lower() == golfer.lower()),
            None
        )

        if player_data:
            # Check for cut players or no score available
            round_score_change = convert_score_to_int(player_data['currentRoundScore'])
            if round_score_change is None and round_id - 1 < len(player_data['rounds']):
                round_score_change = convert_score_to_int(player_data['rounds'][round_id - 1].get('scoreToPar', '-'))
                if round_score_change is None:
                    round_score_change = 0  # Default to 0 if no score is available

            position = player_data['position']
            rounds_scores[round_id - 1] = f"{round_score_change} ({position})"
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
            total_scores[round_id - 1] = cumulative_score
            print(f"Score at the end of Round {round_id} for {golfer}: {cumulative_score}")

            # Apply a 10-stroke penalty if the player is cut after Round 2
            if round_id == 2 and player_data['status'] == 'cut':
                print(f"Applying +10 stroke penalty for cut after Round 2 for {golfer}")
                cumulative_score += 10
                rounds_scores[round_id - 1] += " +10 penalty"
                break  # Stop processing further rounds since the player is cut
        else:
            print(f"{golfer} not found in Round {round_id} data.")
            break

    print(f"Total score for {golfer} with bonus points and penalties: {cumulative_score}\n")
    return cumulative_score, rounds_scores, total_scores

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

    results = []
    for golfer in golfers:
        total_score, rounds_scores, total_scores = calculate_score_with_bonus(golfer, rounds_data)
        results.append({
            "golfer": golfer,
            "total_score": total_score,
            "rounds_scores": rounds_scores,
            "total_scores": total_scores
        })

    # Create a DataFrame and convert it to HTML
    data_for_df = {
        "Golfer": [result["golfer"] for result in results],
        "R1 Score(Position)": [result["rounds_scores"][0] for result in results],
        "R1 Total Score": [result["total_scores"][0] for result in results],
        "R2 Score(Position)": [result["rounds_scores"][1] for result in results],
        "R2 Total Score": [result["total_scores"][1] for result in results],
        "R3 Score(Position)": [result["rounds_scores"][2] for result in results],
        "R3 Total Score": [result["total_scores"][2] for result in results],
        "R4 Score(Position)": [result["rounds_scores"][3] for result in results],
        "Final Score": [result["total_score"] for result in results],
    }

    df = pd.DataFrame(data_for_df)

    # Calculate the total row
    total_row = {
        "Golfer": "Total",
        "R1 Score(Position)": "",
        "R1 Total Score": df["R1 Total Score"].sum() if "R1 Total Score" in df else 0,
        "R2 Score(Position)": "",
        "R2 Total Score": df["R2 Total Score"].sum() if "R2 Total Score" in df else 0,
        "R3 Score(Position)": "",
        "R3 Total Score": df["R3 Total Score"].sum() if "R3 Total Score" in df else 0,
        "R4 Score(Position)": "",
        "Final Score": df["Final Score"].sum() if "Final Score" in df else 0,
    }

    print(f"Total row: {total_row}")

    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

    df_html = df.to_html(classes='table table-striped table-bordered', index=False, justify='center')

    return jsonify(df_html=df_html)

if __name__ == '__main__':
    app.run(debug=True)

