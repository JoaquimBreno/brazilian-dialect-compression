#!/usr/bin/env python3
import os
import re
import sys
import subprocess
import warnings
from pathlib import Path

# Suprimir avisos do PyPDF2
warnings.filterwarnings('ignore', category=UserWarning)

# Verifica e instala as dependências necessárias
required_packages = ['PyPDF2', 'pytesseract', 'Pillow']
try:
    import importlib.util
    missing_packages = [pkg for pkg in required_packages if importlib.util.find_spec(pkg.lower()) is None]
    
    if missing_packages:
        print(f"Instalando dependências necessárias: {', '.join(missing_packages)}")
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages, check=True)
        
    from PyPDF2 import PdfReader, PdfWriter
    import pytesseract
    from PIL import Image
except Exception as e:
    print(f"Erro ao verificar/instalar dependências: {str(e)}")
    print("Instalando manualmente...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "PyPDF2", "pytesseract", "Pillow"], check=True)
        from PyPDF2 import PdfReader, PdfWriter
        import pytesseract
        from PIL import Image
    except Exception as e:
        print(f"Não foi possível instalar as dependências: {str(e)}")
        print("Continuando com funcionalidade limitada...")

def get_file_type(file_path):
    """Executa o comando 'file' para identificar o tipo de arquivo"""
    result = subprocess.run(['file', file_path], capture_output=True, text=True)
    return result.stdout.strip()

def find_ebooks():
    """Encontra todos os arquivos de e-book no diretório atual"""
    # Lista todos os arquivos no diretório atual
    files = os.listdir('.')
    
    # Filtrar os arquivos que podem ser e-books (com e sem extensão)
    potential_ebooks = []
    for file in files:
        if os.path.isfile(file) and not file.endswith('.py') and not file.endswith('.txt') and not file.endswith('.sh'):
            file_info = get_file_type(file)
            if any(term in file_info.lower() for term in ['epub', 'mobi', 'book', 'pdf']):
                potential_ebooks.append((file, file_info))
    
    return potential_ebooks

def check_calibre_installed():
    """Verifica se o Calibre está instalado"""
    result = subprocess.run('which ebook-convert', shell=True, capture_output=True, text=True)
    return result.returncode == 0

def convert_to_pdf(ebook_path):
    """Converte um e-book para PDF usando o Calibre"""
    if not check_calibre_installed():
        print("O Calibre não está instalado. Não é possível converter.")
        print("Instale o Calibre com um dos seguintes comandos:")
        print("  - macOS: brew install --cask calibre")
        print("  - Ubuntu/Debian: sudo apt-get install calibre")
        print("  - Fedora/RHEL: sudo dnf install calibre")
        return None
    
    output_path = f"{Path(ebook_path).stem}.pdf"
    print(f"Convertendo {ebook_path} para PDF...")
    
    try:
        result = subprocess.run(['ebook-convert', ebook_path, output_path], 
                                capture_output=True, text=True, check=True)
        print(f"Conversão concluída: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Erro ao converter {ebook_path}: {e.stderr}")
        return None

def extract_text_from_page(page):
    """Extrai texto de uma página PDF"""
    try:
        return page.extract_text() or ""
    except Exception as e:
        print(f"Aviso: Não foi possível extrair texto da página. Erro: {str(e)}")
        return ""

def is_blank_page(text):
    """Detecta se uma página está em branco ou tem conteúdo insignificante"""
    # Remove espaços em branco e caracteres especiais
    cleaned_text = re.sub(r'[\s\n\r\t\f\v]+', '', text)
    # Considera em branco se tiver menos de 10 caracteres após limpeza
    return len(cleaned_text) < 10

def has_page_number_pattern(text):
    """Detecta se o texto tem padrões típicos de numeração de página"""
    # Padrões comuns de numeração de página
    patterns = [
        r'^\s*\d+\s*$',  # Número sozinho
        r'^\s*-\s*\d+\s*-\s*$',  # -123-
        r'^\s*\[\s*\d+\s*\]\s*$',  # [123]
        r'^\s*Página\s+\d+\s*$',  # Página 123
        r'^\s*Page\s+\d+\s*$',  # Page 123
        r'^\s*[ivxlcdmIVXLCDM]+\s*$'  # Numeração romana
    ]
    
    lines = text.strip().split('\n')
    for line in lines:
        if any(re.match(pattern, line) for pattern in patterns):
            return True
    return False

def is_cover_page(text, page_number):
    """Detecta se é uma página de capa"""
    # Converte para minúsculas e remove acentos para comparação
    text_lower = text.lower()
    
    # Indicadores fortes de capa
    strong_indicators = [
        'todos os direitos reservados',
        'all rights reserved',
        'copyright',
        '©',
        'primeira edição',
        'first edition',
        'published by',
        'publicado por',
        'editora',
        'publisher'
    ]
    
    # Se for uma das primeiras 2 páginas e tiver algum indicador forte
    if page_number <= 1 and any(ind in text_lower for ind in strong_indicators):
        return True
    
    # Características típicas de capa
    # - Pouco texto (mas não vazia)
    # - Sem números de página
    # - Sem pontuação típica de texto corrido
    if (10 < len(text.strip()) < 200 and  # Tem pouco texto
        not has_page_number_pattern(text) and  # Não tem número de página
        not re.search(r'[.!?][^\n]*[.!?]', text)):  # Não tem múltiplas frases
        return True
    
    return False

def is_toc_page(text):
    """Detecta se é uma página de sumário/índice"""
    text_lower = text.lower()
    
    # Títulos comuns de sumário (expandido)
    toc_titles = [
        'sumário',
        'índice',
        'conteúdo',
        'sumario',
        'indice',
        'conteudo',
        'table of contents',
        'contents',
        'index',
        'índice geral',
        'índice analítico',
        'índice remissivo',
        'lista de capítulos',
        'lista de conteúdos',
        'índice detalhado',
        'sumário detalhado',
        'conteúdo programático',
        'programa do curso',
        'outline',
        'table des matières',  # francês
        'contenido',  # espanhol
        'índice de conteúdos'
    ]
    
    # Verifica se começa com um título de sumário
    first_lines = text_lower.split('\n')[:3]  # Checa as 3 primeiras linhas
    if any(any(title in line for title in toc_titles) for line in first_lines):
        return True
    
    # Padrões de formatação de sumário (expandido)
    toc_patterns = [
        # Capítulo/Seção + número + página
        r'^\s*(?:capítulo|capitulo|seção|secao|parte|chapter|section|part|unidade|módulo|modulo|lição|licao)\s*[\dIVXivx]+[\s\.\-]+.+?\d+\s*$',
        
        # Número + título + página
        r'^\s*[\dIVXivx]+[\s\.\-]+[^\n]+?\d+\s*$',
        
        # Título + sequência de pontos/traços + página
        r'^.+?[\.\-]{3,}\d+\s*$',
        
        # Padrões com parênteses
        r'^\s*[\dIVXivx]+[\s\.\-]+[^\n]+?\(\d+\)\s*$',
        
        # Padrões com colchetes
        r'^\s*[\dIVXivx]+[\s\.\-]+[^\n]+?\[\d+\]\s*$',
        
        # Padrões com p. ou pág.
        r'^.+?(?:p\.|pág\.|página|pagina)\s*\d+\s*$',
        
        # Letras + título + página
        r'^\s*[A-Za-z][\s\.\-]+[^\n]+?\d+\s*$',
        
        # Bullets/marcadores + título + página
        r'^\s*[•\-\*]\s+[^\n]+?\d+\s*$'
    ]
    
    # Conta quantas linhas seguem os padrões de sumário
    toc_line_count = 0
    numbered_lines = 0  # Contador para linhas com números
    lines = text_lower.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:  # Ignora linhas vazias
            continue
            
        # Verifica padrões de sumário
        if any(re.match(pattern, line) for pattern in toc_patterns):
            toc_line_count += 1
        
        # Conta linhas que terminam com número
        if re.search(r'\d+\s*$', line):
            numbered_lines += 1
    
    # Critérios para considerar como sumário:
    # 1. Pelo menos 3 linhas com padrão de sumário OU
    # 2. Mais de 50% das linhas não vazias terminam com número E pelo menos 5 linhas com número
    total_non_empty_lines = sum(1 for line in lines if line.strip())
    
    if (toc_line_count >= 3 or 
        (numbered_lines >= 5 and numbered_lines / total_non_empty_lines > 0.5)):
        return True
    
    return False

def is_intro_page(text):
    """Detecta se é uma página de introdução/prefácio"""
    text_lower = text.lower()
    
    # Títulos comuns de introdução
    intro_titles = [
        'introdução',
        'prefácio',
        'prólogo',
        'apresentação',
        'introduction',
        'preface',
        'foreword',
        'prologue',
        'preâmbulo',
        'nota do autor',
        'nota do editor',
        'about the author',
        'sobre o autor'
    ]
    
    # Verifica se começa com um título de introdução
    first_paragraph = text_lower.split('\n')[0].strip()
    if any(title in first_paragraph for title in intro_titles):
        # Verifica se tem conteúdo suficiente após o título
        content_after_title = text_lower.split('\n', 1)[1] if '\n' in text_lower else ''
        return len(content_after_title.strip()) > 100
    
    return False

def should_remove_page(text, page_number, total_pages):
    """Determina se uma página deve ser removida baseado em várias características"""
    # Sempre remove páginas em branco
    if is_blank_page(text):
        return True, "página em branco"
    
    # Verifica capa apenas nas primeiras páginas
    if page_number <= 2 and is_cover_page(text, page_number):
        return True, "capa"
    
    # Verifica sumário nas primeiras páginas
    if page_number <= 15 and is_toc_page(text):
        return True, "sumário"
    
    # Verifica introdução nas primeiras páginas
    if page_number <= 15 and is_intro_page(text):
        return True, "introdução"
    
    # Verifica páginas finais (copyright, etc)
    if page_number >= total_pages - 3:
        if is_cover_page(text, page_number):  # Contracapa
            return True, "contracapa"
    
    return False, None

def has_links(text):
    """Detecta se uma página contém links ou URLs"""
    # Padrões comuns de URLs e links
    url_patterns = [
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',  # URLs completas
        r'www\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z]{2,})+',  # URLs começando com www
        r'(?:mailto:|email:)\s*[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Links de email
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Endereços de email
        r'(?:facebook|twitter|instagram|linkedin)\.com/\S+',  # Links de redes sociais
    ]
    
    # Verifica cada padrão
    for pattern in url_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    # Palavras-chave que indicam presença de links
    link_keywords = [
        'clique aqui',
        'click here',
        'visit',
        'acesse',
        'access',
        'link:',
        'url:',
        'website:',
        'site:',
        'blog:',
        'veja mais em',
        'saiba mais em',
        'learn more at',
        'find us at'
    ]
    
    # Verifica palavras-chave
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in link_keywords)

