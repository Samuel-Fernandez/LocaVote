from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.models.users_model import load_users, save_users, add_user
from app.models.countries_model import load_countries, get_current_voting_country, set_current_voting_country, get_country_by_id
from app.models.vote_model import get_all_votes, save_votes, add_vote, get_one_vote
from datetime import datetime, timedelta

# Ajouter en haut du fichier, après les imports
active_users = {}  # Dictionnaire pour suivre les utilisateurs actifs



main = Blueprint('main', __name__)

@main.route('/profiles', methods=['GET', 'POST'])
def profile():
    users = load_users()

    if request.method == 'GET':
        current_user_id = session.get('user_id')
        filtered_users = [u for u in users if u["id"] != current_user_id]
        return render_template('profile.html', users=filtered_users)
    elif request.method == 'POST':
        new_user = request.form.get('new_user')

        if new_user:
            users = load_users()
            new_id = max([u["id"] for u in users], default=0) + 1
            add_user(new_id, new_user)
        return redirect(url_for('main.profile'))

@main.route('/', methods=['GET'])
def home(): 
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    
    countries = load_countries()

    current_voting_country = get_current_voting_country()

    return render_template('home.html', user_id=user_id, user_name=user_name, countries=countries, current_voting_country=current_voting_country)

@main.route("/current_vote_country")
def current_vote_country():
    country = get_current_voting_country()
    if country:
        return jsonify({
            "id": country.id,
            "name": country.name
        })
    else:
        return jsonify(None)


@main.route('/get_current_country', methods=['GET'])
def get_current_country():
    current_country = get_current_voting_country()
    
    if current_country:
        return jsonify({
            'country_id': current_country['id'],
            'country_name': current_country['name']
        })
    else:
        return jsonify({
            'country_id': None,
            'country_name': None
        })

@main.route('/set_country', methods=['POST'])
def set_voting_country_form():
    country_id = request.form.get('country')
    if country_id and set_current_voting_country(int(country_id)):
        return redirect(url_for('main.home'))
    else:
        return "Error: Invalid country", 400

@main.route('/set_voting_country', methods=['POST'], endpoint='set_voting_country_route')
def set_voting_country_route():
    try:
        if not request.is_json:
            return jsonify(success=False, error="Invalid JSON request"), 400
            
        data = request.get_json()
        country_id = int(data.get("country_id"))
        success = set_current_voting_country(country_id)
        
        if success:
            country = get_country_by_id(country_id)
            if country:
                return jsonify(success=True, country_name=country["name"], country_id=country["id"])
            else:
                return jsonify(success=False, error="Country not found"), 404
        else:
            return jsonify(success=False, error="Failed to set voting country"), 400
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@main.route('/vote/<int:country_id>')
def vote(country_id):
    user_id = session.get("user_id")
    existing_vote = get_one_vote(user_id, country_id)
    return render_template('vote.html', country_id=country_id, vote=existing_vote)

@main.route('/submit_vote/<int:country_id>', methods=['POST'])
def submit_vote(country_id):
    data = request.get_json()
    vote_value = data.get('vote')
    user_id = session.get("user_id")

    if vote_value is not None and 1 <= int(vote_value) <= 20:
        existing = get_one_vote(user_id, country_id)
        if existing is None:
            add_vote(user_id, country_id, int(vote_value))
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Already voted'})
    return jsonify({'success': False})

@main.route('/results', methods=['GET'])
def results():
    # Récupère tous les votes
    votes = get_all_votes()
    countries = load_countries()  # Charger la liste des pays

    # Dictionnaire pour stocker la somme des votes et le nombre de votes par pays
    country_votes = {}

    # Accumuler les votes pour chaque pays
    for vote in votes:
        country_id = vote['country_id']
        vote_value = vote['vote']

        if country_id not in country_votes:
            country_votes[country_id] = {'total_votes': 0, 'vote_count': 0}

        country_votes[country_id]['total_votes'] += vote_value
        country_votes[country_id]['vote_count'] += 1

    # Calculer la moyenne des votes pour chaque pays et ajouter le nom du pays
    country_results = []
    for country_id, data in country_votes.items():
        average_vote = data['total_votes'] / data['vote_count']
        average_vote = round(average_vote * 4) / 4  # Arrondi à 0.25
        
        # Trouver le pays correspondant
        country = next((c for c in countries if c['id'] == country_id), None)
        country_name = country['name'] if country else f"Pays inconnu (ID: {country_id})"
        
        country_results.append({
            'country_id': country_id,
            'country_name': country_name,
            'average_vote': average_vote
        })

    # Trier les pays par la moyenne des votes (du plus élevé au plus bas)
    country_results.sort(key=lambda x: x['average_vote'], reverse=True)

    return render_template('results.html', country_results=country_results)

# Ajouter un before_request pour mettre à jour l'activité des utilisateurs
@main.before_request
def update_last_activity():
    if 'user_id' in session:
        user_id = session['user_id']
        if user_id in active_users:
            active_users[user_id] = datetime.now()

# Modifier la route select_user pour ajouter l'utilisateur aux actifs
@main.route('/select_user/<int:user_id>')
def select_user(user_id):
    users = load_users()
    selected_user = next((u for u in users if u["id"] == user_id), None)
    if selected_user:
        session.permanent = True
        session['user_id'] = selected_user['id']
        session['user_name'] = selected_user['name']
        active_users[selected_user['id']] = datetime.now()  # Ajouter à active_users
    return redirect(url_for('main.home'))

# Modifier la route logout pour retirer l'utilisateur des actifs
@main.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id in active_users:
        del active_users[user_id]
    session.clear()
    return redirect(url_for('main.profile'))

# Ajouter une nouvelle route pour obtenir les utilisateurs actifs
@main.route('/get_active_users')
def get_active_users():
    now = datetime.now()
    timeout = timedelta(minutes=30)
    # Nettoyer les utilisateurs inactifs
    to_remove = [user_id for user_id, last_active in active_users.items() if (now - last_active) > timeout]
    for user_id in to_remove:
        del active_users[user_id]
    return jsonify(list(active_users.keys()))