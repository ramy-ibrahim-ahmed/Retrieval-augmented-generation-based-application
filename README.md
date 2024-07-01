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