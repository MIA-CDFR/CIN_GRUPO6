# Manual de Utilizador - Sistema de Roteamento Multimodal do Porto

## Índice
1. [Introdução](#introdução)
2. [Instalação](#instalação)
3. [Configuração](#configuração)
4. [Início Rápido](#início-rápido)
5. [API REST](#api-rest)
6. [Algoritmos Disponíveis](#algoritmos-disponíveis)
7. [Interpretação de Resultados](#interpretação-de-resultados)
8. [Testes e Validação](#testes-e-validação)
9. [Resolução de Problemas](#resolução-de-problemas)
10. [FAQ](#faq)

---

## Introdução

O Sistema de Roteamento Multimodal do Porto é uma ferramenta avançada de otimização de rotas que combina múltiplos meios de transporte (autocarro, comboio/metro, caminhada) na área metropolitana do Porto.

### Características Principais

- **Otimização Multi-Objetivo**: Minimiza simultaneamente tempo de viagem, emissões de CO2 e distância de caminhada
- **Três Algoritmos**: A* heurístico, Dijkstra exaustivo e ACO estocástico
- **Dados Reais**: Integra horários GTFS do Metro do Porto e STCP, redes OSM
- **Fronteira Pareto**: Encontra múltiplas soluções eficientes, não uma única "melhor rota"
- **REST API**: Interface para integração em outras aplicações

### Requisitos do Sistema

- **Python**: 3.10 ou superior
- **Sistema Operativo**: Windows, macOS, Linux
- **Memória RAM**: Mínimo 4 GB (recomendado 8 GB)
- **Espaço em Disco**: 500 MB (incluindo dados GTFS)

---

## Instalação

### Passo 1: Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/CIN_GRUPO6.git
cd CIN_GRUPO6/code
```

### Passo 2: Instalar Dependências

#### Opção A: Com Poetry (Recomendado)

```bash
# Instalar Poetry (se não tiver)
pip install poetry

# Instalar dependências
poetry install

# Ativar ambiente virtual
poetry shell
```

#### Opção B: Com pip

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Windows:
venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### Passo 3: Descarregar Dados GTFS (Opcional)

Se os ficheiros GTFS não estiverem presentes:

```bash
# Os dados já estão incluídos em feeds/
# Se precisar atualizar:
python -c "from app.utils.feed import update_gtfs; update_gtfs()"
```

### Passo 4: Verificar Instalação

```bash
# Testar se tudo está funcionando
python -m app.test_cases

# Deve ver um resumo de 22 casos de teste
```

---

## Configuração

### Estrutura de Ficheiros

```
code/
├── app/
│   ├── main.py              # Entrada principal / API
│   ├── test_cases.py        # Casos de teste
│   ├── models/              # Modelos de dados
│   ├── services/            # Lógica principal
│   │   ├── graph.py         # Construção da rede
│   │   ├── solution.py      # Classe de solução
│   │   └── algoritms/       # Implementações dos algoritmos
│   └── utils/               # Utilitários
│       ├── co2.py           # Cálculo de emissões
│       ├── feed.py          # Processamento GTFS
│       ├── geo.py           # Operações geográficas
│       ├── route.py         # Cálculo de rotas
│       └── time.py          # Manipulação temporal
├── feeds/                   # Dados GTFS
│   ├── gtfs_metro/          # Metro do Porto
│   └── gtfs_stcp/           # STCP (autocarros)
└── requirements.txt         # Dependências
```

### Variáveis de Ambiente

Criar ficheiro `.env` (opcional):

```env
# Logging
LOG_LEVEL=INFO

# Performance
MAX_WALKING_DISTANCE_KM=2.0
MAX_WAIT_TIME_SEC=1800

# API
API_HOST=localhost
API_PORT=8000
DEBUG=False
```

---

## Início Rápido

### Opção 1: Script Python Simples

```python
from app.services.graph import MultimodalGraph
from app.services.algoritms.a_star import AStarRouter
from app.utils.geo import get_coordinates

# 1. Construir a rede multimodal
graph = MultimodalGraph()
graph.build_from_gtfs()

# 2. Definir origem e destino
origin_coords = get_coordinates("Livraria Bertrand, Porto")
destination_coords = get_coordinates("Torre dos Clérigos, Porto")

start_time = "09:00:00"

# 3. Executar A*
router = AStarRouter(graph)
solutions = router.find_routes(
    origin=origin_coords,
    destination=destination_coords,
    start_time=start_time
)

# 4. Visualizar resultados
for i, solution in enumerate(solutions, 1):
    print(f"Rota {i}:")
    print(f"  Tempo: {solution.total_time}s ({solution.total_time//60}min)")
    print(f"  CO2: {solution.total_co2:.1f}g")
    print(f"  Caminhada: {solution.total_walk_km:.2f}km")
    print()
```

### Opção 2: Linha de Comando

```bash
# Ainda não implementado - ver Opção 3 (API REST)
```

### Opção 3: API REST

```bash
# Iniciar servidor
python -m uvicorn app.main:app --reload

# Num outro terminal, fazer pedido:
curl -X POST http://localhost:8000/api/routes \
  -H "Content-Type: application/json" \
  -d '{
    "origin": {"lat": 41.1579, "lon": -8.6291},
    "destination": {"lat": 41.1625, "lon": -8.6362},
    "start_time": "09:00:00",
    "algorithm": "astar"
  }'
```

---

## API REST

### Endpoints Disponíveis

#### `POST /api/routes`

Calcular rotas entre dois pontos.

**Request:**
```json
{
  "origin": {
    "lat": 41.1579,
    "lon": -8.6291
  },
  "destination": {
    "lat": 41.1625,
    "lon": -8.6362
  },
  "start_time": "09:00:00",
  "algorithm": "astar",
  "max_walking_km": 2.0,
  "max_wait_time_sec": 1800
}
```

**Response:**
```json
{
  "status": "success",
  "algorithm": "astar",
  "num_solutions": 3,
  "solutions": [
    {
      "total_time": 1200,
      "total_co2": 45.3,
      "total_walk_km": 0.5,
      "arrival_sec": 32400,
      "path": [
        {
          "type": "walk",
          "distance_km": 0.3,
          "duration_sec": 180
        },
        {
          "type": "bus",
          "route_id": "13",
          "trip_id": "trip_001",
          "departure_time": "09:05:00",
          "arrival_time": "09:15:00"
        }
      ]
    }
  ],
  "computation_time_sec": 0.234
}
```

**Parâmetros:**
- `origin` (obrigatório): Coordenadas de origem {lat, lon}
- `destination` (obrigatório): Coordenadas de destino {lat, lon}
- `start_time` (obrigatório): Hora de partida (HH:MM:SS)
- `algorithm` (opcional): "astar", "dijkstra" ou "aco" (padrão: "astar")
- `max_walking_km` (opcional): Distância máxima de caminhada (padrão: 2.0 km)
- `max_wait_time_sec` (opcional): Tempo máximo de espera (padrão: 1800 sec)

#### `GET /api/health`

Verificar estado do servidor.

```bash
curl http://localhost:8000/api/health
```

Response:
```json
{
  "status": "healthy",
  "graph_loaded": true,
  "num_stops": 1250,
  "num_routes": 45
}
```

#### `GET /api/algorithms`

Listar algoritmos disponíveis.

```bash
curl http://localhost:8000/api/algorithms
```

---

## Algoritmos Disponíveis

### 1. A* (A-Star) - Recomendado para Uso Geral

**Características:**
- Heurístico: usa estimativa de distância para guiar a busca
- Rápido: tempo de computação típico de 0.1-0.5 segundos
- Aproximado: pode não encontrar todas as soluções
- Ideal para: tempo real, navegação interativa

**Parâmetros:**
```python
{
    "MAX_LABELS_PER_NODE": 10,      # Máximo de soluções por nó
    "TIME_WINDOW_EPSILON": 120,      # Tolerância de agrupamento (segundos)
    "RELAXATION_FACTOR": 1.5         # Fator de relaxação para pruning
}
```

**Uso:**
```python
from app.services.algoritms.a_star import AStarRouter

router = AStarRouter(graph)
solutions = router.find_routes(origin, destination, start_time)
```

### 2. Dijkstra - Garantia Teórica

**Características:**
- Exaustivo: testa todas as possibilidades
- Completo: encontra a fronteira Pareto óptima
- Lento: tempo de computação de 5-30 segundos
- Ideal para: pesquisa offline, validação de qualidade

**Parâmetros:**
```python
{
    "MAX_LABELS_PER_NODE": 8,
    "TIME_WINDOW_EPSILON": 60
}
```

**Uso:**
```python
from app.services.algoritms.dijkstra import DijkstraRouter

router = DijkstraRouter(graph)
solutions = router.find_routes(origin, destination, start_time)
```

### 3. ACO (Ant Colony Optimization) - Busca Criativa

**Características:**
- Estocástico: resultados variam entre execuções
- Criativo: pode descobrir rotas não óbvias
- Moderado: tempo de 2-10 segundos
- Ideal para: exploração, descoberta de alternativas, análise sensibilidade

**Parâmetros:**
```python
{
    "ALPHA": 1.0,          # Peso de feromona
    "BETA": 3.0,           # Peso de heurística
    "RHO": 0.1,            # Taxa de evaporação
    "Q": 100,              # Quantidade de feromona depositada
    "num_ants": 30,        # Número de formigas por iteração
    "num_iterations": 20   # Número de iterações
}
```

**Uso:**
```python
from app.services.algoritms.aco import ACORouter

router = ACORouter(graph)
solutions = router.find_routes(origin, destination, start_time)
```

### Comparação Rápida

| Critério | A* | Dijkstra | ACO |
|----------|-----|----------|-----|
| Velocidade | ⚡⚡⚡ | ⚡ | ⚡⚡ |
| Completude | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Uso Real | ✅ | ❌ | ⚠️ |
| Paralelizável | ✅ | ❌ | ✅ |

---

## Interpretação de Resultados

### Entender a Classe Solution

Cada solução retornada tem estes atributos:

```python
solution.total_time       # Tempo total em segundos
solution.total_co2        # Emissões em gramas
solution.total_walk_km    # Distância a pé em km
solution.arrival_sec      # Hora de chegada (segundos desde meia-noite)
solution.path             # Lista de segmentos (walk/transit)
```

### Exemplo: Interpretar uma Solução

```python
# Rota de Clérigos a Gaia Centre
if solutions:
    best = solutions[0]
    
    print(f"Tempo de viagem: {best.total_time//60} min e {best.total_time%60} seg")
    print(f"Emissões CO2: {best.total_co2:.1f}g (equivalente a {best.total_co2/1000:.2f}kg)")
    print(f"Caminhada: {best.total_walk_km:.2f}km")
    
    # Chegada esperada
    hours = best.arrival_sec // 3600
    minutes = (best.arrival_sec % 3600) // 60
    print(f"Chega às: {hours:02d}:{minutes:02d}")
    
    # Analisar segmentos
    for seg in best.path:
        if seg["type"] == "walk":
            print(f"  - Caminhar {seg['distance_km']:.2f}km")
        else:  # transit
            print(f"  - {seg['type'].upper()} linha {seg['route_id']}")
            print(f"    Depart: {seg['departure_time']} -> Chega: {seg['arrival_time']}")
```

### A Fronteira Pareto

O sistema não retorna "a melhor rota", mas um conjunto de **rotas Pareto-óptimas** onde não há nenhuma que seja melhor em todos os critérios simultaneamente.

**Exemplo:**

| Rota | Tempo | CO2 | Caminhada |
|------|-------|-----|-----------|
| 1 | 25 min | 80g | 0.5 km |
| 2 | 35 min | 20g | 1.0 km |
| 3 | 30 min | 60g | 0.8 km |

- Rota 1 é melhor em tempo
- Rota 2 é melhor em CO2
- Rota 3 não é Pareto-óptima (dominada por combinações das outras)

**Usar estas rotas consoante a sua prioridade:**

```python
# Se quer ser rápido
fastest = min(solutions, key=lambda s: s.total_time)

# Se quer ser ecológico
greenest = min(solutions, key=lambda s: s.total_co2)

# Se quer caminhar pouco
walkless = min(solutions, key=lambda s: s.total_walk_km)
```

---

## Testes e Validação

### Executar Casos de Teste

```bash
# Listar todos os 22 casos de teste
python -m app.test_cases
```

Vê uma lista organizada por complexidade:

- 🟢 **Trivial** (2 casos): Rotas muito simples para validação básica
- 🟡 **Low** (3 casos): Transferências simples
- 🟠 **Medium** (3 casos): Casos realistas comuns
- 🔴 **High** (5 casos): Rotas longas e complexas
- 🔵 **Special** (5 casos): Edge cases e validação de algoritmos
- ⚫ **Extreme** (4 casos): Testes de robustez

### Exemplos de Teste

```python
from app.test_cases import TestCaseEvaluator

# Obter um caso específico
test = TestCaseEvaluator.get_by_id("TC-2.1")
print(f"Teste: {test['name']}")
print(f"Origem: {test['origem']}")
print(f"Destino: {test['destino']}")

# Executar rota e validar
origin_coords = get_coordinates(test['origem'])
dest_coords = get_coordinates(test['destino'])

solutions = router.find_routes(origin_coords, dest_coords, test['start_time'])

# Validar que cumpre critérios
is_valid, violations = TestCaseEvaluator.validate_solution(solutions[0], test)

if is_valid:
    print("✅ Solução válida!")
else:
    for v in violations:
        print(f"⚠️ {v}")
```

### Comparação Entre Algoritmos

```python
from app.services.algoritms.a_star import AStarRouter
from app.services.algoritms.dijkstra import DijkstraRouter
from app.services.algoritms.aco import ACORouter

astar_router = AStarRouter(graph)
dijkstra_router = DijkstraRouter(graph)
aco_router = ACORouter(graph)

# Executar todos os três
import time

algorithms = {
    "A*": astar_router,
    "Dijkstra": dijkstra_router,
    "ACO": aco_router
}

for name, router in algorithms.items():
    start = time.time()
    solutions = router.find_routes(origin, destination, start_time)
    elapsed = time.time() - start
    
    print(f"{name}:")
    print(f"  Tempo computação: {elapsed:.3f}s")
    print(f"  Rotas encontradas: {len(solutions)}")
    print(f"  Melhor tempo: {min(s.total_time for s in solutions)//60}min")
    print(f"  Mais eco: {min(s.total_co2 for s in solutions):.1f}g CO2")
    print()
```

---

## Resolução de Problemas

### Problema: ImportError ao executar

```
ModuleNotFoundError: No module named 'app'
```

**Solução:**
Certifique-se que está no diretório `code/`:

```bash
cd CIN_GRUPO6/code
python -m app.test_cases
```

### Problema: UnicodeEncodeError com emojis

```
UnicodeEncodeError: 'charmap' codec can't encode character
```

**Solução (Windows):**
```bash
set PYTHONIOENCODING=utf-8
python -m app.test_cases
```

**Solução (macOS/Linux):**
```bash
export PYTHONIOENCODING=utf-8
python -m app.test_cases
```

### Problema: Nenhuma rota encontrada

**Causas possíveis:**
1. Coordenadas inválidas
2. Origem/destino muito distante (> 10 km)
3. Hora muito tarde (sem serviço noturno)
4. Dados GTFS desatualizados

**Debug:**
```python
from app.utils.geo import get_coordinates

# Verificar se geocoding funciona
coords = get_coordinates("Livraria Bertrand, Porto")
print(f"Coordenadas: {coords}")  # Deve ter 'lat' e 'lon'

# Verificar rede
print(f"Stops na rede: {len(graph.stops)}")
print(f"Rotas: {len(graph.routes)}")
```

### Problema: Algoritmo muito lento

**Para A*:** Aumentar `RELAXATION_FACTOR` (e.g., 2.0 em vez de 1.5)

**Para Dijkstra:** Normal estar lento - é exaustivo

**Para ACO:** Diminuir `num_iterations` (e.g., 10 em vez de 20)

### Problema: Resultados diferentes entre execuções

**Normal com ACO** - é estocástico por design. Use Dijkstra se precisar resultados determinísticos.

---

## FAQ

### P: Qual algoritmo devo usar?

**R:** 
- **Desenvolvimento/Debug**: A* (rápido)
- **Produção**: A* (equilíbrio velocidade-qualidade)
- **Pesquisa Académica**: Dijkstra (garantia teórica)
- **Análise Sensibilidade**: ACO (diversidade)

### P: Porque é que há múltiplas rotas e não "uma melhor"?

**R:** Porque o problema é multi-objetivo! Não há uma rota que seja melhor em tempo, CO2 E caminhada simultaneamente. As múltiplas rotas permitem escolher a que melhor se adequa aos seus objetivos.

### P: Como adiciono uma nova paragem?

**R:** As paragens vêm do GTFS (dados reais do Metro e STCP). Para adicionar, teria de modificar a API de transporte (fora do escopo deste sistema).

### P: Posso usar isto para rotas fora do Porto?

**R:** Teoricamente sim, se carregar dados GTFS de outra região em `feeds/`. Mas o OSM para ruas estradas é específico para Porto (arredondado para melhor performance).

### P: Qual é a precisão das emissões CO2?

**R:** Baseada em valores médios por modo de transporte (literatura académica). Não é tão precisa como simular com dados meteorológicos/congestionamento reais.

### P: Posso paralelizar múltiplos pedidos?

**R:** Sim! A*  e ACO são thread-safe. Use `concurrent.futures.ThreadPoolExecutor`:

```python
from concurrent.futures import ThreadPoolExecutor

test_cases = TestCaseEvaluator.get_all_names()

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = []
    for test_id, _ in test_cases:
        test = TestCaseEvaluator.get_by_id(test_id)
        future = executor.submit(run_test, test)
        futures.append(future)
    
    results = [f.result() for f in futures]
```

### P: Onde encontro mais documentação técnica?

**R:** Ver [README.md](README.md) para arquitetura detalhada e referências académicas.

---

## Contacto e Suporte

Para questões ou problemas:
1. Consulte este manual
2. Verifique a secção README.md do projeto
3. Execute `python -m app.test_cases` para validar instalação

---

**Versão**: 1.0  
**Última atualização**: Dezembro 2025  
**Autores**: Grupo 6 - CIN - FEUP
