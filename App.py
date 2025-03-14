from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Load or initialize JSON files
def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return []

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

def load_news():
    if os.path.exists('news.json'):
        with open('news.json', 'r') as f:
            return json.load(f)
    return []

def save_news(news):
    with open('news.json', 'w') as f:
        json.dump(news, f, indent=4)

# Initialize users and news
brukere = load_users()
nyheter = load_news()

# Example news item
if not nyheter:
    nyheter.append({
        "overskrift": "Gene Hackman Was Their Most Famous Neighbor. They Rarely Saw Him.",
        "ingress": "Before they were found dead at home last week, the movie star and his wife, Betsy Arakawa, lived an increasingly isolated life in New Mexico.",
        "artikkel": ""
    })
    save_news(nyheter)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    brukernavn = request.form['brukernavn']
    passord = request.form['passord']
    for user in brukere:
        if user['brukernavn'] == brukernavn and user['passord'] == passord:
            session['brukernavn'] = brukernavn
            session['rolle'] = user['rolle']
            if user['rolle'] == 'admin':
                return redirect(url_for('admin'))
            elif user['rolle'] == 'bruker':
                return redirect(url_for('bruker'))
    return "Feil brukernavn eller passord. Prøv igjen.", 401

@app.route('/bruker')
def bruker():
    if 'brukernavn' not in session or session['rolle'] != 'bruker':
        return redirect(url_for('index'))
    return render_template('bruker.html', nyheter=nyheter)

@app.route('/admin')
def admin():
    if 'brukernavn' not in session or session['rolle'] != 'admin':
        return redirect(url_for('index'))
    return render_template('admin.html', brukere=brukere, nyheter=nyheter)

@app.route('/add_user', methods=['POST'])
def add_user():
    if 'brukernavn' not in session or session['rolle'] != 'admin':
        return redirect(url_for('index'))
    brukernavn = request.form['brukernavn']
    passord = request.form['passord']
    rolle = request.form['rolle']
    if not any(user['brukernavn'] == brukernavn for user in brukere):
        brukere.append({'brukernavn': brukernavn, 'passord': passord, 'rolle': rolle})
        save_users(brukere)
    return redirect(url_for('admin'))

@app.route('/delete_user', methods=['POST'])
def delete_user():
    if 'brukernavn' not in session or session['rolle'] != 'admin':
        return redirect(url_for('index'))
    brukernavn = request.form['brukernavn']
    global brukere
    brukere = [user for user in brukere if user['brukernavn'] != brukernavn]
    save_users(brukere)
    return redirect(url_for('admin'))

@app.route('/add_news', methods=['POST'])
def add_news():
    if 'brukernavn' not in session or session['rolle'] != 'admin':
        return redirect(url_for('index'))
    overskrift = request.form['overskrift']
    ingress = request.form['ingress']
    artikkel = request.form['artikkel']
    nyheter.append({'overskrift': overskrift, 'ingress': ingress, 'artikkel': artikkel})
    save_news(nyheter)
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.pop('brukernavn', None)
    session.pop('rolle', None)
    return redirect(url_for('index'))

# Public guest route (no login required)
@app.route('/guest')
def public_guest():
    return render_template('guest.html', nyheter=nyheter)

if __name__ == '__main__':
    app.run(debug=True)
