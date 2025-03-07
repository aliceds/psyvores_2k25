from flask import Flask, render_template, request, redirect, jsonify
import psycopg2
from flask_sqlalchemy import SQLAlchemy
import calendar
from datetime import datetime, timedelta, date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:WezAabnuCCilodGVDVmgJJHtkSpcuZZx@shuttle.proxy.rlwy.net:47283/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

month_names = {
  6: "Juin",
  7: "Juillet",
  8: "Août",
  9: "Septembre"
}

festival_colors = [
    "#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#A133FF",
    "#33FFF5", "#FFC733", "#8D33FF", "#FF8D33", "#33FF8D"
]


# Définir la table festivals
class Festivals(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  start_date = db.Column(db.Date, nullable=False)
  end_date = db.Column(db.Date, nullable=False)
  picture = db.Column(db.String(200))


@app.route('/')
def index():
  festivals = Festivals.query.all()
  year = 2025
  months = list(month_names)
  calendars = {month: calendar.monthcalendar(year, month) for month in list(month_names)}

  festivals = Festivals.query.filter(
    db.extract('year', Festivals.start_date) == year,
    db.extract('month', Festivals.start_date).in_(months)
  ).all()

  for i, festival in enumerate(festivals):
      festival.color = festival_colors[i % len(festival_colors)]

  # Dictionnaire associant les festivals aux jours du mois
  festivals_by_day = {month: {day: [] for week in calendars[month] for day in week if day != 0} for month in months}

  for festival in festivals:
    start_date = festival.start_date
    end_date = festival.end_date
    # Ajouter les festivals à tous les jours où ils ont lieu
    current_date = start_date

    while current_date <= end_date:
      if current_date.month in months:
        festivals_by_day[current_date.month][current_date.day].append(festival)
      current_date += timedelta(days=1)

  return render_template(
    'index.html', 
    calendars=calendars, 
    year=year, 
    date=date,
    festivals=festivals,
    month_names=month_names
  )


@app.route('/festival/add', methods=['POST'])
def add_festival():
    # Récupérer les données du formulaire
    name = request.form['name']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    picture = request.form['picture']
    
    # Créer un nouvel objet Festival
    new_festival = Festivals(
        name=name,
        start_date=start_date,
        end_date=end_date,
        picture=picture
    )
    
    # Ajouter à la base de données et valider
    db.session.add(new_festival)
    db.session.commit()
    
    return jsonify({"success": True, "id": new_festival.id})


@app.route('/festival/<int:id>/edit', methods=['GET'])
def edit_festival(id):
  festival = Festivals.query.get_or_404(id)
  return jsonify({
      "id": festival.id,
      "name": festival.name,
      "start_date": festival.start_date,
      "end_date": festival.end_date,
      "picture": festival.picture
  })

@app.route('/festival/<int:id>/update', methods=['POST'])
def update_festival(id):
  festival = Festivals.query.get_or_404(id)
  festival.name = request.form['name']
  festival.start_date = request.form['start_date']
  festival.end_date = request.form['end_date']
  festival.picture = request.form['picture']
  
  db.session.commit()
  
  return jsonify({"success": True})

@app.route('/festival/<int:id>/delete', methods=['DELETE'])
def delete_festival(id):
  festival = Festivals.query.get_or_404(id)
  db.session.delete(festival)
  db.session.commit()
  
  return jsonify({"success": True})


if __name__ == '__main__':
  app.run(debug=True)
