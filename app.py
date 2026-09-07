from flask import *
from markupsafe import escape
from werkzeug.utils import secure_filename
from flask_login import *
from flask_login import UserMixin
from flask_wtf import FlaskForm
from flask_wtf.file import *
from wtforms import *
from wtforms.validators import *
import psycopg2
import pandas as pd
import datetime
import base64

# -----------------
# LISTA DE AFAZERES
# -----------------
'''
    * Concertar rows de anuncios no mobile
    * Fazer filtros por query SQL!
    * Só mostrar não vendidos
    * Multiplas fotos no form

    * Página individual do anuncio:
        * Só pode ver contato com login V
        * Se for o mesmo user que criou, pode editar e botar como vendido ou cancelado
        * Ver todas as fotos (max 10). Não pode tirar fotos ou colocar novas fotos.
        
    * Avisar que primeira foto será a foto principal do card.
    * Várias páginas de busca (escolher pag 1, 2, 3) e o link mudar. site/filtros/condicao=tal/2
    
    * Add nos dominios reais
    * botar servidor p rodar em pc 

SECUNDARIO
    * Substituir os possiveis status em dicionarios p nao confundir no programa
    * Melhorar design card tipo tamanho dos cards e titulos
    * Lembrar usuario que é um site pequeno mal feito logo precisa ser uma senha diferente pois é vuneravel
    * Chamar 3 pessoas e fazer primeiras vendas p/ atrair pessoas.
    * Página de user
    * Reputação
    * Lista de tamanhos
    * Ver um login seguro
    * Página de novos
    * Implementar data de expiração de anuncio
    * Lidar ccom erros de formulario
    * Mudar botão de upload
    * Botar varias imagens no mesmo anuncio
    * Mostrar pag do anuncio assim que criar
    * Avisar quando imagem for grande demais
    * mudar pag anuncio de obj para dict

JA IMPLEMENTADO
    * Forms de criar anuncios (só UI, sem backend)
    * Página frontal (simples)
    * Login mas não da pra criar user ainda
    * Páginas e partes bloqueadas sem login, lembrete de login
    * Db projetado
    * Listas base de tags e estilos e peças
    * Logout
    * Query de busca
    * Forms de criar usuário
    * forms criar usuario precisa inserir usuario desativado
    * Populador do BD automatico para qnd precisar reiniciar
    * Mudar o BD para as especificacoes novas do arquivo sql
    * Mudar preco no db para ser integer, nao quero gente fazendo 0.99 nos preços.
    * Adicionar campo "cores" e "padroes"
    * Ver como ver cpf na receita federal (manual), lembrar de falar que o site NUNCA usará seus dados nem nome e só vai ser visto manualmente
    * Inicializador BD
    * Forms de venda insere venda
    * Chamar listas de tags a partir do bd, atualmente estão com temp equivalencies
    * Forms de venda inserir as relações multiplas
    * Formatar pagina de anuncios p mostrar cards bonitinhos bulma
    * Mostrar foto principal no card.
    * Add fotos no form.
    * Otimizar pesquisa de tables (tava tdo em so uma, performance horrivel)

    * Página individual do anuncio:
        * Só pode ver contato com login


'''

# ----- TEMP EQUIVALENCIES ----- #
# Não precisamos mais! Eba!
# Fonte estados https://gist.github.com/edirpedro/69c0974613de044ebba6dc7fd0c5b732

# ----- SETTINGS ----- #
app = Flask(__name__,static_url_path='/static')
app.config["SECRET_KEY"] = "lolita"
app.config['MAX_CONTENT_LENGTH'] = 2048 * 2048
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
    # Se a query tiver estados, so consegue fazer com estados sozinho até agora. precisa concertar.

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

    if table == "estados":
        table_id = "sigla"

    df.columns = header

    if test:
        print(df.columns)
        print("My table id ", table_id)

    df.set_index(table_id,inplace=True)

    if test:
        print("This is the requested df")
        print(df)
    return df

def get_for_forms(table_name, test=False):    
    df =sql_df(col="*", table=table_name)
    df = df.sort_values("nome")

    nomes = df["nome"].values.tolist()
    ids = df.index.values

    tuples = []
    for i in range(len(nomes)):
        current = (ids[i], nomes[i])
        tuples.append(current)

    if test:
        print("\n-----\nSelecionando tuplas de...", table_name)
        print(tuples)

    return tuples

