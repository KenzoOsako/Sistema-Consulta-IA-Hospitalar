"""Inference failures never produce clinical claims or export provider errors."""
import importlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from test_privacy import network


def load_rag():
    names = ['langchain_community', 'langchain_community.llms',
             'langchain_community.vectorstores', 'langchain_community.embeddings',
             'langchain_classic', 'langchain_classic.chains',
             'langchain_core', 'langchain_core.prompts']
    modules = {name: types.ModuleType(name) for name in names}
    for name, attribute in [('langchain_community.llms', 'Ollama'),
                            ('langchain_community.vectorstores', 'Chroma'),
                            ('langchain_community.embeddings', 'OllamaEmbeddings'),
                            ('langchain_classic.chains', 'RetrievalQA'),
                            ('langchain_core.prompts', 'PromptTemplate')]:
        setattr(modules[name], attribute, MagicMock())
    with patch.dict(sys.modules, modules):
        return importlib.import_module('node.rag_engine')


rag = load_rag()


class RagFailureTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        for target in ['get_vector_db', 'get_llm', 'PromptTemplate', 'RetrievalQA']:
            patcher = patch.object(rag, target)
            setattr(self, target, patcher.start())
            self.addCleanup(patcher.stop)
        self.chain = self.RetrievalQA.from_chain_type.return_value

    def test_inference_failure_returns_only_generic_unavailability(self):
        self.chain.invoke.side_effect = RuntimeError('synthetic-private-context')
        with patch('builtins.print') as output:
            self.assertEqual(rag.query_local_rag('synthetic-query'), rag.RAG_UNAVAILABLE)
        output.assert_not_called()

    def test_initialization_failure_is_also_unavailable(self):
        self.get_vector_db.side_effect = RuntimeError('synthetic-private-context')
        self.assertEqual(rag.query_local_rag('synthetic-query'), rag.RAG_UNAVAILABLE)
        self.chain.invoke.assert_not_called()

    def test_valid_answer_is_preserved_and_invalid_result_is_blocked(self):
        self.chain.invoke.return_value = {'result': 'synthetic-answer'}
        self.assertEqual(rag.query_local_rag('synthetic-query'), 'synthetic-answer')
        self.chain.invoke.assert_called_once_with({'query': 'synthetic-query'})
        for result in [{}, {'result': None}, {'result': 123}]:
            self.chain.invoke.return_value = result
            self.assertEqual(rag.query_local_rag('synthetic-query'), rag.RAG_UNAVAILABLE)

    async def test_p2p_inference_failure_exports_no_fabricated_answer(self):
        self.chain.invoke.side_effect = RuntimeError('synthetic-private-context')
        host = MagicMock()
        host.get_addrs.return_value = []
        node = network.FederatedP2PNode(8001)
        stream = SimpleNamespace(muxed_conn=SimpleNamespace(peer_id='synthetic'),
            read=AsyncMock(side_effect=[b'q', b'\n']), write=AsyncMock(), close=AsyncMock())
        with patch.object(network, 'new_host', return_value=host), patch('builtins.print'):
            await node.start(rag.query_local_rag)
            handler = host.set_stream_handler.call_args.args[1]
            with patch.object(network, 'sanitize_text', side_effect=lambda text: text):
                await handler(stream)
        stream.write.assert_awaited_once_with(rag.RAG_UNAVAILABLE.encode() + b'\n')
        stream.close.assert_awaited_once()
