from typing import List, Any
import json
from utils.file_handler import FileHandler
from processors.ppm_processor import PPMProcessor

class PPMApp:
    """Aplicação principal que usa o modelo PPM."""
    
    def __init__(self, k_max: int = 2):
        self.k_max = k_max
        self.file_handler = FileHandler()
        self.processor = PPMProcessor(k_max)
        self.text=""
    
    def run(self, filename: str) -> List[Any]:
        """Executa o processamento completo em um arquivo."""
        self.text = self.file_handler.read_file(filename)
        text = self.text
        return self.processor.process_text(text) 

    def get_model_structure_json(self, indent: int = 4) -> str:
        """
        Converte a estrutura do modelo PPM em uma string JSON formatada.
        
        Args:
            indent: Número de espaços para indentação do JSON (padrão: 4)
            
        Returns:
            String contendo a representação JSON da estrutura do modelo
        """
        # Obter a estrutura do modelo
        structure = self.processor.model.structure
        
        # Converter a estrutura para um formato serializável para JSON
        json_structure = {}
        for k, contexts in structure.items():
            json_structure[str(k)] = {}
            for context_key, context_obj in contexts.items():
                # Converter o objeto Context em um dicionário simples
                json_structure[str(k)][context_key] = dict(context_obj.char_counts)
        
        # Converter para string JSON formatada
        return json.dumps(json_structure, indent=indent, ensure_ascii=False)
    
    def save_model_structure_to_file(self, filename: str) -> None:
        """
        Salva a estrutura do modelo em um arquivo JSON.
        
        Args:
            filename: Nome do arquivo para salvar o JSON
        """
        json_data = self.get_model_structure_json()
        self.file_handler.write_file(filename, json_data)