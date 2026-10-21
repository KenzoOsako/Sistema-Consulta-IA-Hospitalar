from functools import lru_cache

from .errors import PrivacyProtectionError


@lru_cache(maxsize=1)
def _engines():
    # Não usar um modelo em outro idioma se o modelo português estiver ausente.
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    from presidio_anonymizer import AnonymizerEngine

    provider = NlpEngineProvider(nlp_configuration={
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "pt", "model_name": "pt_core_news_sm"}],
    })
    analyzer = AnalyzerEngine(
        nlp_engine=provider.create_engine(), supported_languages=["pt"]
    )
    return analyzer, AnonymizerEngine()


def sanitize_text(text: str) -> str:
    """Aplica NER em português ou bloqueia, sem devolver o original em erro."""
    if not isinstance(text, str):
        raise PrivacyProtectionError("Texto inválido para sanitização.")
    if not text:
        return ""
    try:
        analyzer, anonymizer = _engines()
        results = analyzer.analyze(text=text, entities=None, language="pt")
        result = anonymizer.anonymize(text=text, analyzer_results=results)
        if not isinstance(result.text, str):
            raise ValueError("Resultado inválido")
        return result.text
    except Exception:
        # Erros de terceiros podem conter a entrada. Não os exportar.
        raise PrivacyProtectionError("Sanitização indisponível; operação bloqueada.") from None
