import trio
import os
import sys

# Garante que possamos importar os módulos do node
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from node.syft_orchestrator import AntigravityOrchestrator

async def main():
    print("=== Iniciando Simulação Definitiva P2P Local-First ===\n")
    
    # Configurando persistência para os bancos
    os.environ["CHROMA_PERSIST_DIR"] = "./data/hospital_a_db"
    node_a = AntigravityOrchestrator(8001, "")
    
    async with trio.open_nursery() as nursery:
        # Inicia a rede do Nó A em background
        nursery.start_soon(node_a.p2p_node.start, node_a.handle_p2p_query)
        await trio.sleep(3) # Aguarda libp2p inicializar
        
        # Pega o endereço real gerado para o Nó A
        node_a_addr = ""
        if node_a.p2p_node.host:
            # Montagem manual garantida
            node_a_addr = f"/ip4/127.0.0.1/tcp/{node_a.p2p_node.port}/p2p/{node_a.p2p_node.peer_id}"
                
        print(f"\n[DEMO] Hospital A inicializado. Multiaddr Mapeado: {node_a_addr}")
        
        # Configurando persistência para o banco do Nó B
        os.environ["CHROMA_PERSIST_DIR"] = "./data/hospital_b_db"
        node_b = AntigravityOrchestrator(8002, node_a_addr)
        
        # Inicia a rede do Nó B conectada ao Nó A
        nursery.start_soon(node_b.p2p_node.start, node_b.handle_p2p_query)
        await trio.sleep(2)
        print("\n[DEMO] Hospital B inicializado e conectado à Malha.")
        
        # Dá um tempinho para as conexões serem firmadas
        await trio.sleep(3)
        
        print("\n" + "="*50)
        print("💡 TERMINAL INTERATIVO DO PESQUISADOR (HOSPITAL B)")
        print("Digite 'sair' para encerrar a malha.")
        print("="*50 + "\n")
        
        while True:
            # Lê o input do usuário sem bloquear o trio
            pergunta = await trio.to_thread.run_sync(input, "👨‍⚕️ [Você - Hosp. B]: ")
            if pergunta.strip().lower() in ['sair', 'exit', 'quit']:
                break
                
            if not pergunta.strip():
                continue
                
            # O Orquestrador cuida de tudo: RAG Local, Anonimização e Busca P2P
            await node_b.query_system(pergunta)
            print("-" * 50 + "\n")
            
        print("\n[DEMO] Simulação concluída. Desligando a rede...\n")
        
        if node_a.p2p_node.host:
            await node_a.p2p_node.host.close()
        if node_b.p2p_node.host:
            await node_b.p2p_node.host.close()
        nursery.cancel_scope.cancel()

if __name__ == "__main__":
    trio.run(main)
