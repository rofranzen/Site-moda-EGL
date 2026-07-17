from flask import *
from markupsafe import escape
from werkzeug.utils import secure_filename
from flask_login import LoginManager
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *

# ----- SETTINGS ----- #
app = Flask(__name__,static_url_path='/static')
app.config["SECRET_KEY"] = "lolita"
# CHANGE LATER, VERY SECRET!

# ----- USER CLASS ----- #
class User(UserMixin):
    def __init__(self):
        self.exists = True

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


@app.route("/hello")
def hello_world():
    name = request.args.get("Name?", "Flask")
    return f"<p>Hello, world...</p>{escape(name)}"


@app.route("/user/<username>")
def profile(username):
    return f"{escape(username)}'s page."

@app.route("/login", methods=['GET','POST'])
def login_page():
    return render_template('login.html',form=LoginForm())

@app.route("/logintest", methods=['GET','POST'])
def login_test():
    return render_template('logintestold.html', form=LoginForm())

@app.route('/')
@app.route('/<name>')
def index(name=None):
    return render_template('index.html', person=name)


'''@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['the_file']
        file.save(f"/var/www/uploads/{secure_filename(file.filename)}")
    return "Venda postada"'''

@app.route('/passing', methods=['GET', 'POST'])
#@app.route('/passing2', methods=['GET', 'POST'])
def submit():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.pw.data

        return render_template('logged.html', username=username, pw=password)
    return redirect(url_for('login_page'))

if __name__ == "__main__":
    app.run(debug=True)