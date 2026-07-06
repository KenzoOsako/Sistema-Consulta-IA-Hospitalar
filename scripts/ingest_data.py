import os
import sys
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

# Garante que possamos importar os módulos do node
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from node.rag_engine import get_embeddings
from node.privacy.sanitizer import sanitize_text

def ingest_text(text: str, db_dir: str):
    """
    Ingere um texto no banco de dados vetorial.
    Obrigatoriamente aplica o NER Sanitizer ANTES de converter para embedding.
    """
    print("-" * 50)
    print(f"Texto Original (COMPROMETEDOR):\n{text}\n")
    
    # 1. Privacy Shield: Sanitização
    safe_text = sanitize_text(text)
    print(f"Texto Sanitizado (SEGURO PARA DB):\n{safe_text}\n")
    
    # 2. Quebra de Texto
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_text(safe_text)
    
    # 3. Gerar Embeddings e Salvar
    # Forçamos a variável de ambiente para o diretório atual da ingestão
    os.environ["CHROMA_PERSIST_DIR"] = db_dir
    embeddings = get_embeddings()
    
    db = Chroma.from_texts(texts=chunks, embedding=embeddings, persist_directory=db_dir)
    print(f"-> Ingestão concluída. Banco salvo em {db_dir}")
    print("-" * 50)

if __name__ == "__main__":
    # Dados fictícios para teste P2P
    
    # Dados que ficarão apenas no Hospital A
    doc_a = (
        "Prontuário 1023: O paciente João da Silva, nascido em 15/04/1980, CPF 123.456.789-00, "
        "relatou dores agudas no estômago após ingerir o medicamento experimental X-Treme. "
        "Ele foi diagnosticado com a mutação genética BRCA1."
    )
    
    # Dados que ficarão apenas no Hospital B
    doc_b = (
        "Prontuário 4099: A paciente Maria Oliveira, residente na Avenida Paulista 1000, São Paulo, "
        "também apresentou náuseas crônicas e arritmia com o uso contínuo do medicamento X-Treme. "
        "Testes de sequenciamento confirmaram a mutação BRCA1."
    )
    
    print("=== INICIANDO INGESTÃO DE DADOS (COM PRIVACY SHIELD) ===\n")
    ingest_text(doc_a, "./data/hospital_a_db")
    ingest_text(doc_b, "./data/hospital_b_db")
