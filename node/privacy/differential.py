import opendp.prelude as dp

# Habilita features experimentais/contrib do OpenDP
try:
    dp.enable_features("contrib")
except Exception as e:
    print(f"Aviso: OpenDP não inicializou corretamente. {e}")

def add_noise(value: int, epsilon: float = 1.0) -> int:
    """
    Adiciona ruído Diferencialmente Privado a uma contagem (agregação).
    Usamos o mecanismo de Laplace discreto para valores inteiros.
    
    A Sensibilidade é 1 (a adição ou remoção de um paciente altera a contagem em 1).
    O Scale do ruído = Sensibilidade / Epsilon.
    """
    try:
        # Define o domínio e a métrica
        space = dp.atom_domain(T=int), dp.absolute_distance(T=int)
        
        # Cria o mecanismo
        scale = 1.0 / epsilon
        meas = space >> dp.m.then_base_discrete_laplace(scale=scale)
        
        # Aplica o ruído e garante que não seja negativo (para contagens reais)
        noisy_value = meas(value)
        return max(0, noisy_value)
    except Exception as e:
        print(f"Erro ao aplicar Privacidade Diferencial: {e}")
        return value

def apply_dp_to_text(text: str) -> str:
    """
    Função utilitária que poderia ler um texto, extrair números e injetar ruído.
    No nosso MVP, o DP será aplicado primariamente nos endpoints numéricos agregados.
    Se a resposta for puramente textual descritiva, o LLM a gera, mas números 
    são passados por add_noise().
    """
    return text
