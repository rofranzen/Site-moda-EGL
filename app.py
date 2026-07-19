from flask import *
from markupsafe import escape
from werkzeug.utils import secure_filename
from flask_login import *
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
import psycopg2

# ----- SETTINGS ----- #
app = Flask(__name__,static_url_path='/static')
app.config["SECRET_KEY"] = "lolita"
# CHANGE LATER, VERY SECRET!

# ----- CONEXÃO PSYCOPG -----#
import psycopg2
try:
    conn = psycopg2.connect(dbname='postgres', user='postgres', host='localhost', port=5432, password='postgres')
    print("Connection succesful")
except Exception as e:
    print("I am unable to connect to the database", e)

cur = conn.cursor()

def make_sql(col,table,cond=None):
    query = 'SELECT ' + col + ' FROM '+ table

    if cond:
        query += ' WHERE ' + cond
    query += ';'

    print(query)
    cur.execute(query)
    title = [desc[0] for desc in cur.description]
    # Turns to list of tuples
    rows =  [tuple(title)] + cur.fetchall()

    '''for row in rows:
        print(row)'''
    return rows


rows = make_sql(col='*', table="users")

# Temp dictionary since the rest is using dictionary
users_db ={}
# dictionary keys
titles = rows[0][1:]
rows = rows[1:]

for i in range(len(rows)):
    row = rows[i]
    index = row[0]
    row = row[1:]
    new_dictionary = {}

    for j in range(len(row)):
        new_dictionary[titles[j]] = row[j]

    users_db[row[0]] = new_dictionary

# Preciso fazer isso ficar seguro depois. e se eu fizer uma query select where
# user == esse e pw == esse
# ai se não vier nada esta errado obviamente, e não revelaria as senhas.

# ----- DB  QUERY EXAMPLE ----- #
'''
col = "*"
table = "anuncios"
cond = "preco > 20"
results = make_sql(col=col,table=table, cond=cond) #SELECT a FROM b;

print("All anuncios:",results[1:])'''

# ----- USER CLASS ----- #
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.name = username
    
    name = None

    def get(user_id):
        data = users_db.get(user_id)

        if data:
            print("Entro")
            return User(
                username=data['username'],
                id=user_id
            )

        return None
    
    def from_username(username,pw):
        for id in users_db:
            nome_atual = users_db[id]["username"]
            senha_atual = users_db[id]["pw"]
            
            if nome_atual == username:
                if senha_atual == pw:
                    return User.get(id)
                return None
            
        return None


# ----- LOGIN ----- #
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# ----- FUNCTION WRAPPER ----- #

def render_template_w(link):
    if current_user.is_authenticated:
        return render_template(link, person=current_user.name,is_logged=current_user.is_authenticated)
    else:
        return render_template(link, is_logged=current_user.is_authenticated)

# ----- FORMS ----- #
class LoginForm(FlaskForm):
    username = StringField("Nome de usuário", validators=[DataRequired()])
    pw = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")


# ----------------- #
#       ROUTES      #
# ----------------- #

# ----- LOGIN ----- #

@app.route("/login", methods=['GET','POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('login.html',form=LoginForm())

@app.route("/logintest", methods=['GET','POST'])
def login_test():
    return render_template('logintestold.html', form=LoginForm())

@app.route('/')
def index(name=None):
    return render_template_w('index.html')

@app.route('/passing', methods=['GET', 'POST'])
def submit():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.pw.data

        user = User.from_username(username,password)
        if user:
            login_user(user)
            #return redirect(url_for('logged'))
            return redirect(url_for('index'))
    return redirect(url_for('login_page'))

@app.route('/logged')
@login_required
def logged():
    username = current_user.username
    password = "*****"
    return render_template('logged.html', username=username, pw=password)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/user/<username>")
def profile(username):
    return f"{escape(username)}'s page."


'''@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['the_file']
        file.save(f"/var/www/uploads/{secure_filename(file.filename)}")
    return "Venda postada"'''


if __name__ == "__main__":
    app.run(debug=True)