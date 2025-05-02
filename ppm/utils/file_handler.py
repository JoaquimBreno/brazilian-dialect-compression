class FileHandler:
    """Manipula operações de leitura e escrita de arquivos."""
    
    @staticmethod
    def read_file(filename: str) -> str:
        """Lê o conteúdo de um arquivo e retorna como string."""
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    
    @staticmethod
    def write_file(filename: str, content: str) -> None:
        """Escreve conteúdo em um arquivo."""
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)

def write_string_to_file(file_path, content):
    """
    Escreve uma string em um arquivo.
    
    Args:
        file_path: Caminho do arquivo.
        content: Conteúdo a ser escrito.
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    # print(f"Arquivo salvo em: {file_path}") 