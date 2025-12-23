# 🗺️ Multimodal Routing Porto: Metro & STCP

Sistema de otimização multimodal de rotas para a Área Metropolitana do Porto, integrando dados reais do Metro do Porto e STCP com algoritmos avançados (A* Multi-Objetivo, Dijkstra e ACO) para encontrar a Fronteira de Pareto entre Tempo de Viagem, Emissões de CO2 e Exercício Físico.

---

## 📋 Pré-requisitos

- **Python**: Versão 3.10 ou superior
- **Sistema Operativo**: Linux, macOS ou Windows
- **Memória RAM**: Mínimo 4 GB (recomendado 8 GB)
- **Espaço em Disco**: 500 MB

---

## 🚀 Instalação

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/CIN_GRUPO6.git
cd CIN_GRUPO6/code
```

### 2. Criar Ambiente Virtual

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Alternativa com Poetry (recomendado):**

```bash
pip install poetry
poetry install
poetry shell
```

### 4. Verificar Instalação

```bash
python -m app.test_cases
```

Deverá ver um resumo dos 22 casos de teste disponíveis.

---

## 📦 Estrutura do Projeto

```
code/
├── TECHNICAL_DOCUMENTATION.md   # Este ficheiro
├── USER_GUIDE.md                # Guia completo de uso
├── requirements.txt             # Dependências Python
├── pyproject.toml               # Configuração Poetry
│
├── app/                         # Código principal
│   ├── main.py                  # Entrada API REST (FastAPI)
│   ├── test_cases.py            # 22 casos de teste para validação
│   ├── models/                  # Modelos de dados
│   │   └── __init__.py
│   ├── services/                # Lógica de negócio
│   │   ├── graph.py             # Construção da rede multimodal
│   │   ├── solution.py          # Classe Solution (5 atributos)
│   │   └── algoritms/           # Implementações dos algoritmos
│   │       ├── a_star.py        # A* Multi-Objetivo (heurístico)
│   │       ├── dijkstra.py      # Dijkstra Multi-Label (exaustivo)
│   │       └── aco.py           # ACO (estocástico)
│   └── utils/                   # Utilitários
│       ├── co2.py               # Cálculo de emissões CO2
│       ├── feed.py              # Processamento GTFS
│       ├── geo.py               # Operações geográficas
│       ├── route.py             # Cálculo de rotas
│       └── time.py              # Manipulação temporal
│
├── feeds/                       # Dados GTFS reais
│   ├── gtfs_metro/              # Metro do Porto
│   │   ├── agency.txt
│   │   ├── calendar.txt
│   │   ├── calendar_dates.txt
│   │   ├── fare_attributes.txt
│   │   ├── fare_rules.txt
│   │   ├── routes.txt
│   │   ├── shapes.txt
│   │   ├── stop_times.txt
│   │   ├── stops.txt
│   │   ├── transfers.txt
│   │   └── trips.txt
│   └── gtfs_stcp/               # STCP - Autocarros
│       ├── agency.txt
│       ├── calendar.txt
│       ├── calendar_dates.txt
│       ├── routes.txt
│       ├── shapes.txt
│       ├── stop_times.txt
│       ├── stops.txt
│       ├── transfers.txt
│       └── trips.txt
│
└── notebook/                    # Jupyter Notebook para análise
    └── route-optimization-optimized.ipynb
```

---

## 🖥️ Como Executar

### Opção 1: Casos de Teste (Validação)

```bash
python -m app.test_cases
```

Executa 22 casos de teste organizados em 6 níveis de complexidade.

### Opção 2: Script Python Simples

```python
from app.services.graph import MultimodalGraph
from app.services.algoritms.a_star import AStarRouter
from app.utils.geo import get_coordinates

# 1. Construir rede
graph = MultimodalGraph()
graph.build_from_gtfs()

# 2. Definir origem/destino
origin = get_coordinates("Livraria Bertrand, Porto")
destination = get_coordinates("Torre dos Clérigos, Porto")

# 3. Executar algoritmo
router = AStarRouter(graph)
solutions = router.find_routes(origin, destination, "09:00:00")

