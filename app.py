from flask import *
from markupsafe import escape
from werkzeug.utils import secure_filename
from flask_login import *
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *

# ----- SETTINGS ----- #
app = Flask(__name__,static_url_path='/static')
app.config["SECRET_KEY"] = "lolita"
# CHANGE LATER, VERY SECRET!

# ----- DB FALSO -----#

users_db = {
    "1": {
        "username": "aaa",
        "pw": "aaa"
    },
    "2": {
        "username": "bbb",
        "pw": "aaa"
    }
}

# ----- USER CLASS ----- #
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username
    
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



# ----- FORMS ----- #
class LoginForm(FlaskForm):
    username = StringField("Nome de usuário", validators=[DataRequired()])
    pw = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")

# ------------------ #

@app.route("/login", methods=['GET','POST'])
def login_page():
    return render_template('login.html',form=LoginForm())

@app.route("/logintest", methods=['GET','POST'])
def login_test():
    return render_template('logintestold.html', form=LoginForm())

@app.route('/')
@app.route('/<name>')
def index(name=None):
    if current_user.is_authenticated:
        name = current_user.username
    return render_template('index.html', person=name,is_logged=current_user.is_authenticated)

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