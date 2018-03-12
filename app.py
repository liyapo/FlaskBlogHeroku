from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import psycopg2
from flask_heroku import Heroku

POSTGRES = {
    'user': 'postgres',
    'pw': 'postgres123',
    'db': 'blogflask',
    'host': 'localhost',
    'port': '5432',
}

app = Flask(__name__) # create the application instance
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning
DB_URL = 'postgresql+psycopg2://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

# our data base
heroku = Heroku(app)
db = SQLAlchemy(app)

# from command line you can reset your database with commands:
# > set FLASK_APP = routes.py
# > flask resetdb
@app.cli.command()
def resetdb():
    """Destroys and creates the database + tables."""

    from sqlalchemy_utils import database_exists, create_database, drop_database
    if database_exists(DB_URL):
        print('Deleting database.')
        drop_database(DB_URL)
    if not database_exists(DB_URL):
        print('Creating database.')
        create_database(DB_URL)

    print('Creating tables.')
    db.create_all()
    print('Shiny!')

class Postblog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    text = db.Column(db.Text)
    created_at = db.Column(db.DateTime)

@app.route("/")
def list_articles():
    posts = Postblog.query.all()
    #created_at = post.created_at.strftime('%B %d, %Y at %H:%M:%S')
    return render_template('listarticles.html', posts=posts)

@app.route("/detailarticles/<int:pk>")
def detail_articles(pk):
    post = Postblog.query.filter_by(id=pk).one()
#    created_at = post.created_at.strftime('%B %d, %Y at %H:%M:%S')
    return render_template('detailarticles.html', post=post)

@app.route("/createarticle/")
def create_articles():
    return render_template('createarticle.html')

@app.route("/createpost/", methods=['POST'])
def create_post():
    title = request.form['title']
    subtitle = request.form['subtitle']
    author = request.form['author']
    text = request.form['text']
    #created_at = datetime.now().strftime('%B %d, %Y at %H:%M:%S')
    created_at = datetime.now().strftime('%B %d, %Y at %H:%M:%S')

    post = Postblog(title=title, subtitle=subtitle, author=author, text=text, created_at=created_at)

    db.session.add(post)
    db.session.commit()
    return redirect(url_for('list_articles'))

if __name__ == "__main__":
    app.run(debug=True)