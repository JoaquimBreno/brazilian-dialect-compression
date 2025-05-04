from typing import List, Any
import os
import sys

# Garante que os módulos possam ser encontrados diretamente
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(current_dir)))

from ppm.models.ppm_model import PPMModel

class PPMProcessor:
    """Gerencia o processamento do texto usando o modelo PPM."""
    
    def __init__(self, k_max: int = 2, verbose: bool = False):
        self.model = PPMModel(k_max, verbose)
        self.discarded_chars = []  # Pilha de caracteres
        self.encoded_sequence = []  # Sequência codificada
        self.verbose = verbose
    
    def process_text(self, text: str) -> List[Any]:
        """Processa o texto completo e retorna a sequência codificada."""
        for char in text:
            self.process_character(char)
        return self.get_encoded_sequence()
    
    def process_character(self, char: str) -> None:
        """Processa um único caractere."""
        # Processa o caractere no modelo
        self.model.process_character(char, self.discarded_chars)
        
        # Atualiza a pilha de caracteres descartados
        self.discarded_chars.insert(0, char)
        
        if self.verbose:
            # print("Array descartados:", self.discarded_chars)
            pass
        
        # Limpa os caracteres ignorados
        self.model.ignore_chars.clear()
        
        # Atualiza a sequência codificada
        self.encoded_sequence = self.model.get_encoded_bits()
    
    def get_encoded_sequence(self) -> List[Any]:
        """Retorna a sequência codificada."""
        return self.encoded_sequence 