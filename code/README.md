# 🗺️ Multimodal Routing Porto: Metro & STCP
Este projeto implementa um motor de busca de rotas intermodais para a Área Metropolitana do Porto, integrando dados do Metro do Porto e STCP. O sistema utiliza algoritmos avançados (A* Multi-Objetivo, Dijkstra e ACO) para encontrar a Fronteira de Pareto entre Tempo de Viagem, Emissões de CO2 e Exercício Físico.

# 📋 Pré-requisitos
Python: Versão 3.12 ou superior.

Sistema Operativo: Linux, macOS ou Windows (via WSL2 recomendado para melhor suporte de bibliotecas geoespaciais).

Memória RAM: Mínimo 8GB (recomendado 16GB para processamento de grafos OSMnx).

# 🚀 Instalação
Siga os passos abaixo para configurar o ambiente de desenvolvimento:

1. Clonar o Repositório

```bash
git clone https://github.com/MIA-CDFR/CIN_GRUPO6.git
cd CIN_GRUPO6
```

2. Criar um Ambiente Virtual

É altamente recomendado o uso de um ambiente virtual para evitar conflitos de dependências.

```bash
# Criar ambiente
python -m venv venv

# Ativar ambiente (Windows)
.\venv\Scripts\activate

# Ativar ambiente (Linux/macOS)
source venv/bin/activate
```

3. Instalar Dependências

O projeto depende de bibliotecas geoespaciais complexas. O comando abaixo instala todas as versões compatíveis com Python 3.11+.

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Nota: Se tiver problemas na instalação do pyproj ou shapely no Windows, recomendamos o uso do instalador conda ou mamba.

# 📦 Conteúdo do requirements.txt
Certifica-te de que o teu ficheiro requirements.txt contém as seguintes bibliotecas base:

```plaintext
pandas (>=2.3.3,<3.0.0)
networkx (>=3.6.1,<4.0.0)
osmnx (>=2.0.7,<3.0.0)
scipy (>=1.16.3,<2.0.0)
shapely (>=2.1.2,<3.0.0)
gtfs-kit (>=12.0.0,<13.0.0)
geopy (>=2.4.1,<3.0.0)
ipykernel (>=7.1.0,<8.0.0)
folium (>=0.20.0,<0.21.0)
scikit-learn (>=1.8.0,<2.0.0)
```