def photo_w(original_results):
    # Wrap that encodes photos into base64 for jinja

    def decode(item):
        return base64.b64encode(item).decode("utf-8")

    imgs = original_results.copy()
    imgs["arquivo"] = imgs["arquivo"].apply(decode)

    return imgs


# ----- DB  QUERY INSERT ----- #

def insert(table,values,col='',test=False, return_id=False, special_returning=False):
    # %% atualizar depois, devo fazer um dicionario para que os valores nao troquem de lugar.
    # Ex: recebe dicionario com keys do campo a inserir...
    if test:
        print('*-'*40)

    '''# Values é sempre uma lista por enquanto!
    values_str = ""
    for value in values:
        if test:
            print(value)
        values_str += '\'' + value + '\','
    values_str = values_str[:-1] #Tira a ultima virgula
    
    if test:
        print("Values_str:",values_str)'''

    query = f'INSERT INTO {table}  {col} VALUES ( {",".join(["%s"] * len(values))} )'

    if not special_returning:
        query += " RETURNING " + table[:-1] + "_id;"
        # Vai usar o return pra ver se funcionou
    else:
        query += " RETURNING " + special_returning + ";"

    if test:
        print("A query pedida:")
        print(query, (values))

    try:

        cur.execute(query, (values))
        conn.commit()
        # Pega o id novo!
        suceeded = cur.fetchone()[0]

        if test:
            print("Acabou o insert! Deu tudo certo.")
            print("ID =", suceeded)

        if return_id:
            return True, suceeded
        return True
    except Exception as e:
        if test:
            print("O insert acabou e errou...")
            print("Excessão", e)

        if return_id:
            return False, False
        return False

# INSERÇÃO TABLEAS N:M
def insert_n_m(table_1, table_2, items_t1, item_t2):
    # Essa função só funciona por causa do padrão escolhido de nomes no DB.

    col = "("+ table_1 + "," + table_2 + ")"
    table_name = table_1 + "_" + table_2
    all_items_inserted = True

    for item in items_t1:
        values = [str(item),str(item_t2)]

        # O special returning é um patch.
        # def insert não pode ignorar o returning, mas a tabela não tem pk no estilo padrão
        # Logo ela precisa ser definida.

        success = insert(table=table_name, col=col, values=values, special_returning=table_2)

        if not success:
            all_items_inserted = False
    return all_items_inserted


# ------------------------------------------- #
#                                             #
#         INICIALIZAÇÃO DICIONARIOS           #
#                                             #
# ------------------------------------------- #

tables = ['pecas',
          'tamanhos',
          'marcas',
          'estampas',
          'tags',
          'estilos',
          'cores'
          ]

def create_master_reference():
    dic = {}

    for table in tables:
        col = table[:-1] + '_id, nome'
        dic[table] = sql_df(table=table, col=col).to_dict()["nome"]

    return dic

dic = create_master_reference()

query="SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'anuncios';"
cur.execute(query)
result = cur.fetchall()

sale_search_fields = []
for tuples in result:
    sale_search_fields.append(tuples[0])


