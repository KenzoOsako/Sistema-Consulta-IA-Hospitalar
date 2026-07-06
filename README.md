# Federated Science Architecture (Local-First P2P)

## Visao Geral
Este repositorio contem a implementacao definitiva de uma Arquitetura Federada focada em Privacidade para analise de dados medicos e cientificos. A solucao foi projetada sob o paradigma "Local-First", garantindo que os dados sensiveis nunca precisem trafegar para servidores centralizados.

As comunicacoes e a consolidacao do conhecimento inter-hospitalar ocorrem de forma 100% descentralizada (P2P Mesh) utilizando streams TCP multiplexados via `libp2p`. O projeto integra inteligencia artificial generativa (RAG) para consulta de sintomas e prontuarios, acoplada a uma camada rigorosa de higienizacao de dados (NER) via Microsoft Presidio e Privacidade Diferencial (OpenDP).

## Tecnologias Utilizadas
- Comunicação Descentralizada: `libp2p` (TCP Multiplexing), `Trio` (Assincronicidade).
- Inteligência Artificial (RAG): `LangChain`, `Ollama` (LLaMA 3), `ChromaDB`.
- Privacy Shield: `Microsoft Presidio` (Anonimizacao via NER - Spacy), `OpenDP` (Privacidade Diferencial).

## Arquitetura do Sistema

1. Nos Descentralizados (Hospitais): Cada no opera de forma independente em um ambiente seguro, contendo sua propria base de dados vetorial e motor RAG.
2. Privacy Shield: Antes de qualquer requisicao ser distribuida para a rede, o Microsoft Presidio analisa a string e remove quaisquer Informacoes de Identificacao Pessoal (PII).
3. P2P Mesh Network: A conexao inter-institucional dispensa APIs REST tradicionais, utilizando a infraestrutura peer-to-peer criptografada do `libp2p`.
4. Mecanismo de Tolerancia a Falhas: Caso o motor de inferencia local (Ollama) falhe por limitacoes de hardware (ex: ausencia de instrucoes AVX), a camada de rede se mantem resiliente atraves de um fallback responsivo, garantindo o uptime do ecossistema federado.

## Pre-requisitos e Instalacao

O ambiente requer Python instalado, alem do modelo de IA local configurado.

1. Instale as dependencias fundamentais do Python:
```powershell
pip install -r requirements.txt
```

2. Baixe o modelo linguistico do Spacy (PT-BR) para ativar o motor de higienizacao de dados (NER):
```powershell
python -m spacy download pt_core_news_sm
```

3. Instale o modelo generativo local via [Ollama](https://ollama.com/) (requer suporte de hardware compativel). Deixe o servico rodando em segundo plano:
```powershell
ollama run llama3
```

## Guia de Execucao

O projeto inclui um script orquestrador de demonstracao que inicializa instancias multiplas (No A e No B), formata a malha de rede e disponibiliza o terminal de consulta.

Inicie a aplicacao no diretorio raiz:
```powershell
python demo.py
```

### Terminal de Consulta Interativa
Ao iniciar o sistema de malha, o console habilitara um prompt interativo de Pesquisa:
```text
[Pesquisador - Hospital B]:
```
Digite sintomas ou duvidas clinicas.

Fluxo de Processamento:
1. A rede consultara os bancos vetoriais locais (RAG).
2. Se necessario, os dados sao higienizados pelo Privacy Shield (remocao de entidades sensiveis).
3. A query anonima trafega pelo tunel TCP criptografado P2P.
4. Outros nos da malha processam o raciocinio clinico com seus respectivos LLMs.
5. A resposta consolidada retorna de forma federada ao nodo solicitante.
