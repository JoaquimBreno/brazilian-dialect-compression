from collections import defaultdict
from typing import Set

class Context:
    """Representa um contexto no modelo PPM."""
    
    def __init__(self):
        self.char_counts = defaultdict(int)
    
    def add_character(self, char: str):
        """Adiciona um caractere ao contexto ou incrementa sua contagem."""
        self.char_counts[char] += 1
    
    def remove_character(self, char: str):
        """Remove um caractere do contexto."""
        if char in self.char_counts:
            del self.char_counts[char]
    
    def get_characters(self) -> Set[str]:
        """Retorna o conjunto de caracteres neste contexto."""
        return set(self.char_counts.keys())
    
    def contains(self, char: str) -> bool:
        """Verifica se um caractere está presente no contexto."""
        return char in self.char_counts
    
    def get_count(self, char: str) -> int:
        """Retorna a contagem de um caractere específico."""
        return self.char_counts.get(char, 0) 