# ----- ANUNCIO CLASS ----- #
class Anuncio():
    # Classe pega anuncio do bd por ID

    def __init__(self,anuncio_id=None,source_row=None):
        # Pega o row source c prioridade

        if source_row is not None:
            my_anuncio_singular = source_row
        
        elif anuncio_id:
            cond = 'anuncio_id = ' + str(anuncio_id)
            found_anuncio = sql_df(col='*', table='anuncios', cond=cond)

            if found_anuncio.empty:
                self.exists = False
                return None
            my_anuncio_singular = found_anuncio.iloc[0]
            


        self.exists = True

        self.id = anuncio_id
        self.nome = my_anuncio_singular['nome']
        self.preco = my_anuncio_singular['preco']
        self.usuario = my_anuncio_singular['usuario']
        self.descricao = my_anuncio_singular['descricao']
        self.data_ativado = my_anuncio_singular['data_ativado']

        self.tamanho = my_anuncio_singular['tamanho']
        self.peca = my_anuncio_singular['peca']
        self.marca = my_anuncio_singular['marca']
        
        self.status = my_anuncio_singular['status']
        self.trocas = my_anuncio_singular['trocas']
        self.defeito = my_anuncio_singular['defeito']

        cond = 'anuncio = ' + str(anuncio_id)
        found_foto = sql_df(col="*",table="fotos", cond=cond)
        my_img = photo_w(found_foto).iloc[0]

        self.arquivo = my_img['arquivo']
        self.tipo_arquivo = my_img['tipo_arquivo']
        self.alt_text = my_img['alt_text']
        
    def get_owner(self):
        if not self.exists:
            return None

        col = 'user_id, username, contato, estado_sigla'
        table = 'users'
        cond = 'user_id = ' + str(self.usuario)

        found_owner = sql_df(col=col, table=table, cond=cond)

        my_owner = found_owner.iloc[0]
        self.usuario_nome = my_owner['username']
        self.usuario_estado = my_owner['estado_sigla']
        self.usuario_contato = my_owner['contato']

    def status_text(self):
        if self.status:
            return "Disponível"
        return "Fechado"

    def defeito_text(self):
        if self.defeito:
            return "Sim"
        return "Não"
    
    def trocas_text(self):
        if self.trocas:
            return "Sim"
        return "Não"

    def peca_text(self):
        return dic["pecas"][self.peca]

    def tamanho_text(self):
            return dic["tamanhos"][self.tamanho]

    def marca_text(self):
            return dic["marcas"][self.marca]

    def from_df(df, test=False):

        list = []

        for index, row in df.iterrows():

            if test:
                print("index:",index)
                print("iloc:",df.loc[index])
                print("row:", row)

            item = Anuncio(source_row = row, anuncio_id = index)
            list.append(item)

        return list
        

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
        #cond = '(username = \'' + username + '\') AND (pw = \'' + pw + '\')'
        cond = "username = \'" + username + "\'"
        print("my cond",cond)

        found_user = sql_df('*', 'users', cond)

        #print("-+-"*30)
        print(found_user)
        #print("my id = ", found_id)

        if len(found_user.index) == 1:
            found_pw = found_user.iloc[0]['pw']

            if found_pw != pw:
                return "Senha não corresponde ao usuário."

            found_id = found_user.index[0]
            return User(
                username=username,
                id=found_id
            )
        return "Usuário não existe."


# ----- LOGIN ----- #
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# ----- FUNCTION WRAPPER ----- #

def render_template_w(link, sales_list=None,df_header=None, df_values=None, df_imgs=None,form=None,obj=None):
    # df é um dataframe recebido pela pagina.
    # Devemos tomar cuidado com qual dataframe é pareado com qual página!
    if current_user.is_authenticated:
        return render_template(link, sales_list=sales_list,header=df_header, values=df_values, imgs=df_imgs, person=current_user.name,is_logged=current_user.is_authenticated, form=form,obj=obj)

    else:
        return render_template(link, sales_list=sales_list, header=df_header, values=df_values, imgs=df_imgs, is_logged=current_user.is_authenticated, form=form, obj=obj)

# ----- FORMS ----- #
#Login
class LoginForm(FlaskForm):
    username = StringField("Nome de usuário", validators=[DataRequired()])
    pw = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")
