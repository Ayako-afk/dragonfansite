from flask import Flask, render_template, request, redirect, url_for
import requests, json, random, os

app = Flask(__name__)
DATA_FILE = "dragons.json"

def load_dragons():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_dragons(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

@app.route("/")
def index():
    dragons = load_dragons()
    if len(dragons) > 200:
        dragons = random.sample(dragons, 200)
    return render_template("index.html", dragons=dragons)

@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        username = request.form["username"].strip()
        api_url = f"https://dragcave.net/api/v2/user?username={username}&filter=GROWING"
        try:
            resp = requests.get(api_url)
            data = resp.json()

            dragons = load_dragons()
            for dragon in data["growing"]:
                # store each dragon's link + owner
                dragons.append({
                    "owner": username,
                    "id": dragon["id"],
                    "name": dragon.get("name") or "Unnamed",
                    "image": dragon["image"]
                })
            save_dragons(dragons)
            return redirect(url_for("index"))
        except Exception as e:
            return f"Error: {e}"

    return render_template("submit.html")

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
