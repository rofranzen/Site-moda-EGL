from flask import *
from markupsafe import escape
from werkzeug.utils import secure_filename
from flask_login import *
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
import psycopg2
import pandas as pd

# ----- TEMP EQUIVALENCIES ----- #


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

    '''print("A query pedida:")
    print(query)'''
    cur.execute(query)
    title = [desc[0] for desc in cur.description]
    # Turns to list of tuples
    rows =  [tuple(title)] + cur.fetchall()

    '''for row in rows:
        print(row)'''
    return rows

# Dataframe from sql query
def sql_df(col,table,cond=None):

    query_res = make_sql(col,table,cond)
    data = query_res[1:]
    header = query_res[0]

    table_id = table[:-1] + '_id'

    df = pd.DataFrame(data)
    df.columns = header
    df.set_index(table_id,inplace=True)
    '''print("This is the requested df")
    print(df)'''
    return df

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
        cond = 'user_id = ' + user_id
        found_user = sql_df('user_id, username', 'users', cond)


        if found_user.empty:
            return None
        
        return User(
            id=user_id,
            username=found_user.iloc[0]['username']
        )


    
    def from_username(username,pw):
        cond = '(username = \'' + username + '\') AND (pw = \'' + pw + '\')'
        #print("my cond",cond)
        found_user = sql_df('*', 'users', cond)
        #print("-+-"*30)
        found_id = found_user.index[0]
        #print(found_user)
        #print("my id = ", found_id)

        if len(found_user.index) == 1:
            return User(
                username=username,
                id=found_id
            )
        return None

# ----- LOGIN ----- #
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# ----- FUNCTION WRAPPER ----- #

def render_template_w(link, df=None):
    # df é um dataframe recebido pela pagina.
    # Devemos tomar cuidado com qual dataframe é pareado com qual página!
    if current_user.is_authenticated:
        return render_template(link, df=df, person=current_user.name,is_logged=current_user.is_authenticated)
    else:
        return render_template(link, df=df, is_logged=current_user.is_authenticated)


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

@app.route("/anuncios")
def anuncios():
    link = "anuncios.html"

    # Query de todos os anuncios
    col = "*"
    table = "anuncios"
    cond = ''
    results = make_sql(col=col,table=table, cond=cond) #SELECT a FROM b;
    print("All anuncios:", results)

    return render_template_w('anuncios.html', df=results,is_logged=current_user.is_authenticated)

'''@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['the_file']
        file.save(f"/var/www/uploads/{secure_filename(file.filename)}")
    return "Venda postada"'''


if __name__ == "__main__":
    app.run(debug=True)