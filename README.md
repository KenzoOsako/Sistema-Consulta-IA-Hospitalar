# Federated Science Architecture (Local-First P2P)

Este projeto implementa uma Arquitetura Federada de Produção focada em Privacidade para dados médicos e científicos.
As comunicações ocorrem de forma 100% descentralizada (P2P Mesh via libp2p TCP Multiplexed streams), RAG local usando LangChain + Ollama, e anonimização rigorosa via Microsoft Presidio (NER).

## 🚀 Como Iniciar a Rede Mesh P2P

Ao invés de rodarmos servidores HTTP ou APIs REST centralizadas, levantaremos Nós em uma malha criptografada P2P nativa, garantindo que os dados viajem anonimizados diretamente de nó para nó.

### 1. Preparar a Base (Obrigatório)

Primeiro, instale as dependências Python:
```powershell
pip install -r requirements.txt
```

Para o sistema de anonimização (Privacy Shield / NER) funcionar, baixe o pacote do idioma português:
```powershell
python -m spacy download pt_core_news_sm
```

Instale o [Ollama](https://ollama.com/download) (necessário suporte a AVX) e rode `ollama run llama3` no terminal em segundo plano.

### 2. Rodar a Simulação Interativa (Orquestrador)

Nós preparamos um script `demo.py` que sobe automaticamente dois Hospitais (Nó A e Nó B), conecta as redes e abre um terminal para você interagir.

No seu terminal, rode:
```powershell
python demo.py
```

### 3. Consultando a Malha (Terminal P2P)

O próprio terminal exibirá:
`👨‍⚕️ [Você - Hosp. B]:`

Digite qualquer sintoma ou dúvida médica. O sistema irá:
1. Buscar no banco de dados vetorial local (RAG / ChromaDB).
2. Se não encontrar o suficiente, o **Presidio** higieniza sua frase (retirando qualquer dado pessoal).
3. Envia o dado anonimizado via TCP stream (`libp2p`) para os outros hospitais na malha (ex: Nó A).
4. O Nó A responde sem saber quem é o paciente.
5. Você recebe a resposta consolidada na sua tela.

*Nota: Se a sua máquina local não suportar a inferência pesada do LLaMA 3, o sistema de Inteligência Artificial entrará em modo Fallback e responderá normalmente à requisição P2P para garantir o uptime da rede.*
