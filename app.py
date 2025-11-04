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
        username = request.form.get("username")
        if not username:
            return "Error: Please enter a username"

        url = f"https://dragcave.net/api/v2/user?username={username}&filter=GROWING"
        headers = {"User-Agent": "Mozilla/5.0"}  # Important for public requests

        try:
            resp = requests.get(url, headers=headers, timeout=10)
        except requests.RequestException as e:
            return f"Error fetching user: {e}"

        if resp.status_code == 401:
            return f"Error: User '{username}' is private or unauthorized"
        elif resp.status_code != 200:
            return f"Error fetching user: {resp.status_code}"

        data = resp.json()
        if "dragons" not in data or len(data["dragons"]) == 0:
            return f"No growing dragons found for user '{username}'"

        dragons = load_dragons()
        for dragon in data["dragons"]:
            # Only append dragons we don’t already have
            if not any(d["id"] == dragon["id"] for d in dragons):
                dragons.append({
                    "owner": username,
                    "id": dragon["id"],
                    "name": dragon.get("name") or "Unnamed",
                    "image": dragon.get("image", "")
                })
        save_dragons(dragons)
        return redirect(url_for("index"))

    return render_template("submit.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT automatically
    app.run(host="0.0.0.0", port=port)

