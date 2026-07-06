import os
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

# Configuração para o modelo em Português do spaCy
configuration = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "pt", "model_name": "pt_core_news_sm"}],
}

try:
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()

    analyzer = AnalyzerEngine(
        nlp_engine=nlp_engine, 
        supported_languages=["pt"]
    )
except Exception as e:
    print(f"Aviso: Não foi possível carregar o modelo de NLP pt_core_news_sm. Erro: {e}")
    # Fallback to default
    analyzer = AnalyzerEngine()

anonymizer = AnonymizerEngine()

def sanitize_text(text: str) -> str:
    """
    Recebe um texto cru e mascara todas as entidades sensíveis (PII/PHI).
    Substitui por tokens como <PERSON>, <LOCATION>, etc.
    """
    if not text:
        return text
        
    try:
        # Analisa entidades no texto
        results = analyzer.analyze(text=text, entities=None, language="pt")
        # Mascara entidades baseadas no resultado
        anonymized_result = anonymizer.anonymize(text=text, analyzer_results=results)
        return anonymized_result.text
    except Exception as e:
        print(f"Erro na sanitização: {e}")
        return text
