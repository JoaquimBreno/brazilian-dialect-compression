import string
import math
from typing import Dict, List

from models.context import Context
from utils.encoder import codificar_ppm  # Importando a função


class PPMModel:
    """Modelo principal do PPM (Prediction by Partial Matching)."""

    def __init__(self, k_max: int = 2, verbose: bool = False):
        self.k_max = k_max
        self.structure = {k: {} for k in range(-1, k_max + 1)}
        self.ignore_chars = set()
        self.esc_symbol = 'ç'  # Símbolo de escape (ro)
        self.encoded_bits = []  # Lista para armazenar os bits codificados
        self.verbose = verbose
        self.alphabet = string.ascii_lowercase + "_"
        # self.alphabet = "abcdr"
        self.initialize_alphabet()

    def initialize_alphabet(self):
        """Inicializa o modelo com o alfabeto para k=-1."""
        self.structure[-1]["NO_CONTEXT"] = Context()
        for letra in self.alphabet:
            self.structure[-1]["NO_CONTEXT"].add_character(letra)

    def get_context(self, k: int, context_str: str) -> Context:
        """Retorna o contexto para um determinado k e string de contexto."""
        context_key = context_str if context_str else "NO_CONTEXT"
        # Se não existe o contexto, cria um novo
        if context_key not in self.structure[k]:
            self.structure[k][context_key] = Context()
        return self.structure[k][context_key]

    def is_context_complete(self, context: Context) -> bool:
        """Verifica se um contexto contém todos os símbolos do alfabeto incluindo espaço."""
        alphabet = set(self.alphabet)
        context_chars = context.get_characters()
        return alphabet.issubset(context_chars)

    def process_character(self, char: str, context_stack: List[str]) -> None:
        """Processa um caractere no modelo PPM."""
        element_found = False
        numerador = 0
        denominador = 0
        entropia = 0
        if not context_stack:
            # Caso especial para o primeiro caractere
            # Codifica o caractere no contexto -1
            encoded_bits = codificar_ppm(
                self.structure, -1, "NO_CONTEXT", char, self.ignore_chars, False)
            if encoded_bits:
                # Calcula a probabilidade como tupla (numerador, denominador)
                # pega o contexto -1
                context = self.get_context(-1, "NO_CONTEXT")
                numerador = context.char_counts[char]
                denominador = sum(context.char_counts.values())
                entropia = round(math.log2(numerador/denominador), 4)
                self.encoded_bits.append(
                    (char, -1, "NO_CONTEXT", encoded_bits, (numerador, denominador), entropia))
                if self.verbose:
                    # print(
                    #     f"Codificando '{char}' no contexto -1 com bits: {encoded_bits}")
                    pass

            self.structure[-1]["NO_CONTEXT"].remove_character(char)
            self.get_context(0, "NO_CONTEXT").add_character(char)
            self.get_context(0, "NO_CONTEXT").add_character(self.esc_symbol)
        else:
            stack_size = len(context_stack)
            stack_size = min(stack_size, self.k_max)

            # Verifica cada nível de k, começando pelo maior possível
            for k in range(stack_size, -2, -1):
                if k > 0:
                    context_str = ''.join(context_stack[k-1::-1])
                else:
                    context_str = "NO_CONTEXT"

                context = self.get_context(k, context_str)
                # print(f"Contexto: {context.char_counts}")
                if context.contains(char):  # se o caractere está no contexto
                    if k == -1:  # se o contexto é -1
                        # Codifica o caractere no contexto -1
                        encoded_bits = codificar_ppm(
                            self.structure, -1, "NO_CONTEXT", char, {}, False)
                        if encoded_bits:
                            # Calcula a probabilidade como tupla (numerador, denominador)
                            numerador = context.char_counts[char]
                            denominador = sum(
                                count for c, count in context.char_counts.items() if c not in self.ignore_chars)
                            entropia = round(
                                math.log2(numerador/denominador), 4)
                            self.encoded_bits.append(
                                (char, -1, "NO_CONTEXT", encoded_bits, (numerador, denominador), entropia))
                            if self.verbose:
                                # print(
                                #     f"Codificando '{char}' no contexto -1 com bits: {encoded_bits}")
                                pass

                        context.remove_character(char)
                    else:  # se o contexto não é -1
                        if not element_found:
                            # Codifica o caractere no contexto atual
                            encoded_bits = codificar_ppm(
                                self.structure, k, context_str, char, self.ignore_chars, False)
                            if encoded_bits:
                                # Calcula a probabilidade como tupla (numerador, denominador)
                                numerador = context.char_counts[char]
                                denominador = sum(
                                    count for c, count in context.char_counts.items() if c not in self.ignore_chars)
                                entropia = round(
                                    math.log2(numerador/denominador), 4)
                                self.encoded_bits.append(
                                    (char, k, context_str, encoded_bits, (numerador, denominador), entropia))
                                if self.verbose:
                                    # print(
                                    #     f"Codificando '{char}' no contexto {k}:{context_str} com bits: {encoded_bits}")
                                    pass

                        element_found = True
                        context.add_character(char)
                else:  # se o caractere não está no contexto
                    if k != -1:  # se o contexto não é -1
                        if len(context.char_counts):
                            if not element_found:
                                # Codifica o caractere de escape (ro)
                                escape_bits = codificar_ppm(
                                    self.structure, k, context_str, self.esc_symbol, self.ignore_chars, False)
                                if escape_bits:
                                    # Calcula a probabilidade para o símbolo de escape
                                    numerador = context.char_counts.get(
                                        self.esc_symbol, 0)
                                    denominador = sum(
                                        count for c, count in context.char_counts.items() if c not in self.ignore_chars)
                                    entropia = round(
                                        math.log2(numerador/denominador), 4)
                                    self.encoded_bits.append(
                                        (self.esc_symbol, k, context_str, escape_bits, (numerador, denominador), entropia))
                                    if self.verbose:
                                        # print(
                                        #     f"Codificando escape '{self.esc_symbol}' no contexto {k}:{context_str} com bits: {escape_bits}")
                                        pass
                            # Caracteres que devem ser ignorados na codificação
                            characters = {
                                c for c in context.get_characters() if c != self.esc_symbol}
                            if self.verbose:
                                # print(f"Contexto caracteres: {characters}")
                                pass

                            if characters:
                                self.ignore_chars.update(characters)

                        # Adiciona escape symbol e o caractere
                        context.add_character(self.esc_symbol)
                        context.add_character(char)

                        # verifica se o contexto está completo para poder remover ro
                        if self.is_context_complete(context):
                            context.remove_character(self.esc_symbol)

    def get_probabilities(self, context_str: str, k: int) -> Dict[str, float]:
        """Calcula as probabilidades para um dado contexto."""
        context = self.get_context(k, context_str)
        total_count = sum(context.char_counts.values())
        return {char: count / total_count for char, count in context.char_counts.items()}

    def get_encoded_bits(self) -> List:
        """Retorna os bits codificados até o momento."""
        return self.encoded_bits