# 4. Processar resultados
for i, sol in enumerate(solutions, 1):
    print(f"Rota {i}: {sol.total_time//60}min, {sol.total_co2:.0f}g CO2")
```

### Opção 3: API REST

```bash
# Terminal 1: Iniciar servidor
python -m uvicorn app.main:app --reload

# Terminal 2: Fazer pedido
curl -X POST http://localhost:8000/api/routes \
  -H "Content-Type: application/json" \
  -d '{
    "origin": {"lat": 41.1579, "lon": -8.6291},
    "destination": {"lat": 41.1625, "lon": -8.6362},
    "start_time": "09:00:00",
    "algorithm": "astar"
  }'
```

### Opção 4: Jupyter Notebook

```bash
jupyter notebook notebook/route-optimization-optimized.ipynb
```

---

## 🧠 Algoritmos Implementados

### 1. A* Multi-Objetivo

- **Tipo**: Heurístico
- **Tempo**: 0.1-0.5s típicamente
- **Completude**: ⭐⭐⭐
- **Ideal para**: Produção, tempo real
- **Parâmetros**:
  ```python
  MAX_LABELS_PER_NODE = 10
  TIME_WINDOW_EPSILON = 120  # segundos
  RELAXATION_FACTOR = 1.5
  ```

### 2. Dijkstra Multi-Label

- **Tipo**: Exaustivo (garantia teórica)
- **Tempo**: 5-30s (mais lento)
- **Completude**: ⭐⭐⭐⭐⭐
- **Ideal para**: Validação, pesquisa
- **Parâmetros**:
  ```python
  MAX_LABELS_PER_NODE = 8
  TIME_WINDOW_EPSILON = 60  # segundos
  ```

### 3. ACO (Ant Colony Optimization)

- **Tipo**: Estocástico (bio-inspirado)
- **Tempo**: 2-10s
- **Completude**: ⭐⭐⭐
- **Ideal para**: Exploração, diversidade
- **Parâmetros**:
  ```python
  ALPHA = 1.0           # peso de feromona
  BETA = 3.0            # peso de heurística
  RHO = 0.1             # taxa de evaporação
  Q = 100               # quantidade de feromona
  num_ants = 30
  num_iterations = 20
  ```

### Comparação Rápida

| Aspecto | A* | Dijkstra | ACO |
|---------|-----|----------|-----|
| Velocidade | ⚡⚡⚡ | ⚡ | ⚡⚡ |
| Completude | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Tempo Real | ✅ | ❌ | ⚠️ |
| Paralelizável | ✅ | ❌ | ✅ |

---

## 📊 Metodologia de Avaliação

### Problema Multi-Objetivo

O sistema minimiza **simultaneamente** três critérios:

1. **Tempo de Viagem** (segundos)
2. **Emissões CO2** (gramas)
3. **Distância de Caminhada** (quilómetros)

### Fronteira de Pareto

Em vez de retornar "a melhor rota", o sistema retorna um **conjunto de rotas Pareto-óptimas** onde:
- Nenhuma rota é melhor em todos os critérios
- Cada rota representa um trade-off diferente
- O utilizador escolhe consoante prioridades pessoais

### Classe Solution

Cada solução tem 5 atributos:

```python
class Solution:
    total_time: int          # Tempo em segundos
    total_co2: float         # CO2 em gramas
    total_walk_km: float     # Caminhada em km
    arrival_sec: int         # Hora chegada (seg desde meia-noite)
    path: List[Segment]      # Sequência de segmentos
```

---

## 📚 Conjunto de Casos de Teste

O projeto inclui **22 casos de teste** para validação e comparação dos algoritmos:

```
🟢 TRIVIAL (2 casos)
   TC-1.1: Caminhada simples
   TC-1.2: Transporte direto

🟡 LOW (3 casos)
   TC-2.1: Uma transferência
   TC-2.2: Hora de pico
   TC-7.2: Hub principal

🟠 MEDIUM (3 casos)
   TC-3.1: Duas transferências
   TC-3.2: Origem periférica
   TC-3.3: Trade-off tempo/eco

