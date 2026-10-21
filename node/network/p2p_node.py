import trio
import re
from libp2p import new_host
from libp2p.network.stream.net_stream import INetStream
from libp2p.crypto.rsa import create_new_key_pair
from libp2p.peer.peerinfo import info_from_p2p_addr
from multiaddr import Multiaddr
from ..privacy.sanitizer import sanitize_text
from ..privacy.differential import add_noise
from ..privacy.errors import PrivacyProtectionError

PROTOCOL_ID = "/med-federated/1.0.0"
PRIVACY_BLOCKED = "[Consulta bloqueada: proteção de privacidade indisponível.]"


def protect_response(response: str) -> str:
    if not isinstance(response, str):
        raise PrivacyProtectionError("Resposta inválida.")
    # A DP existente cobre contagens inteiras, não números em prosa.
    if re.fullmatch(r"[0-9]+", response.strip()):
        try:
            return str(add_noise(int(response.strip()), epsilon=0.5))
        except (ValueError, OverflowError):
            raise PrivacyProtectionError("Contagem inválida.") from None
    return sanitize_text(response)

class FederatedP2PNode:
    """
    Nó de comunicação descentralizada usando libp2p puro.
    Substitui APIs REST centralizadas por túneis streams seguros.
    """
    def __init__(self, port: int):
        self.port = port
        self.host = None
        self.peer_id = None
        
    async def start(self, query_handler):
        # 1. Identidade Criptográfica (Chaves RSA locais)
        key_pair = create_new_key_pair()
        
        # 2. Inicializa o Host (Nó P2P)
        self.host = new_host(key_pair=key_pair)
        self.peer_id = self.host.get_id().pretty()
        
        # 3. Define o manipulador do protocolo federado
        async def stream_handler(stream: INetStream):
            print(f"\n[P2P] Conexao recebida de: {stream.muxed_conn.peer_id}")
            
            # Lê a requisição P2P até a quebra de linha para não travar no read()
            read_bytes = b""
            while True:
                chunk = await stream.read(1)
                if chunk == b'\n' or not chunk:
                    break
                read_bytes += chunk
                
            query_str = read_bytes.decode('utf-8')
            
            # Processa usando o handler injetado (Syft Orchestrator)
            try:
                # Protege a saída de qualquer handler antes da escrita no stream.
                response_str = protect_response(query_handler(query_str))
            except PrivacyProtectionError:
                response_str = PRIVACY_BLOCKED
            try:
                await stream.write(response_str.encode('utf-8') + b'\n')
            finally:
                await stream.close()
            
        self.host.set_stream_handler(PROTOCOL_ID, stream_handler)
        
        listen_addr = Multiaddr(f"/ip4/127.0.0.1/tcp/{self.port}")
        
        # 4. Inicia escuta com o gerenciador de contexto oficial do libp2p
        async with self.host.run(listen_addrs=[listen_addr]):
            print(f"\n[OK] No Federado (Producao) Iniciado na porta {self.port}")
            print(f"[+] O Endereco (Multiaddr) deste no e:")
            for addr in self.host.get_addrs():
                print(f"   {addr}/p2p/{self.peer_id}")
                
            # Mantém a task do servidor viva em background
            await trio.sleep_forever()

            
    async def query_peer(self, peer_maddr_str: str, query_text: str) -> str:
        """
        Envia uma query RAG anonimizada para outro nó da malha P2P.
        """
        # Nenhuma conexão ou escrita ocorre se a sanitização falhar.
        try:
            safe_query = sanitize_text(query_text)
        except PrivacyProtectionError:
            return PRIVACY_BLOCKED
        # Extrai ID do Peer e Maddr
        maddr = Multiaddr(peer_maddr_str)
        info = info_from_p2p_addr(maddr)
        
        try:
            # Estabelece túnel
            await self.host.connect(info)
            # Abre o stream do protocolo
            stream = await self.host.new_stream(info.peer_id, [PROTOCOL_ID])
            
            # Escreve a requisição com quebra de linha
            await stream.write(safe_query.encode('utf-8') + b'\n')
            
            # Aguarda a resposta (lê até quebra de linha)
            read_bytes = b""
            while True:
                chunk = await stream.read(1)
                if chunk == b'\n' or not chunk:
                    break
                read_bytes += chunk
                
            await stream.close()
            return read_bytes.decode('utf-8')
        except Exception:
            return "[Erro P2P: consulta não concluída.]"
