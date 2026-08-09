CREATE TABLE estados(
	sigla CHAR(2) PRIMARY KEY,
	nome VARCHAR(50) UNIQUE NOT NULL
);


CREATE TABLE users(
	user_id SERIAL PRIMARY KEY,
	ativado BOOLEAN NOT NULL,
	username VARCHAR(50) UNIQUE NOT NULL,
	pw VARCHAR(50) NOT NULL,
	cpf INTEGER UNIQUE NOT NULL,
	data_nascimento DATE NOT NULL,
	contato VARCHAR(50) NOT NULL,
	estado_sigla CHAR(2) REFERENCES estados(sigla)
);

CREATE TABLE tamanhos(
	tamanho_id SERIAL PRIMARY KEY,
	nome VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE pecas(
	peca_id SERIAL PRIMARY KEY,
	nome VARCHAR(50) UNIQUE NOT NULL,
	descricao TEXT
);

CREATE TABLE marcas(
	marca_id SERIAL PRIMARY KEY,
	nome VARCHAR(50) UNIQUE NOT NULL,
	nacional BOOLEAN
);

CREATE TABLE estampas(
	estampa_id SERIAL PRIMARY KEY,
	nome VARCHAR(50) UNIQUE NOT NULL,
	descricao TEXT
);

CREATE TABLE cores(
	core_id SERIAL PRIMARY KEY,
	nome VARCHAR(50) UNIQUE NOT NULL,
	descricao TEXT
);

CREATE TABLE estilos(
	estilo_id SERIAL PRIMARY KEY,
	nome VARCHAR(50) UNIQUE NOT NULL,
	descricao TEXT
);

CREATE TABLE tags(
	tag_id SERIAL PRIMARY KEY,
	nome VARCHAR(50) UNIQUE NOT NULL,
	descricao TEXT
);

CREATE TABLE anuncios(
	anuncio_id SERIAL PRIMARY KEY,
	nome VARCHAR(50) NOT NULL,
	status VARCHAR(10) NOT NULL,
	trocas BOOL NOT NULL,
	defeito BOOL NOT NULL,
	preco INTEGER NOT NULL,
	descricao TEXT,

	usuario INTEGER NOT NULL,
	data_ativado DATE NOT NULL,

	tamanho INTEGER REFERENCES tamanhos(tamanho_id),
	peca INTEGER REFERENCES pecas(peca_id),
	marca INTEGER REFERENCES marcas(marca_id)
);

CREATE TABLE estilo_anuncio(
	anuncio INTEGER NOT NULL REFERENCES anuncios(anuncio_id),
	estilo INTEGER NOT NULL REFERENCES estilos(estilo_id),

	PRIMARY KEY(estilo,anuncio)
);

CREATE TABLE estampa_anuncio(
	anuncio INTEGER NOT NULL REFERENCES anuncios(anuncio_id),
	estampa INTEGER NOT NULL REFERENCES estampas(estampa_id),

	PRIMARY KEY(estampa,anuncio)
);

CREATE TABLE cor_anuncio(
	anuncio INTEGER NOT NULL REFERENCES anuncios(anuncio_id),
	cor INTEGER NOT NULL REFERENCES cores(core_id),

	PRIMARY KEY(cor,anuncio)
);

CREATE TABLE tag_anuncio(
	anuncio INTEGER NOT NULL REFERENCES anuncios(anuncio_id),
	tag INTEGER NOT NULL REFERENCES tags(tag_id),

	PRIMARY KEY(tag,anuncio)
);

CREATE TABLE fotos(
	foto_id SERIAL PRIMARY KEY,
	anuncio INTEGER NOT NULL REFERENCES anuncios(anuncio_id),
	arquivo BYTEA NOT NULL,
	tipo_arquivo VARCHAR(10) NOT NULL,
	alt_text TEXT NOT NULL
);

