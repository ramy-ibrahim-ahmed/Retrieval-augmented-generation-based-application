# Retrieval-augmented-generation-based-application

Retrieval augmented generation chatbot with FastAPI and MongoDB

## Requirements

- Python 3.8 or later

#### Install python using miniconda

1. Download miniconda from [here](https://docs.anaconda.com/miniconda/miniconda-install/)
2. Create a new virtual environment by the following command:

```bash
$ conda create -n mini-rag python=3.8
```

3. Activate the environment:

```bash
$ conda activate mini-rag
```

# Installation

### Install the required packages

```bash
$ pip install -r requirements
```

### Setup the environment variables

```bash
$ cp .env.example .env
```

Set your own environment variables in the `.env` file. Like `OPENAI_API_KEY` Value.

## Run the FastAPI server

```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## Run Docker compose survices

```bash
$ cd docker
$ sudo docker compose up -d
```

```bash
$ cd docker
$ cp .env.example .env
```

- update `.env` with your credentials