def has_copyright(text):
    """Detecta se uma página contém informações de copyright"""
    # Termos relacionados a copyright
    copyright_terms = [
        'copyright',
        '©',
        'todos os direitos reservados',
        'all rights reserved',
        'direitos autorais',
        'propriedade intelectual',
        'intellectual property',
        'rights reserved',
        'direitos reservados',
        'published by',
        'publicado por',
        'editora',
        'publisher',
        'printing rights',
        'direitos de impressão',
        'legal rights',
        'direitos legais',
        'reproduction rights',
        'direitos de reprodução'
    ]
    
    text_lower = text.lower()
    return any(term.lower() in text_lower for term in copyright_terms)

def clean_pdf(pdf_path, output_path=None):
    """Remove capas, sumários, introduções e páginas em branco de um PDF"""
    try:
        if 'PdfReader' not in globals():
            print("PyPDF2 não está disponível. Não é possível limpar o PDF.")
            return None, []
            
        # Sempre usar o arquivo original como saída
        output_path = pdf_path
        
        # Tenta abrir o PDF com tratamento de erro
        try:
            reader = PdfReader(pdf_path)
        except Exception as e:
            print(f"Erro ao abrir o PDF {pdf_path}: {str(e)}")
            print("O arquivo pode estar corrompido ou protegido.")
            return None, []
        
        writer = PdfWriter()
        total_pages = len(reader.pages)
        removed_pages = []
        removal_reasons = []
        processed_pages = 0
        
        print(f"\nLimpando: {pdf_path}")
        print(f"Total de páginas: {total_pages}")
        print("Analisando padrões de texto para identificar páginas estruturais...")
        
        # Barra de progresso simples
        progress_length = 40
        
        for i in range(total_pages):
            # Atualiza a barra de progresso
            processed_pages += 1
            progress = int((processed_pages / total_pages) * progress_length)
            sys.stdout.write('\r')
            sys.stdout.write(f"[{'=' * progress}{' ' * (progress_length - progress)}] {processed_pages}/{total_pages}")
            sys.stdout.flush()
            
            try:
                page = reader.pages[i]
                text = extract_text_from_page(page)
                
                # Verifica se é uma página com pouco texto (menos de 300 caracteres)
                if len(text.strip()) < 300:
                    removed_pages.append(i + 1)
                    removal_reasons.append("pouco texto")
                    continue
                
                # Verifica se é sumário em qualquer parte do documento
                if is_toc_page(text):
                    removed_pages.append(i + 1)
                    removal_reasons.append("sumário")
                    continue
                
                # Verifica se a página contém links
                if has_links(text):
                    removed_pages.append(i + 1)
                    removal_reasons.append("contém links")
                    continue
                
                # Verifica se a página contém informações de copyright
                if has_copyright(text):
                    removed_pages.append(i + 1)
                    removal_reasons.append("copyright")
                    continue
                
                should_remove, reason = should_remove_page(text, i, total_pages)
                
                if should_remove:
                    removed_pages.append(i + 1)
                    removal_reasons.append(reason)
                    continue
                
                # Se não for para remover, adiciona a página ao novo PDF
                writer.add_page(page)
                
            except Exception as e:
                print(f"\nAviso: Erro ao processar página {i+1}: {str(e)}")
                # Adiciona a página mesmo com erro para não perder conteúdo
                try:
                    writer.add_page(reader.pages[i])
                except:
                    print(f"Não foi possível adicionar a página {i+1} ao novo PDF")
        
        print("\n")  # Nova linha após a barra de progresso
        
        # Escrever o PDF limpo sobrescrevendo o original
        try:
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
        except Exception as e:
            print(f"Erro ao salvar o PDF: {str(e)}")
            return None, []
        
        if removed_pages:
            print(f"\nPDF limpo! {len(removed_pages)} páginas removidas:")
            for page, reason in zip(removed_pages, removal_reasons):
                print(f"- Página {page}: {reason}")
            print(f"\nArquivo original atualizado: {output_path}")
        else:
            print("\nNenhuma página estrutural detectada para remoção.")
            print(f"Arquivo original mantido: {output_path}")
        
        return output_path, removed_pages
        
    except Exception as e:
        print(f"\nErro ao limpar {pdf_path}: {str(e)}")
        return None, []

