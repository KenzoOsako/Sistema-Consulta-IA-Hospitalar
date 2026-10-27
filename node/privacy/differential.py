import math

from .errors import PrivacyProtectionError


def add_noise(value: int, epsilon: float = 1.0) -> int:
    """Perturba uma contagem com sensibilidade 1; erros não liberam o original."""
    if type(value) is not int or value < 0:
        raise PrivacyProtectionError("Contagem inválida.")
    if not isinstance(epsilon, (int, float)) or isinstance(epsilon, bool):
        raise PrivacyProtectionError("Epsilon inválido.")
    if not math.isfinite(epsilon) or epsilon <= 0:
        raise PrivacyProtectionError("Epsilon inválido.")
    try:
        import opendp.prelude as dp

        dp.enable_features("contrib")
        space = dp.atom_domain(T=int), dp.absolute_distance(T=int)
        measurement = space >> dp.m.then_base_discrete_laplace(scale=1.0 / epsilon)
        result = measurement(value)
        if type(result) is not int:
            raise ValueError("Resultado inválido")
        return max(0, result)
    except Exception:
        raise PrivacyProtectionError("Privacidade diferencial indisponível; operação bloqueada.") from None


def apply_dp_to_text(text: str) -> str:
    """Não há mecanismo de privacidade diferencial de texto livre implementado."""
    raise PrivacyProtectionError("Privacidade diferencial de texto livre não implementada.")
