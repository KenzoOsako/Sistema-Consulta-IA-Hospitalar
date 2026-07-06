# Federated Science Architecture (Local-First P2P)

## 📌 Visão Geral
Este repositório contém a implementação definitiva de uma Arquitetura Federada focada em Privacidade para análise de dados médicos e científicos. A solução foi projetada sob o paradigma "Local-First", garantindo que os dados sensíveis nunca precisem trafegar para servidores centralizados.

As comunicações e a consolidação do conhecimento inter-hospitalar ocorrem de forma 100% descentralizada (P2P Mesh) utilizando streams TCP multiplexados via `libp2p`. O projeto integra inteligência artificial generativa (RAG) para consulta de sintomas e prontuários, acoplada a uma camada rigorosa de higienização de dados (NER) via Microsoft Presidio e Privacidade Diferencial (OpenDP).

## 🛠️ Tecnologias Utilizadas
- **Comunicação Descentralizada:** `libp2p` (TCP Multiplexing), `Trio` (Assincronicidade).
- **Inteligência Artificial (RAG):** `LangChain`, `Ollama` (LLaMA 3), `ChromaDB`.
- **Privacy Shield:** `Microsoft Presidio` (Anonimização via NER - Spacy), `OpenDP` (Privacidade Diferencial).

## 🏗️ Arquitetura do Sistema

1. **Nós Descentralizados (Hospitais):** Cada nó opera de forma independente em um ambiente seguro, contendo sua própria base de dados vetorial e motor RAG.
2. **Privacy Shield:** Antes de qualquer requisição ser distribuída para a rede, o Microsoft Presidio analisa a string e remove quaisquer Informações de Identificação Pessoal (PII).
3. **P2P Mesh Network:** A conexão inter-institucional dispensa APIs REST tradicionais, utilizando a infraestrutura peer-to-peer criptografada do `libp2p`.
4. **Mecanismo de Tolerância a Falhas:** Caso o motor de inferência local (Ollama) falhe por limitações de hardware (ex: ausência de instruções AVX), a camada de rede se mantém resiliente através de um fallback responsivo, garantindo o uptime do ecossistema federado.

## ⚙️ Pré-requisitos e Instalação

O ambiente requer Python instalado, além do modelo de IA local configurado.

1. Instale as dependências fundamentais do Python:
```powershell
pip install -r requirements.txt
```

2. Baixe o modelo linguístico do Spacy (PT-BR) para ativar o motor de higienização de dados (NER):
```powershell
python -m spacy download pt_core_news_sm
```

3. Instale o modelo generativo local via [Ollama](https://ollama.com/) (requer suporte de hardware compatível). Deixe o serviço rodando em segundo plano:
```powershell
ollama run llama3
```

## 🚀 Como Executar

O projeto inclui um script orquestrador de demonstração que inicializa instâncias múltiplas (Nó A e Nó B), formata a malha de rede, e disponibiliza o terminal de consulta.

Inicie a aplicação:
```powershell
python demo.py
```

### 💻 Interagindo com o Terminal Federado
Ao rodar a malha, você obterá acesso ao prompt interativo do Pesquisador:
```text
👨‍⚕️ [Você - Hosp. B]:
```
Digite sintomas ou dúvidas clínicas (ex: *"paciente masculino relata dores crônicas na lombar"*). 

**Fluxo de Processamento:**
1. A rede consultará os bancos vetoriais locais (RAG).
2. Se necessário, os sintomas são higienizados (remoção de entidades sensíveis).
3. A query anônima trafega pelo túnel TCP criptografado.
4. Outros nós da malha processam o raciocínio clínico com seus próprios LLMs.
5. A resposta consolidada retorna de forma federada ao pesquisador inicial.
