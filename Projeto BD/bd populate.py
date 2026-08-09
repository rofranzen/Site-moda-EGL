import psycopg2
import pandas as pd
from pathlib import Path

# ----- CONEXÃO PSYCOPG -----#
import psycopg2
try:
    conn = psycopg2.connect(dbname='postgres', user='postgres', host='localhost', port=5432, password='postgres')
    print("Connection succesful")
except Exception as e:
    print("I am unable to connect to the database", e)
cur = conn.cursor()

def insert(table,values,col='',test=False):
    # %% atualizar depois, devo fazer um dicionario para que os valores nao troquem de lugar.
    # Ex: recebe dicionario com keys do campo a inserir...
    if test:
        print('*-'*40)


    query = f'INSERT INTO {table}  {col} VALUES ( {",".join(["%s"] * len(values))} )'
    #query += " RETURNING " + table[:-1] + "_id;"
    # Vai usar o return pra ver se funcionou

    if test:
        print("A query pedida:")
        print(query, (values))

    try:

        cur.execute(query, (values))
        conn.commit()

        return True
    except Exception as e:
        if test:
            print("O insert acabou e errou...")
            print("Excessão", e)
        return False

def maquina_estados(text):
    #Pega file e tira titulo e dados

    odd_even = 0
    line = []
    matrix = []
    item = ""
    for char in text:
        if char == "\"":
            odd_even += 1
            if odd_even > 1:
                # É par e final de item
                line.append(item)
                item = ""
                odd_even = 0
        elif char == "\n":
            matrix.append(line)
            line = []
            odd_even = 0
        elif odd_even == 1:
            item += char
    matrix.append(line)
    return matrix

def reset_serial_call(table):

    table_id = table[:-1] + "_id"
    val = table + "_" + table_id + "_seq"
    query = f"SELECT setval('{val}',(SELECT MAX({table_id}) FROM {table}));"
    
    cur.execute(query)

        
def truncate(table):
    query = "TRUNCATE TABLE " + table + " CASCADE;"

    cur.execute(query)
    conn.commit()

def populate(table):

    base = Path(__file__).parent
    filename = base / "data_initializer" / f"{table}.txt"

    content = ""
    with open(filename, 'r', encoding="utf-8") as f:
        content = f.read()
    content = maquina_estados(content)

    title = content[0]
    data = content[1:]
    '''print(title)
    print("this is ", data)
    print(content[:])'''

    if table == "fotos":
        for row in data:
            # Le a imagem de acordo com o link especificado.
            filename = base / "data_initializer" / "fotos" / (row[title.index("arquivo")] + "." + row[title.index("tipo_arquivo")])
            f = open(filename,'rb')
            filedata = psycopg2.Binary( f.read() )
            row[title.index("arquivo")] = filedata

    col_str = "("
    for col in title:
        col_str += col + ", "
    col_str = col_str[:-2] + ")"
    #print("col_str: ", col_str)

    for row in data:
        #print(row)
        insert(table=table, col=col_str, values=row, test=False)

    if table != "estados":
        reset_serial_call(table)

# Precisa ser essa ordem!!! estados -> users -> resto -> anuncios
tables = ["estados","users", "tags", "marcas", "tamanhos", "estilos", "pecas", "estampas", "cores","anuncios", "fotos"]

for table in tables:
    #print("Tentar... ->", table)
    truncate(table)
    populate(table)

    