#Criar conta
class CreateUserForm(FlaskForm):

    username = StringField("Nome de usuário", validators=[DataRequired()],
                           render_kw={"placeholder": "Ex: GothicMaria"})
    pw = PasswordField("Senha", validators=[DataRequired()],
                           render_kw={"placeholder": "*********"})
    cpf = IntegerField("CPF (Apenas p/ verificar conta)", validators=[DataRequired()],
                           render_kw={"placeholder": "Não registraremos nomes, respeitamos nome social."})
    nascimento = DateField("Data de nascimento (Apenas p/ verificar conta)",validators=[DataRequired()],
                           render_kw={"placeholder": "01/01/1999"})
    contato = StringField("Contato: Email, Whatsap ou Insta", validators=[DataRequired()],
                           render_kw={"placeholder": "Ex: email@muitolegal.com, (00) 12345-6789..."})
    estado = SelectField("Estado", choices=get_for_forms("estados"))
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
    trocas = BooleanField("Aceita trocas?")
    defeito = BooleanField("Produto com defeito?")
    preco = IntegerField("Preço (Número inteiro)",validators=[DataRequired(), NumberRange(min=0, max=1000)])
    descricao = TextAreaField("Descrição",validators=[DataRequired()])
    tamanho = SelectField("Tamanho", choices=get_for_forms("tamanhos"))
    peca = SelectField("Peça", choices=get_for_forms("pecas"))
    marca = SelectField("Marca", choices=get_for_forms("marcas"))
    foto = FileField("Foto do produto", validators=[FileRequired()])#, FileAllowed(["jpg", "jpeg", "png", "gif", "webp"], "Apenas são aceitos arquivos de imagem.")])
    estilos = MultiCheckboxField("Estilos", choices=get_for_forms("estilos"))
    cores = MultiCheckboxField("Cores", choices=get_for_forms("cores"))
    estampas = MultiCheckboxField("Estampas", choices=get_for_forms("estampas"))
    tags = MultiCheckboxField("Tags", choices=get_for_forms("tags"))

    submit = SubmitField("Criar venda")

class SearchSalesForm(FlaskForm):
    campo = SelectField("Campo de pesquisa", choices=sale_search_fields)


# ----------------- #
#       ROUTES      #
# ----------------- #

