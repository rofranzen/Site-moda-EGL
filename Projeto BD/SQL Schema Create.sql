CREATE TABLE estados(
	sigla CHAR(2) PRIMARY KEY,
	nome VARCHAR(50) UNIQUE NOT NULL
);


CREATE TABLE users(
	user_id SERIAL PRIMARY KEY,
	username VARCHAR(50) UNIQUE NOT NULL,
	pw VARCHAR(50) NOT NULL,
	estado_sigla CHAR(2) REFERENCES estados(sigla)
);

CREATE TABLE tamanhos(
	tam_id SERIAL PRIMARY KEY,
	nome VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE pecas(
	peca_id SERIAL PRIMARY KEY,
	nome VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE marcas(
	marca_id SERIAL PRIMARY KEY,
	nome VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE estilos(
	estilo_id SERIAL PRIMARY KEY,
	nome VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE tags(
	tag_id SERIAL PRIMARY KEY,
	nome VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE anuncios(
	anuncio_id SERIAL PRIMARY KEY,
	nome VARCHAR(50) NOT NULL,
	status VARCHAR(10) NOT NULL,
	data_postado DATE,
	trocas BOOL NOT NULL,
	defeito BOOL NOT NULL,
	preco DECIMAL(5,2) NOT NULL,
	descricao TEXT,

	tamanho INTEGER REFERENCES tamanhos(tam_id),
	peca INTEGER REFERENCES pecas(peca_id),
	marca INTEGER REFERENCES marcas(marca_id)
);

CREATE TABLE estilo_anuncio(
	anuncio INTEGER NOT NULL REFERENCES anuncios(anuncio_id),
	estilo INTEGER NOT NULL REFERENCES estilos(estilo_id),

	PRIMARY KEY(estilo,anuncio)
);

CREATE TABLE tag_anuncio(
	anuncio INTEGER NOT NULL REFERENCES anuncios(anuncio_id),
	tag INTEGER NOT NULL REFERENCES tags(tag_id),

	PRIMARY KEY(tag,anuncio)
);

CREATE TABLE fotos(
	foto_id SERIAL PRIMARY KEY,
	anuncio INTEGER NOT NULL REFERENCES anuncios(anuncio_id),
	arquivo BYTEA NOT NULL
);

