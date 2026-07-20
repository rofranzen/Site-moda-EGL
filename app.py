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

# -----------------
# LISTA DE AFAZERES
# -----------------
'''
    * Chamar listas de tags a partir do bd, atualmente estão com temp equivalencies
    * Forms de criar usuário
    * forms criar usuario precisa inserir usuario desativado
    * Mudar o BD para as especificacoes novas do arquivo sql
    * Populador do BD automatico para qnd precisar reiniciar
    * Fazer forms de criar venda funcionar
    * Mudar preco no db para ser integer, nao quero gente fazendo 0.99 nos preços.
    * Formatar pagina de anuncios p mostrar cards bonitinhos bulma
    * Fazer filtros por query SQL!
    * Página de novos
    * Implementar data de expiração de anuncio
    * Só mostrar não vendidos
    * Página individual do anuncio:
        * Só pode ver contato com login
        * Se for o mesmo user que criou, pode editar e botar como vendido ou cancelado
        * Ver todas as fotos (max 10). Não pode tirar fotos ou colocar novas fotos.
    * Add fotos no form.
    * Mostrar foto principal no card.
    * Avisar que primeira foto será a foto principal do card.
    * Várias páginas de busca (escolher pag 1, 2, 3) e o link mudar. site/filtros/condicao=tal/2
    * Add nos dominios reais
    * botar servidor p rodar em pc 

SECUNDARIO
    
    * Adicionar campo "cores" e "padroes" tlvz? segunda versão do site.
    * Ver como ver cpf na receita federal (manual), lembrar de falar que o site NUNCA usará seus dados nem nome e só vai ser visto manualmente
    * Lembrar usuario que é um site pequeno mal feito logo precisa ser uma senha diferente pois é vuneravel
    * Chamar 3 pessoas e fazer primeiras vendas p/ atrair pessoas.
    * Página de user
    * Reputação
    * Lista de tamanhos
    * Pagina de artistas hehe
    * Ver um login seguro

JA IMPLEMENTADO
    * Forms de criar anuncios (só UI, sem backend)
    * Página frontal (simples)
    * Login mas não da pra criar user ainda
    * Páginas e partes bloqueadas sem login, lembrete de login
    * Db projetado
    * Listas base de tags e estilos e peças
    * Logout
    * Query de busca

'''

# ----- TEMP EQUIVALENCIES ----- #
a = "1"
b = "2"
lista_tam = [a,b]
lista_estilos = [a,b]
lista_tags = ["pasteis","monocromatico"]
lista_pecas = [a,b]
lista_marcas = ["bodyline","lisliza"]
lista_status = ["Ativo", "Vendido", "Expirado"]
lista_estados = ['AC',
                'AL',
                'AP',
                'AM',
                'BA',
                'CE',
                'DF',
                'ES',
                'GO',
                'MA',
                'MS',
                'MT',
                'MG',
                'PA',
                'PB',
                'PR',
                'PE',
                'PI',
                'RJ',
                'RN',
                'RS',
                'RO',
                'RR',
                'SC',
                'SP',
                'SE',
                'TO',
                ]

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

# ----- DB QUERY QUESTION ----- #
def make_sql(col,table,cond=None,join=None, test=False):
    query = 'SELECT ' + col + ' FROM '+ table

    '''if join:
        query += '''''

    if cond:
        query += ' WHERE ' + cond
    query += ';'

    if test:
        print("A query pedida:")
        print(query)
    cur.execute(query)
    title = [desc[0] for desc in cur.description]
    # Turns to list of tuples
    rows =  [tuple(title)] + cur.fetchall()

    '''for row in rows:
        print(row)'''
    
    if test:
        print("Acabou a query! Agora iremos df")
    return rows

# Dataframe from sql query
def sql_df(col,table,cond=None, join=None, test =False):

    if test:
        print("Começamos sql_df")

    query_res = make_sql(col=col,table=table,cond=cond,join=join,test=test)
    data = query_res[1:]
    header = query_res[0]


    if test:
        print("Vamos transformar em df:")

    df = pd.DataFrame(data)

    if test:
        print("\nSucesso! agora é um df.")

    if ',' in table:
        table_id = table[:table.index(',')-1] + '_id'
    else:
        table_id = table[:-1] + '_id'

    df.columns = header

    if test:
        print(df.columns)
        print("My table id ", table_id)

    df.set_index(table_id,inplace=True)

    if test:
        print("This is the requested df")
        print(df)
    return df


# ----- DB  QUERY INSERT ----- #

# INSERT INTO users (id,name,contact) VALUES (id_value,name_value,contact_value...)

def insert(table,values,test=False):
    # %% atualizar depois, devo fazer um dicionario para que os valores nao troquem de lugar.
    # Ex: recebe dicionario com keys do campo a inserir...

    query = 'INSERT INTO ' + table + ' VALUES ('+ values + ');'

    if test:
        print("A query pedida:")
        print(query)

    cur.execute(query)

    if test:
        print("Acabou o insert! Deu tudo certo.")

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

def render_template_w(link, df_header=None, df_values=None):
    # df é um dataframe recebido pela pagina.
    # Devemos tomar cuidado com qual dataframe é pareado com qual página!
    if current_user.is_authenticated:
        return render_template(link, header=df_header, values=df_values, person=current_user.name,is_logged=current_user.is_authenticated)
    else:
        return render_template(link, header=df_header, values=df_values, is_logged=current_user.is_authenticated)


# ----- FORMS ----- #
#Login
class LoginForm(FlaskForm):
    username = StringField("Nome de usuário", validators=[DataRequired()])
    pw = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")

#Criar conta
class CreateUserForm(FlaskForm):
    cpf = IntegerField("CPF", validators=[DataRequired()])
    username = StringField("Nome de usuário", validators=[DataRequired()])
    pw = PasswordField("Senha", validators=[DataRequired()])
    contato = StringField("Contato (email, whatsapp, instagram...)", validators=[DataRequired()])
    estado = SelectField("Estado", choices=lista_estados)
    submit = SubmitField("Entrar")

# Import dos docs de wtfforms
class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class CreateSaleForm(FlaskForm):
    nome = StringField("Nome do produto", validators=[DataRequired()])
    trocas = BooleanField("Aceita trocas?",validators=[DataRequired()])
    defeito = BooleanField("Produto com defeito?",validators=[DataRequired()])
    preco = IntegerField("Preço (Número inteiro)",validators=[DataRequired()])
    descricao = TextAreaField("Descrição",validators=[DataRequired()])
    tamanho = SelectField("Tamanho", choices=lista_tam)
    peca = SelectField("Peça", choices=lista_pecas)
    marca = SelectField("Marca", choices=lista_marcas)
    estilos = MultiCheckboxField("Estilos", choices=lista_estilos)
    tags = MultiCheckboxField("Tags", choices=lista_tags)

    submit = SubmitField("Criar venda")


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
    col = "anuncios.anuncio_id,anuncios.nome,anuncios.preco,users.username"
    table = "anuncios, users"
    cond = 'anuncios.usuario = users.user_id'
    #print("antes d anuncios")
    results = sql_df(col=col,table=table, cond=cond) #SELECT a FROM b;
    print("All anuncios:", results)
    #print("all columns", results.columns)

    return render_template_w('anuncios.html', df_header=results.columns, df_values=results.values)

@app.route("/criar_anuncio")
@login_required
def criar_anuncio():
    return render_template('criar_anuncio.html',form=CreateSaleForm())

'''@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['the_file']
        file.save(f"/var/www/uploads/{secure_filename(file.filename)}")
    return "Venda postada"'''


if __name__ == "__main__":
    app.run(debug=True)