# ----------- #
#    LOGIN    #
# ----------- #
@app.route("/login", methods=['GET','POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('login.html',form=LoginForm())

@app.route('/passing', methods=['GET', 'POST'])
def submit():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.pw.data

        user = User.from_username(username,password)


        if type(user) is User:
            login_user(user)
            #return redirect(url_for('logged'))
            return redirect(url_for('index'))
        
    return redirect(url_for('login_page'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ----------------- #
#    CRIAR CONTA    #
# ----------------- #
@app.route("/criar_usuario")
def criar_usuario():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # Has to be wrapper func so it gets authenticated status == unlogged
    return render_template("criar_usuario.html", form=CreateUserForm())

@app.route("/passing_user_create", methods=['GET', 'POST'])
def passing_create_user():
    form = CreateUserForm()
    if form.validate_on_submit():

        # Supostamente o wtforms ja faz escaping
        # Pelo oque pesquisei é verdade, esperemos que seja mesmo...
        cpf = str(form.cpf.data) # Precisa para inserir por query
        username = form.username.data
        pw = form.pw.data
        contato = form.contato.data
        estado_sigla = form.estado.data
        data_nascimento = str(form.nascimento.data)
        ativado = str(False)

        table = "users"
        col = "(cpf,data_nascimento,username,pw,contato,estado_sigla,ativado)"
        values = [cpf,data_nascimento,username,pw,contato,estado_sigla,ativado]

        user_was_inserted = insert(table=table,col=col,values=values)
        if user_was_inserted:
            return render_template("conta_criada.html")
    return redirect(url_for('criar_usuario'))


# ---------- #
# HOME INDEX #
# ---------- #

@app.route('/')
def index(name=None):
    return render_template_w('index.html')


@app.route("/user/<username>")
def profile(username):
    return f"{escape(username)}'s page."

# -------- #
# ANUNCIOS #
# -------- #

@app.route("/anuncios_sql")
def anuncios_sql():
    template = "anuncios.html"

    # Query de todos os anuncios
    col = "anuncios.anuncio_id,anuncios.nome,anuncios.preco,users.username"
    table = "anuncios, users"
    cond = 'anuncios.usuario = users.user_id'
    #print("antes d anuncios")
    results = sql_df(col=col,table=table, cond=cond) #SELECT a FROM b;
    print("All anuncios:", results)
    #print("all columns", results.columns)

    return render_template_w('anuncios_sql.html', df_header=results.columns, df_values=results.values)

@app.route("/anuncios")
def anuncios():
    link = "anuncios.html"

    # Query de todos os anuncios
    col = "anuncios.anuncio_id," \
    "anuncios.nome as nome," \
    "anuncios.preco as preco," \
    "anuncios.data_ativado as data_ativado," \
    "anuncios.descricao as descricao," \
    "anuncios.usuario as usuario," \
    "anuncios.tamanho as tamanho," \
    "anuncios.status as status," \
    "anuncios.trocas as trocas," \
    "anuncios.defeito as defeito," \
    "pecas.nome as peca," \
    "marcas.nome as marca"
    table = "anuncios, pecas, marcas"
    cond = 'anuncios.peca = pecas.peca_id AND ' \
    'anuncios.marca = marcas.marca_id AND ' \
    'anuncios.status = \'Ativo\' ' \
    
    'ORDER BY data_ativado DESC'

    #print("antes d anuncios")
    results = sql_df(col=col,table=table, cond=cond, test=False) #SELECT a FROM b;
    #print("All anuncios:", results)
    #print("#-"*40)
    #print("all columns", results.columns)

    col = "foto_id, " \
    "arquivo, " \
    "tipo_arquivo, " \
    "anuncio," \
    "alt_text"
    table = "fotos"
    cond = ""
    df_imgs = photo_w(sql_df(col=col,table=table, cond=cond, test=False))

    sales_list = Anuncio.from_df(results)

    return render_template_w('anuncios.html', sales_list=sales_list)

@app.route("/anuncio_singular/<id>")
def anuncio_singular(id):

    obj = Anuncio(anuncio_id=id)

    if not obj.exists:
        return render_template_w('nao_existe.html')

    if current_user.is_authenticated:
        obj.get_owner()

    return render_template_w('anuncio_singular.html',obj=obj)

@app.route("/criar_anuncio")
@login_required
def criar_anuncio():
    return render_template_w('criar_anuncio.html',form=CreateSaleForm())


@app.route("/passing_sale_create", methods=['GET', 'POST'])
@login_required
def passing_sale_create():
    form = CreateSaleForm()
    print(form.marca.choices)

    if form.validate_on_submit():
        print("-*"*200)

        nome = form.nome.data
        trocas = str(form.trocas.data)
        defeito = str(form.defeito.data)
        preco = str(form.preco.data)
        descricao = form.descricao.data
        tamanho = str(form.tamanho.data)
        peca = str(form.peca.data)
        marca = str(form.marca.data)
        foto = form.foto.data #mudar para ter varias fotos dps
        cores = form.cores.data
        estampas = form.estampas.data
        estilos = form.estilos.data
        tags = form.tags.data


        status = "Ativo"
        usuario = current_user.id
        #print(current_user.id)
        data_ativado = datetime.datetime.now().strftime("%x")

        table = "anuncios"
        col = "(nome,trocas,defeito,preco,descricao,tamanho,peca,marca,usuario,status,data_ativado)"
        values = [nome,
                trocas,
                defeito,
                preco,
                descricao,
                tamanho,
                peca,
                marca,
                usuario,
                status,
                data_ativado]

        sale_was_inserted, anuncio_id = insert(table=table,
                                               col=col,
                                               values=values, 
                                               return_id=True,
                                               test=False)

        # INSERÇÃO TABLEAS N:M
        if sale_was_inserted:

            tabelas_multiplas = [["tag", tags],
                                 ["estilo", estilos],
                                 ["estampa", estampas],
                                 ["cor", cores]
                                ]
            table_2 = "anuncio"

            for i in range(len(tabelas_multiplas)):
                table_1 = tabelas_multiplas[i][0]
                items_t1 = tabelas_multiplas[i][1]
                insert_n_m(table_1=table_1, table_2=table_2, items_t1=items_t1,item_t2=anuncio_id)

            table = "fotos"
            col = "(arquivo,tipo_arquivo,anuncio,alt_text)"

            foto_bytea = psycopg2.Binary(foto.read())
            values = [ foto_bytea, "png", anuncio_id, "alt_text here"]
            foto_id = insert(table="fotos",col=col,values=values,return_id=True,test=True)


            return render_template_w("anuncio_criado.html")
        else:
            print("Anuncio falhou...")
    else:
        print(form.errors)
    return redirect(url_for('criar_anuncio'))

'''@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['the_file']
        file.save(f"/var/www/uploads/{secure_filename(file.filename)}")
    return "Venda postada"'''


@app.route("/placeholder")
def placeholder():
    return render_template("placeholder_site.html")

if __name__ == "__main__":
    app.run(debug=True)