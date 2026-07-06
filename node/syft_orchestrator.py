import os
import trio
from .network.p2p_node import FederatedP2PNode
from .rag_engine import query_local_rag
from .privacy.sanitizer import sanitize_text
from .privacy.differential import add_noise

class AntigravityOrchestrator:
    """
    O cérebro do nó hospitalar. Substitui a antiga API REST centralizada.
    Gerencia a tomada de decisão (RAG Local vs Rede Federada P2P) e as camadas
    de Privacidade Diferencial e NER.
    
    Em arquiteturas puras, isso atuaria como o Domain Node do PySyft.
    """
    def __init__(self, port: int, peer_maddr: str = ""):
        self.port = port
        self.peer_maddr = peer_maddr
        self.p2p_node = FederatedP2PNode(port)
        
    def handle_p2p_query(self, query_text: str) -> str:
        """
        Callback ativado quando recebemos uma query criptografada pela malha libp2p.
        Aqui reside o Privacy Shield (Privacidade Diferencial).
        """
        print(f"[Orchestrator] Processando query remota P2P...")
        answer = query_local_rag(query_text)
        
        # Privacy Shield: Differential Privacy
        if answer.strip().isdigit():
            val = int(answer.strip())
            noisy_val = add_noise(val, epsilon=0.5)
            print(f"[Privacy Shield] Ruído DP aplicado. Real: {val}, Informado à rede: {noisy_val}")
            answer = str(noisy_val)
            
        return answer
        
    async def start(self):
        # Inicia a rede libp2p passando o manipulador RAG local
        await self.p2p_node.start(self.handle_p2p_query)
        
    async def query_system(self, query_text: str):
        """
        O pesquisador local envia uma pergunta pela interface do terminal/UI.
        """
        print(f"\n[Pesquisador] Dúvida: {query_text}")
        
        # 1. RAG Local (ChromaDB + Ollama)
        print("[Orchestrator] Buscando nos registros da Instituição (Local)...")
        local_ans = query_local_rag(query_text)
        print(f"\n[Resposta Local]\n{local_ans}\n")
        
        # 2. Busca Federada
        if self.peer_maddr:
            print("[Orchestrator] Enviando consulta para a Malha P2P Federada...")
            # Sanitiza a query (NER - Remoção de Nomes) ANTES de ir para a rede
            safe_query = sanitize_text(query_text)
            print(f"[Privacy Shield] Dado anonimizado na rede: '{safe_query}'")
            
            p2p_ans = await self.p2p_node.query_peer(self.peer_maddr, safe_query)
            print(f"\n[Conhecimento Federado (Outros Hospitais)]\n{p2p_ans}\n")

async def main():
    port = int(os.getenv("P2P_PORT", "8001"))
    peer = os.getenv("PEER_MADDR", "")
    
    orchestrator = AntigravityOrchestrator(port, peer)
    
    async with trio.open_nursery() as nursery:
        nursery.start_soon(orchestrator.p2p_node.start, orchestrator.handle_p2p_query)
        await trio.sleep(1)
        
        print("\n[Terminal] Sistema Operacional. Digite sua pergunta (ou 'sair'):")
        while True:
            query = await trio.to_thread.run_sync(input, "> ")
            if query.lower().strip() == 'sair':
                if orchestrator.p2p_node.host:
                    await orchestrator.p2p_node.host.close()
                nursery.cancel_scope.cancel()
                break
            await orchestrator.query_system(query)

if __name__ == "__main__":
    trio.run(main)
