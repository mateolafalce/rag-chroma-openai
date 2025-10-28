# RAG-Chroma-OpenAI

This project implements a Retrieval-Augmented Generation (RAG) system using Flask, OpenAI, and ChromaDB. It allows you to perform intelligent queries on your own data, integrating generative AI capabilities.

<div align="center">

<img src="static/1.png" alt="Preview" />

<img src="static/2.png" alt="Preview" />

<img src="static/3.png" alt="Preview" />

</div>

## Installation

1. Clone the repository and navigate to the project folder:

```bash
git clone https://github.com/mateolafalce/rag-chroma-openai.git
cd rag-chroma
```

2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your OpenAI API key:

```env
OPENAI_API_KEY=sk-...
```

## Usage

1. Start the Flask application:

```bash
python app.py
```

2. Access the web interface at [http://localhost:5000](http://localhost:5000).

## Usar Docker

Para levantar la aplicación usando Docker Compose sigue estos pasos:

1. Crea un archivo `.env` en la raíz del proyecto con tu clave de OpenAI:

```bash
# .env
OPENAI_API_KEY=sk-...
```

Docker Compose cargará automáticamente ese archivo y lo pasará al contenedor.

2. Construye y arranca el servicio:

```bash
docker compose up --build
```

O, si usas la versión clásica de docker-compose:

```bash
docker-compose up --build
```

3. Abre tu navegador en http://localhost:5000

Notas:
- El volumen `./chroma_db` se monta dentro del contenedor para persistir la base de datos de Chroma entre reinicios.
- Si quieres ejecutar en segundo plano añade la opción `-d` (ej.: `docker compose up --build -d`).


