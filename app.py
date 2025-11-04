import requests
from flask import Flask, request, render_template, redirect, url_for
import json, os

app = Flask(__name__)
DRAGON_FILE = "dragons.json"

def load_dragons():
    if os.path.exists(DRAGON_FILE):
        with open(DRAGON_FILE) as f:
            return json.load(f)
    return []

def save_dragons(dragons):
    with open(DRAGON_FILE, "w") as f:
        json.dump(dragons, f, indent=2)

@app.route("/", methods=["GET"])
def index():
    dragons = load_dragons()
    # Show only 200 random dragons
    import random
    dragons_sample = random.sample(dragons, min(len(dragons), 200))
    return render_template("index.html", dragons=dragons_sample)

@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        dragon_code = request.form.get("dragon_code")

        if not dragon_code:
            return "Error: Please enter a dragon code"

        # URL to fetch the specific dragon using the dragon code
        url = f"https://dragcave.net/api/v2/dragon/{dragon_code}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            resp = requests.get(url, headers=headers, timeout=10)
        except requests.RequestException as e:
            return f"Error fetching dragon: {e}"

        if resp.status_code != 200:
            # Handle error if the dragon code is invalid or something went wrong
            return f"Error fetching dragon: {resp.status_code}"

        data = resp.json()

        # Check if the dragon information exists in the response
        if "dragon" not in data:
            return f"Error: Dragon with code '{dragon_code}' not found"

        # Extract dragon information
        dragon = data["dragon"]
        dragon_info = {
            "id": dragon["id"],
            "name": dragon.get("name") or "Unnamed",
            "image": dragon.get("image", ""),
            "code": dragon_code
        }

        dragons = load_dragons()
        dragons.append(dragon_info)  # Add the dragon to the list
        save_dragons(dragons)

        return redirect(url_for("index"))

    return render_template("submit.html")
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT automatically
    app.run(host="0.0.0.0", port=port)

