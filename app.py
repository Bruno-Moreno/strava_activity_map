from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('strava_activities.html')  # Ensure your HTML file is in the templates folder

if __name__ == '__main__':
    app.run(debug=True)