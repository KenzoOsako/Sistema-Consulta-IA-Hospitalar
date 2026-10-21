# Federated Science Architecture (Local-First P2P)

> **Protótipo experimental, não homologado para prontuários ou uso clínico.**
> NER pode deixar de detectar identificadores. Criptografia de transporte e
> substituição de entidades não garantem anonimização nem conformidade legal.

## Limites e bloqueio de falhas

As consultas são sanitizadas antes de abrir uma conexão P2P. Respostas de
qualquer handler passam pela proteção na saída do stream. Se o modelo português,
o sanitizador ou o mecanismo de ruído falhar, a operação é bloqueada; o original
não é usado como fallback. A ingestão também para antes de gerar embeddings se
a sanitização falhar. Texto de entrada, saída e contagens brutas não são usados
como mensagens de diagnóstico desses mecanismos.

O mecanismo de ruído cobre apenas respostas constituídas por uma contagem
inteira não negativa, sob a hipótese de sensibilidade 1. Texto livre passa por
NER, **não por privacidade diferencial**. Não existe orçamento acumulado de
privacidade, controle institucional de peers ou avaliação formal de anonimização
neste protótipo. Não use dados reais. A resposta de demonstração do RAG em falhas
continua sendo simulada, não evidência clínica.

Regressões isoladas, com motores e transporte simulados:

```bash
python -m unittest discover -s tests -v
```

Esses testes verificam o bloqueio das falhas e os pontos de exportação; não
homologam o modelo NER, OpenDP, libp2p ou a qualidade das respostas médicas.

## Visao Geral
Este repositorio explora uma arquitetura federada experimental para analise local de dados sinteticos medicos e cientificos, sob o paradigma "Local-First".

As comunicacoes e a consolidacao do conhecimento inter-hospitalar ocorrem de forma 100% descentralizada (P2P Mesh) utilizando streams TCP multiplexados via `libp2p`. O projeto integra inteligencia artificial generativa (RAG) para consulta de sintomas e prontuarios, acoplada a uma camada experimental de deteccao de entidades (NER) via Microsoft Presidio e ruido para contagens via OpenDP.

## Tecnologias Utilizadas
- Comunicação Descentralizada: `libp2p` (TCP Multiplexing), `Trio` (Assincronicidade).
- Inteligência Artificial (RAG): `LangChain`, `Ollama` (LLaMA 3), `ChromaDB`.
- Privacy Shield: `Microsoft Presidio` (Anonimizacao via NER - Spacy), `OpenDP` (Privacidade Diferencial).

## Arquitetura do Sistema

1. Nos Descentralizados (Hospitais): Cada no opera de forma independente em seu ambiente local, contendo sua propria base de dados vetorial e motor RAG. O isolamento e a seguranca operacional precisam ser configurados e avaliados separadamente.
2. Privacy Shield: Antes de qualquer requisicao ser distribuida para a rede, o Microsoft Presidio analisa a string e substitui entidades detectadas. Identificadores nao reconhecidos podem permanecer no texto.
3. P2P Mesh Network: A conexao inter-institucional dispensa APIs REST tradicionais, utilizando a infraestrutura peer-to-peer criptografada do `libp2p`.
4. Mecanismo de Tolerancia a Falhas: Caso o motor de inferencia local (Ollama) falhe por limitacoes de hardware (ex: ausencia de instrucoes AVX), a camada de rede se mantem resiliente atraves de um fallback responsivo, produzindo uma resposta simulada. Isso nao comprova disponibilidade do sistema nem resposta clinica valida.

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

## Verificação contínua

A [CI](.github/workflows/ci.yml) usa Python 3.12 e executa os testes isolados com a biblioteca padrão, sem baixar modelos nem acessar dados clínicos. Alterações em sanitização, ruído ou transporte devem preservar os testes de bloqueio e de tráfego legítimo. Integrações reais continuam exigindo um ambiente separado com dados sintéticos.
