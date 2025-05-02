import heapq
import math
from collections import defaultdict

# class Node:
#     def __init__(self, char, freq, order):
#         self.char = char
#         self.freq = freq
#         self.order = order  # Indica a ordem alfabética
#         self.left = None
#         self.right = None
    
#     def __lt__(self, other):
#         # Primeiro, ordenamos pela frequência (menor primeiro)
#         if self.freq != other.freq:
#             return self.freq < other.freq
#         # Se as frequências forem iguais, usamos a ordem alfabética
#         return self.order > other.order


class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None


def equiprovable_huffman(frequency_dict):
    # Ordenar as chaves alfabéticas, mas sem considerar o cedilha primeiro
    sorted_items = sorted(frequency_dict.items(), key=lambda x: (x[0], x[1]))

    # Número de caracteres distintos
    num_chars = len(sorted_items)

    # Calcular o número de bits necessários para representar todos os caracteres
    code_length = math.ceil(math.log2(num_chars))

    # Gerar os códigos binários de comprimento fixo
    codes = {char: format(i, f'0{code_length}b') for i, (char, _) in enumerate(sorted_items)}

    return codes

# def build_huffman_tree(frequency_dict, verbose=True):
#     # Ordenando o dicionário primeiro por cedilha, depois alfabeticamente e, por fim, pela frequência
#     sorted_items = sorted(frequency_dict.items(), key=lambda x: x[1])
#     print(f"Lista de nós antes da construção da árvore depois do sort por frequencia: {sorted_items}")
#     sorted_items = sorted(sorted_items, key=lambda x: x[0], reverse=True)
#     print(f"Lista de nós antes da construção da árvore depois do sort por alfabeto: {sorted_items}")
#     heap = [Node(char, freq, char) for char, freq in sorted_items]
#     heapq.heapify(heap)
    
#     if verbose:
#         print(f"Lista de nós antes da construção da árvore: {[f'({node.char}, {node.freq})' for node in heap]}")    

#     while len(heap) > 1:
#         right = heapq.heappop(heap)
#         left = heapq.heappop(heap)
#         merged = Node(None, left.freq + right.freq, min(left.order, right.order))
#         merged.left = left
#         merged.right = right
#         heapq.heappush(heap, merged)
        
#         if verbose:
#             print(f"Unindo '{left.char}' e '{right.char}' com frequências {left.freq} e {right.freq} para formar '{merged.char}' com frequência {merged.freq}")
#             #print(f"heap apos alteracao: {[f'({node.char}, {node.freq})' for node in heap]}") 
#     return heap[0]


def stable_sort(lst):
    """ Ordenação estável por frequência crescente e ordem alfabética ('ç' antes de 'a'). """
    return sorted(lst, key=lambda x: (x[1], x[0] is None, -ord(x[0]) if x[0] is not None else float('inf')))

def build_huffman_tree(frequency_dict, verbose):
    # Criar uma lista de nós e ordenar por frequência (crescendo), mantendo ordem alfabética
    nodes = [(char, freq, Node(char, freq)) for char, freq in frequency_dict.items()]
    nodes = stable_sort(nodes)  # Ordenação inicial
    
    #(f"Lista de nós antes da construção da árvore: {[f'({node[0]}, {node[1]})' for node in nodes]}")

    while len(nodes) > 1:
        # Pegamos os dois primeiros elementos (menores frequências)
        (char1, freq1, right) = nodes.pop(0)
        (char2, freq2, left) = nodes.pop(0)

        # Criamos um novo nó que agrupa os dois
        merged = Node(None, freq1 + freq2)
        merged.left = left
        merged.right = right

        # Inserimos na posição correta para manter estabilidade
        nodes.append((None, freq1 + freq2, merged))
        nodes = stable_sort(nodes)  # Manter ordenação estável

        #print(f"Unindo '{char1}' e '{char2}' com frequências {freq1} e {freq2} para formar um nó com frequência {freq1 + freq2}")
        #print(f"Lista de nós após união: {[f'({node[0]}, {node[1]})' for node in nodes]}")
    
    return nodes[0][2]  # Retorna a raiz da árvore


def generate_huffman_codes(node, prefix="", codebook={}):
    if node is not None:
        if node.char is not None:
            codebook[node.char] = prefix
        generate_huffman_codes(node.left, prefix + "0", codebook)
        generate_huffman_codes(node.right, prefix + "1", codebook)
    return codebook

def huffman_encoding(frequency_dict, verbose=False):
    if not frequency_dict:
        return {}

    tree_root = build_huffman_tree(frequency_dict, verbose)
    codes = generate_huffman_codes(tree_root, "", {})
    return codes

def codificar_ppm(ppm_structure, k, context, char, ignore_chars, verbose=False):
    # Implementação da decodificação PPM (não fornecida no código original)
    freq_dict = {}
        
    if k == -1:

        contexts_dict = ppm_structure[k]["NO_CONTEXT"].char_counts
        if len(contexts_dict) == 1:
            return None
        codes = equiprovable_huffman(contexts_dict)
    elif k == 0:
        contexts_dict = ppm_structure[k]["NO_CONTEXT"].char_counts
            
        freq_dict = {c: count for c, count in contexts_dict.items() if c not in ignore_chars}
            
        if len(freq_dict) == 1:
            # Se o dicionário estiver vazio, retorna None
            return None

        codes = huffman_encoding(freq_dict, verbose)
    else:
        contexts_dict = ppm_structure[k][context].char_counts
            
        freq_dict = {c: count for c, count in contexts_dict.items() if c not in ignore_chars}
        if len(freq_dict) == 1:
            # Se o dicionário estiver vazio, retorna None
            return None
        codes = huffman_encoding(freq_dict, verbose)

    return codes.get(char, None)

def decodificar_ppm(ppm_structure, k, context, code, ignore_chars, verbose=False):
    freq_dict = {}
    
    if k == -1:
        contexts_dict = ppm_structure[k]["NO_CONTEXT"].char_counts
        codes = equiprovable_huffman(contexts_dict)
    elif k == 0:
        contexts_dict = ppm_structure[k]["NO_CONTEXT"].char_counts

        freq_dict = {c: count for c, count in contexts_dict.items() if c not in ignore_chars}
        
        codes = huffman_encoding(freq_dict, verbose)
    else:
        contexts_dict = ppm_structure[k][context].char_counts
            
        freq_dict = {c: count for c, count in contexts_dict.items() if c not in ignore_chars}
        codes = huffman_encoding(freq_dict, verbose)

    for chars, c in codes.items():
        if code == c:
            return codes, chars

    return codes, None