def main():
    print("=" * 60)
    print("GERENCIADOR DE E-BOOKS - CONVERSÃO E LIMPEZA")
    print("=" * 60)
    
    # 1. Encontrar e-books
    ebooks = find_ebooks()
    
    if not ebooks:
        print("Nenhum e-book encontrado no diretório atual.")
        return
    
    print(f"Encontrados {len(ebooks)} e-books.")
    
    # 2. Agrupar e-books por tipo
    types = {}
    for file, file_info in ebooks:
        type_match = re.search(r':\s*(.*?)($|,)', file_info)
        if type_match:
            file_type = type_match.group(1).strip()
            if file_type not in types:
                types[file_type] = []
            types[file_type].append(file)
    
    # Mostrar os tipos encontrados
    print("\n--- TIPOS DE ARQUIVOS ENCONTRADOS ---")
    for file_type, files in types.items():
        print(f"\n{file_type} ({len(files)} arquivos):")
        for file in files[:5]:  # Mostrar apenas os primeiros 5 de cada tipo
            print(f"  - {file}")
        if len(files) > 5:
            print(f"  - ... e mais {len(files) - 5} arquivo(s)")
    
    # 3. Verificar se o Calibre está instalado
    calibre_installed = check_calibre_installed()
    
    # 4. Menu de opções
    while True:
        print("\n--- OPÇÕES ---")
        print("1. Converter todos os e-books para PDF" + (" (Calibre necessário)" if not calibre_installed else ""))
        print("2. Limpar todos os PDFs (remover capas, sumários, etc.)")
        print("3. Converter e limpar tudo" + (" (Calibre necessário)" if not calibre_installed else ""))
        print("4. Sair")
        
        choice = input("\nEscolha uma opção (1-4): ").strip()
        
        if choice == '1':
            if not calibre_installed:
                print("\nO Calibre não está instalado. Para instalar o Calibre:")
                print("  - No macOS: brew install --cask calibre")
                print("  - No Ubuntu/Debian: sudo apt-get install calibre")
                print("  - No Fedora/RHEL: sudo dnf install calibre")
                print("\nPor favor, instale o Calibre e execute este script novamente.")
                continue
            
            for file, _ in ebooks:
                converted_pdf = convert_to_pdf(file)
                print("-" * 40)
                
        elif choice == '2':
            pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
            
            if not pdf_files:
                print("Nenhum arquivo PDF encontrado no diretório atual.")
                continue
            
            print(f"Encontrados {len(pdf_files)} arquivos PDF.")
            
            for pdf_file in pdf_files:
                output_path, removed_pages = clean_pdf(pdf_file)
                print("-" * 40)
                
        elif choice == '3':
            if not calibre_installed:
                print("\nO Calibre não está instalado. Não é possível converter e-books.")
                print("Para instalar o Calibre:")
                print("  - No macOS: brew install --cask calibre")
                print("  - No Ubuntu/Debian: sudo apt-get install calibre")
                print("  - No Fedora/RHEL: sudo dnf install calibre")
                print("\nPor favor, instale o Calibre e execute este script novamente.")
                continue
            
            # Converter todos os e-books primeiro
            converted_pdfs = []
            for file, _ in ebooks:
                converted_pdf = convert_to_pdf(file)
                if converted_pdf:
                    converted_pdfs.append(converted_pdf)
                print("-" * 40)
            
            # Depois limpar todos os PDFs (incluindo os recém-convertidos)
            pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
            
            if not pdf_files:
                print("Nenhum arquivo PDF encontrado para limpar.")
                continue
            
            print(f"Limpando {len(pdf_files)} arquivos PDF...")
            
            for pdf_file in pdf_files:
                output_path, removed_pages = clean_pdf(pdf_file)
                print("-" * 40)
                
        elif choice == '4':
            print("\nSaindo do programa. Até mais!")
            break
            
        else:
            print("\nOpção inválida. Por favor, escolha uma opção entre 1 e 4.")

if __name__ == "__main__":
    main() 