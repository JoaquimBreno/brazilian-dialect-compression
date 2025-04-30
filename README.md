# Brazilian Regional Dialect Classification Study


[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![NLP](https://img.shields.io/badge/NLP-Compression-green.svg)](https://en.wikipedia.org/wiki/Natural_language_processing)

> **A novel approach to Brazilian dialect analysis using text compression algorithms to identify, classify, and visualize regional linguistic patterns.**

*[Read this in Portuguese](./PTBR.md)*

## 📋 Table of Contents

- [Overview](#-overview)
- [Dataset](#-dataset)
- [Featured Authors](#-featured-authors)
- [Methodology](#-methodology)
- [Analysis](#-analysis)
- [Objectives](#-objectives)
- [Requirements](#-requirements)
- [Usage](#-usage)
- [Results](#-results)

## 🔍 Overview

This project analyzes and classifies dialects from four Brazilian regions using text compression techniques as a method of linguistic analysis. By leveraging information theory and compression algorithms, we can identify statistical patterns specific to each regional dialect without requiring explicit linguistic feature engineering.

## 📚 Dataset

- **Composition**: Literary texts with strong regional linguistic characteristics
- **Division**: Training, testing, and validation sets, 100k characters per batch
- **Pre-processing**: Clean data organized by region
- **Scope**: Works from contemporary and non-contemporary authors that highlight or simulate regional dialects

## 👥 Featured Authors

### Northeast (Nordeste)

- Maria Valéria Rezende
- Ariano Suassuna
- Patativa do Assaré
- Bráulio Bessa
- Jarid Arraes
- Itamar Vieira Junior
- Raquel de Queiroz

### South (Sul)

- Luis Fernando Verissimo
- Josue Guimaraes
- Leticia Wierzchowski
- Simoes Lopes Neto
- Paulo Leminski
- Dalton Trevisan
- Cruz e Souza

### Southeast (Sudeste)

- Paulo Lins
- Machado de Assis
- Guimaraes Rosa
- Monteiro Lobato
- Cornéllio Pena
- Oswaldo de Andrade
- Fernanda Torres

### North (Norte)

- Milton Hatoum
- Edyr Augusto
- Dalcídio Jurandir
- Marcio Souza
- Thiago Mello
- Marcia Kambeba

## 🔬 Methodology

We apply different compression algorithms to analyze the linguistic characteristics of the texts:

- **PPM (Prediction by Partial Matching)**: Primary algorithm of the study
- **Lempel-Ziv (LZ77, LZMA)**: Dictionary-based compressors
- **BWT (Burrows-Wheeler Transform)**: Text transformation for pattern analysis

<p align="center">
  <img src="https://via.placeholder.com/600x300?text=Compression+Methodology" alt="Compression Methodology" width="500"/>
</p>

## 📊 Analysis

- Calculation of compression rates by region
- Measurement of entropy in regional texts
- Construction of distance matrices between dialects
- Generation of dendrograms for similarity visualization
- Cross-regional linguistic pattern comparison

## 🎯 Objectives

- Quantify linguistic differences between regional dialects
- Identify distinctive characteristics of each region
- Establish similarity relationships between different dialects
- Contribute to linguistic studies on dialectal variations in Brazil
- Create a computational model for dialect classification

## 💻 Requirements

- Python 3.6+
- NumPy
- Compression libraries (lzma, zlib)
- Visualization tools for dendrograms

## 🚀 Usage

1. Execute the PPM processor on the training data:

```
---------
```

2. Compare with other compression algorithms:

```
------------
```

3. Generate distance matrix and dendrogram:

```
-----------------
```

## 📈 Results

The results include:

- Compression rates by region
- Distance matrices between dialects
- Dendrogram visualizations
- Statistical analyses of linguistic characteristics

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Acknowledgments

Special thanks to all the authors whose works contribute to this linguistic study and to the research community in computational linguistics.