🔴 HIGH (5 casos)
   TC-4.1: Distância longa
   TC-4.2: Rede complexa
   TC-4.3: Madrugada
   TC-4.4: Transporte longo
   TC-4.5: Múltiplas paragens

🔵 SPECIAL (5 casos)
   TC-5.1: Solução única
   TC-5.2: Diversidade Pareto
   TC-5.3: A* vs Dijkstra
   TC-5.4: CO2 muito diferentes
   TC-5.5: ACO stochástico

⚫ EXTREME (4 casos)
   TC-6.1: Origem=Destino
   TC-6.2: Madrugada
   TC-6.3: Tempo restritivo
   TC-6.4: Localização isolada
```

---

## 📖 Documentação

- **[USER_GUIDE.md](USER_GUIDE.md)**: Guia completo com exemplos práticos
- **[route-optimization-optimized.ipynb](notebook/route-optimization-optimized.ipynb)**: Análise interativa
- **Código comentado**: Cada ficheiro tem documentação em docstrings

---

## ⚙️ Dependências Principais

```
networkx (3.6.1+)      # Grafos
osmnx (2.0.7+)         # OpenStreetMap
pandas (2.3.3+)        # Dados
scipy (1.16.3+)        # Algoritmos numéricos
shapely (2.1.2+)       # Geometria
gtfs-kit (12.0.0+)     # GTFS parsing
geopy (2.4.1+)         # Geocoding
folium (0.20.0+)       # Mapas interativos
matplotlib (3.10.8+)   # Visualização
fastapi (0.100.0+)     # API REST
uvicorn (0.24.0+)      # ASGI server
```

Ver [requirements.txt](requirements.txt) para versões exatas.

---

## 🔍 Resolução de Problemas

### ImportError ao executar

```bash
# Certifique-se que está no diretório correto
cd CIN_GRUPO6/code
python -m app.test_cases
```

### UnicodeEncodeError (Windows)

```bash
set PYTHONIOENCODING=utf-8
python -m app.test_cases
```

### Nenhuma rota encontrada

- Verificar coordenadas (devem ser no Porto)
- Testar com casos de teste primeiro: `python -m app.test_cases`
- Ver [USER_GUIDE.md](USER_GUIDE.md) secção "Resolução de Problemas"

### Algoritmo muito lento

- **A***: Aumentar `RELAXATION_FACTOR`
- **Dijkstra**: Normal estar lento (é exaustivo)
- **ACO**: Diminuir `num_iterations`

---

## 📝 Licença

Este projeto é parte de avaliação académica da disciplina Conceitos de Informática II (CIN) da FEUP.

---

## 👥 Autores

Grupo 6 - CIN - FEUP - 2025

---

## 📚 Referências Académicas

### Algoritmos de Roteamento

1. Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). A formal basis for the heuristic determination of minimum cost paths. *IEEE Transactions on Systems Science and Cybernetics*, 4(2), 100-107.

2. Dijkstra, E. W. (1959). A note on two problems in connexion with graphs. *Numerische Mathematik*, 1(1), 269-271.

3. Dorigo, M., & Stützle, T. (2004). *Ant Colony Optimization*. MIT Press.

### Roteamento Multimodal

4. Pyrga, E., Schulz, F., Wagner, D., & Zaroliagis, C. (2008). Efficient models for timetable information in public transportation systems. *ACM Journal of Experimental Algorithmics*, 12, 1-39.

5. Müller-Hannemann, M., & Schnee, M. (2004). Finding all attractive train connections by multi-criteria Pareto search. *Transportation Research Record*, 1915(1), 246-263.

### Emissões e Sustentabilidade

6. McKinnon, A. C., & Piecyk, M. (2009). Measurement of CO2 emissions from road freight transport: A comparative study of available tools. *Energy Policy*, 37(10), 3657-3665.

7. European Environment Agency (2022). *Greenhouse gas emissions from transport in Europe*. EEA Report No. 13/2022.

---

**Versão**: 1.0  
**Última atualização**: Dezembro 2025  
**Status**: Produção
