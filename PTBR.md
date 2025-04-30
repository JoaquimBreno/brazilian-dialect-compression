# Estudo e Classificação de Dialetos Regionais Brasileiros

<p align="center">
  <img src="https://via.placeholder.com/800x400?text=Dialetos+Regionais+Brasileiros" alt="Dialetos Regionais Brasileiros" width="600"/>
</p>

[![Licença: MIT](https://img.shields.io/badge/Licença-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![PLN](https://img.shields.io/badge/PLN-Compressão-green.svg)](https://pt.wikipedia.org/wiki/Processamento_de_linguagem_natural)

> **Uma abordagem inovadora para análise de dialetos brasileiros utilizando algoritmos de compressão de texto para identificar, classificar e visualizar padrões linguísticos regionais.**

*[Read this in English](./README.md)*

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Dataset](#-dataset)
- [Autores por Região](#-autores-por-região)
- [Metodologia](#-metodologia)
- [Análises](#-análises)
- [Objetivos](#-objetivos)
- [Requisitos](#-requisitos)
- [Uso](#-uso)
- [Resultados](#-resultados)

## 🔍 Visão Geral

Este projeto analisa e classifica dialetos de quatro regiões do Brasil utilizando técnicas de compressão de texto como método de análise linguística. Ao aproveitar a teoria da informação e algoritmos de compressão, podemos identificar padrões estatísticos específicos de cada dialeto regional sem necessidade de engenharia de características linguísticas explícitas.

## 📚 Dataset

- **Composição**: Textos literários com forte presença de regionalismos
- **Divisão**: Conjuntos de treino, teste e validação, 100k caracteres por batch
- **Pré-processamento**: Dados limpos e organizados por região
- **Escopo**: Obras de autores contemporâneos e não contemporâneos que evidenciam ou simulam dialetos regionais

## 👥 Autores por Região

### Nordeste
- Maria Valéria Rezende
- Ariano Suassuna
- Patativa do Assaré
- Bráulio Bessa
- Jarid Arraes
- Itamar Vieira Junior
- Raquel de Queiroz

### Sul
- Luis Fernando Verissimo
- Josue Guimaraes
- Leticia Wierzchowski
- Simoes Lopes Neto
- Paulo Leminski
- Dalton Trevisan
- Cruz e Souza

### Sudeste
- Paulo Lins
- Machado de Assis
- Guimaraes Rosa
- Monteiro Lobato
- Cornéllio Pena
- Oswaldo de Andrade
- Fernanda Torres

### Norte
- Milton Hatoum
- Edyr Augusto
- Dalcídio Jurandir
- Marcio Souza
- Thiago Mello
- Marcia Kambeba

## 🔬 Metodologia

Aplicamos diferentes algoritmos de compressão para analisar as características linguísticas dos textos:

- **PPM (Prediction by Partial Matching)**: Algoritmo principal do estudo
- **Lempel-Ziv (LZ77, LZMA)**: Compressores baseados em dicionário
- **BWT (Burrows-Wheeler Transform)**: Transformação de texto para análise de padrões

<p align="center">
  <img src="https://via.placeholder.com/600x300?text=Metodologia+de+Compressão" alt="Metodologia de Compressão" width="500"/>
</p>

## 📊 Análises

- Cálculo de taxa de compressão por região
- Medição de entropia de textos regionais
- Construção de matrizes de distância entre dialetos
- Geração de dendrogramas para visualização de similaridades
- Comparação de padrões linguísticos entre regiões

## 🎯 Objetivos

- Quantificar diferenças linguísticas entre dialetos regionais
- Identificar características distintivas de cada região
- Estabelecer relações de similaridade entre diferentes dialetos
- Contribuir para estudos linguísticos sobre variações dialetais no Brasil
- Criar um modelo computacional para classificação de dialetos

## 💻 Requisitos

- Python 3.6+
- NumPy
- Bibliotecas de compressão (lzma, zlib)
- Ferramentas de visualização para dendrogramas

## 🚀 Uso

1. Execute o processador PPM nos dados de treinamento:
```
---------
```

2. Compare com outros algoritmos de compressão:
```
------------
```

3. Gere matriz de distância e dendrograma:
```
-----------------
```

## 📈 Resultados

Os resultados incluem:
- Taxas de compressão por região
- Matrizes de distância entre dialetos
- Visualizações de dendrogramas
- Análises estatísticas de características linguísticas

<p align="center">
  <img src="https://via.placeholder.com/600x400?text=Dendrograma+de+Dialetos+Regionais" alt="Dendrograma de Dialetos Regionais" width="500"/>
</p>

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

## 🤝 Agradecimentos

Agradecimentos especiais a todos os autores cujas obras contribuem para este estudo linguístico e à comunidade de pesquisa em linguística computacional. 