from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Schema
from datetime import datetime
import psycopg2
from flask_heroku import Heroku
 

#-----------------------------------------------
#    Data base
#-----------------------------------------------

POSTGRES = {
    'user': 'postgres',
    'pw': 'postgres123',
    'db': 'blogflask',
    'host': 'localhost',
    'port': '5432',
}

app = Flask(__name__) # create the application instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning
DB_URL = 'postgresql+psycopg2://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

# our data base
heroku = Heroku(app)
db = SQLAlchemy(app)

#----------------------------------------------------------
# class for articles and for api
#----------------------------------------------------------

class Postblog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    text = db.Column(db.Text)
    created_at = db.Column(db.DateTime)

class PostSchema(Schema):
    class Meta:
        fields = ("id", "title", "author", "text", "created_at")

#-----------------------------------------------------------
# views and urls
#-----------------------------------------------------------

@app.route("/api/", methods=['GET'])
def api_get_posts():
    posts = Postblog.query.all()
    result = PostSchema(many=True)
    return jsonify(result.dump(posts).data)
    
@app.route("/")
def list_articles():
    posts = Postblog.query.all()
    return render_template('listarticles.html', posts=posts)

@app.route("/detailarticles/<int:pk>")
def detail_articles(pk):
    post = Postblog.query.filter_by(id=pk).one()
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
    created_at = datetime.now().strftime('%B %d, %Y at %H:%M:%S')
    
    post = Postblog(title=title, subtitle=subtitle, author=author, text=text, created_at=created_at)

    db.session.add(post)
    db.session.commit()
    return redirect(url_for('list_articles'))

#--------------------------------------------------------------
# python app.py to run server
#--------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)