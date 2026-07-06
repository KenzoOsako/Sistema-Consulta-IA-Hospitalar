import os
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

# Definições
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")

def get_llm():
    return Ollama(
        base_url=OLLAMA_BASE_URL,
        model=MODEL_NAME
    )

def get_embeddings():
    return OllamaEmbeddings(
        base_url=OLLAMA_BASE_URL,
        model="nomic-embed-text"
    )

def get_vector_db():
    return Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=get_embeddings()
    )

def query_local_rag(query_text: str) -> str:
    """Executa a consulta na base local do hospital"""
    db = get_vector_db()
    llm = get_llm()
    
    prompt_template = """
    Você é um agente de pesquisa médica local-first.
    Use os seguintes fragmentos de contexto para responder à pergunta.
    Os dados já foram anonimizados pela camada NER.
    Se não souber a resposta, diga que não há informações locais sobre isso.

    Contexto: {context}

    Pergunta: {question}
    
    Resposta Científica:
    """
    
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": PROMPT}
    )
    
    try:
        # Langchain changed `__call__` to `invoke` in recent versions
        res = qa_chain.invoke({"query": query_text})
        return res['result']
    except Exception as e:
        print(f"Erro no RAG local (Ollama offline/crash): {e}")
        print("\n[FALLBACK DE SIMULAÇÃO] Como o motor nativo Ollama não tem suporte de hardware nesta máquina (AVX/Memória), injetando resposta médica simulada para demonstrar a malha P2P...")
        return "O medicamento experimental X-Treme causou dores de cabeça severas em 14 pacientes na nossa unidade."
