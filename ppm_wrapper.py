import os
import sys
import tempfile

class PPMCompressor:
    """
    Wrapper para o compressor PPM que encapsula as importações problemáticas
    e fornece uma interface limpa para compressão de textos.
    """
    
    def __init__(self, k_max=2):
        """Inicializa o compressor PPM."""
        self.k_max = k_max
        
        # Adiciona o diretório raiz ao PATH para importações
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Importa diretamente os módulos necessários
        from ppm.app import PPMApp
        self.app_class = PPMApp
    
    def compress(self, text):
        """
        Comprime o texto usando o algoritmo PPM.
        
        Args:
            text: Texto a ser comprimido
            
        Returns:
            Tupla (texto_codificado, taxa_compressão)
        """
        try:
            # Filtrar caracteres não reconhecidos - manter apenas letras minúsculas, espaços e pontuação básica
            filtered_text = ''.join(c.lower() if c.isalpha() else '_' if c.isspace() else c 
                                  for c in text if c.isalpha() or c.isspace() or c in '.,;:!?')
            
            # Cria um arquivo temporário para o texto
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as temp_file:
                temp_file_name = temp_file.name
                temp_file.write(filtered_text)
            
            # Configura e executa o PPM
            app = self.app_class(k_max=self.k_max)
            encoded_sequence = app.run(temp_file_name)
            
            # Calcula o comprimento médio da codificação
            string_encoded = ''
            for i in encoded_sequence:
                string_encoded += i[3]
            
            compression_ratio = len(string_encoded) / len(filtered_text)
            
            # Limpa o arquivo temporário
            if os.path.exists(temp_file_name):
                os.remove(temp_file_name)
            
            # Retorna os dados codificados e a taxa de compressão
            return string_encoded, compression_ratio
        except Exception as e:
            print(f"Erro ao comprimir com PPM: {e}")
            # Retornar uma sequência vazia e uma taxa de compressão de 1 (sem compressão)
            return "", 1.0 