import requests
from flask import Flask, request, render_template, redirect, url_for
import json, os

app = Flask(__name__)
DRAGON_FILE = "dragons.json"  # File to store the dragons temporarily

# Set your Dragon Cave Client ID here (replace with your actual Client ID)
CLIENT_ID = "aya's-dragon-wagon.cb98ed1b48cb1d76"

# Function to load dragons from the local JSON file
def load_dragons():
    if os.path.exists(DRAGON_FILE):
        with open(DRAGON_FILE) as f:
            return json.load(f)
    return []

# Function to save dragons to the local JSON file
def save_dragons(dragons):
    with open(DRAGON_FILE, "w") as f:
        json.dump(dragons, f, indent=2)

# Route to display the list of dragons (show 200 random dragons from the stored file)
@app.route("/", methods=["GET"])
def index():
    dragons = load_dragons()
    # Show only 200 random dragons, or fewer if there are not enough
    import random
    dragons_sample = random.sample(dragons, min(len(dragons), 200))
    return render_template("index.html", dragons=dragons_sample)

# Route for submitting a username to fetch their dragons
@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return "Error: Please enter a username"

        # API request to fetch user's dragons (filtering for GROWING dragons only)
        url = f"https://dragcave.net/api/v2/user?username={username}&filter=GROWING"
        
        # Set the headers to include the Client ID for authorization
        headers = {
            "Client-ID": aya's-dragon-wagon.cb98ed1b48cb1d76  # This is where we pass the Client ID
        }

        # Make the request with headers
        resp = requests.get(url, headers=headers)

        if resp.status_code != 200:
            return f"Error fetching user: {resp.status_code}"

        data = resp.json()

        # Check if there are dragons in the response
        if "dragons" not in data:
            return f"Error: No dragons found for user '{username}'"

        dragons = load_dragons()
        for dragon in data["dragons"]:
            dragons.append({
                "owner": username,
                "id": dragon["id"],
                "name": dragon.get("name") or "Unnamed",  # If no name, default to "Unnamed"
                "image": dragon.get("image", "")  # Optional image field, some dragons might not have images
            })

        save_dragons(dragons)  # Save updated list of dragons to the file
        return redirect(url_for("index"))  # Redirect to the index page to show the list of dragons

    return render_template("submit.html")  # Render the submit page for the user to enter a username

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Run the Flask app
