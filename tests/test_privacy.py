"""Regressões isoladas: sem prontuários, modelos, rede ou banco reais."""
import importlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from node.privacy.errors import PrivacyProtectionError
from node.privacy.sanitizer import sanitize_text
from node.privacy.differential import add_noise, apply_dp_to_text


class SanitizerTests(unittest.TestCase):
    def test_failure_does_not_return_or_print_input(self):
        analyzer = MagicMock()
        analyzer.analyze.side_effect = RuntimeError("synthetic-sensitive-text")
        with patch('node.privacy.sanitizer._engines', return_value=(analyzer, MagicMock())):
            with patch('builtins.print') as output:
                with self.assertRaises(PrivacyProtectionError) as error:
                    sanitize_text('synthetic-sensitive-text')
        self.assertNotIn('synthetic-sensitive-text', str(error.exception))
        output.assert_not_called()

    def test_missing_model_blocks(self):
        with patch('node.privacy.sanitizer._engines', side_effect=RuntimeError):
            with self.assertRaises(PrivacyProtectionError):
                sanitize_text('synthetic text')

    def test_success_returns_anonymizer_output(self):
        analyzer, anonymizer = MagicMock(), MagicMock()
        anonymizer.anonymize.return_value = SimpleNamespace(text='<PERSON>')
        with patch('node.privacy.sanitizer._engines', return_value=(analyzer, anonymizer)):
            self.assertEqual(sanitize_text('synthetic name'), '<PERSON>')
        analyzer.analyze.assert_called_once_with(text='synthetic name', entities=None, language='pt')

    def test_empty_input_does_not_load_model(self):
        with patch('node.privacy.sanitizer._engines') as engines:
            self.assertEqual(sanitize_text(''), '')
        engines.assert_not_called()


class DifferentialTests(unittest.TestCase):
    def test_invalid_parameters_block(self):
        for value, epsilon in [(True, 1), (-1, 1), (1, 0), (1, -1), (1, float('nan')), (1, float('inf')), (1, True)]:
            with self.subTest(value=value, epsilon=epsilon):
                with self.assertRaises(PrivacyProtectionError):
                    add_noise(value, epsilon)

    def test_missing_engine_never_returns_original(self):
        with patch.dict(sys.modules, {'opendp': None, 'opendp.prelude': None}):
            with self.assertRaises(PrivacyProtectionError):
                add_noise(123)

    def test_text_is_not_misrepresented_as_differentially_private(self):
        with self.assertRaises(PrivacyProtectionError):
            apply_dp_to_text('a count of 123')

    def test_success_uses_measurement(self):
        class Measurement:
            def __rrshift__(self, space):
                return lambda value: 7
        parent, dp = types.ModuleType('opendp'), types.ModuleType('opendp.prelude')
        parent.prelude = dp
        dp.enable_features = MagicMock()
        dp.atom_domain = dp.absolute_distance = lambda **kwargs: None
        dp.m = SimpleNamespace(then_base_discrete_laplace=lambda **kwargs: Measurement())
        with patch.dict(sys.modules, {'opendp': parent, 'opendp.prelude': dp}):
            self.assertEqual(add_noise(123, 0.5), 7)


def load_network():
    """Substitui somente dependências de transporte, mantendo o código da aplicação."""
    names = ['trio', 'libp2p', 'libp2p.network', 'libp2p.network.stream',
             'libp2p.network.stream.net_stream', 'libp2p.crypto', 'libp2p.crypto.rsa',
             'libp2p.peer', 'libp2p.peer.peerinfo', 'multiaddr']
    modules = {name: types.ModuleType(name) for name in names}
    modules['trio'].sleep_forever = AsyncMock()
    modules['libp2p'].new_host = MagicMock()
    modules['libp2p.network.stream.net_stream'].INetStream = object
    modules['libp2p.crypto.rsa'].create_new_key_pair = MagicMock()
    modules['libp2p.peer.peerinfo'].info_from_p2p_addr = lambda value: SimpleNamespace(peer_id='peer')
    modules['multiaddr'].Multiaddr = lambda value: value
    with patch.dict(sys.modules, modules):
        return importlib.import_module('node.network.p2p_node')


network = load_network()


class NetworkBoundaryTests(unittest.IsolatedAsyncioTestCase):
    async def test_failed_outgoing_sanitization_does_not_connect(self):
        node = network.FederatedP2PNode(8001)
        node.host = MagicMock()
        with patch.object(network, 'sanitize_text', side_effect=PrivacyProtectionError):
            self.assertEqual(await node.query_peer('peer', 'raw input'), network.PRIVACY_BLOCKED)
        node.host.connect.assert_not_called()

    async def test_legitimate_outgoing_query_uses_sanitized_text(self):
        node = network.FederatedP2PNode(8001)
        stream = SimpleNamespace(write=AsyncMock(), read=AsyncMock(side_effect=[b'o', b'k', b'\n']), close=AsyncMock())
        node.host = SimpleNamespace(connect=AsyncMock(), new_stream=AsyncMock(return_value=stream))
        with patch.object(network, 'sanitize_text', return_value='<PERSON>'):
            self.assertEqual(await node.query_peer('peer', 'raw input'), 'ok')
        stream.write.assert_awaited_once_with(b'<PERSON>\n')

    async def invoke_handler(self, answer, sanitizer=None, noise=None):
        host = MagicMock()
        host.get_addrs.return_value = []
        node = network.FederatedP2PNode(8001)
        stream = SimpleNamespace(
            muxed_conn=SimpleNamespace(peer_id='peer'),
            read=AsyncMock(side_effect=[b'q', b'\n']), write=AsyncMock(), close=AsyncMock())
        with patch.object(network, 'new_host', return_value=host):
            await node.start(lambda query: answer)
        handler = host.set_stream_handler.call_args.args[1]
        with patch.object(network, 'sanitize_text', sanitizer or MagicMock(return_value='<PERSON>')):
            with patch.object(network, 'add_noise', noise or MagicMock(return_value=7)):
                await handler(stream)
        stream.close.assert_awaited_once()
        return stream.write.call_args.args[0]

    async def test_text_response_is_sanitized_for_any_handler(self):
        self.assertEqual(await self.invoke_handler('raw private answer'), b'<PERSON>\n')

    async def test_failed_response_sanitization_exports_only_generic_error(self):
        result = await self.invoke_handler('raw private answer', sanitizer=MagicMock(side_effect=PrivacyProtectionError))
        self.assertEqual(result, network.PRIVACY_BLOCKED.encode() + b'\n')

    async def test_numeric_response_uses_noise(self):
        self.assertEqual(await self.invoke_handler('123'), b'7\n')

    async def test_failed_noise_does_not_export_raw_count(self):
        result = await self.invoke_handler('123', noise=MagicMock(side_effect=PrivacyProtectionError))
        self.assertEqual(result, network.PRIVACY_BLOCKED.encode() + b'\n')


if __name__ == '__main__':
    unittest.main()
