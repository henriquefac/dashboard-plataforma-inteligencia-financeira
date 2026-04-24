# Frontend (Dashboard de Inteligência Financeira)

Este é o frontend da plataforma, desenvolvido para fornecer uma visualização clara, interativa e inteligente dos dados financeiros processados pelo backend.

## Design e UX

### Por que Streamlit?
O **Streamlit** foi escolhido para o desenvolvimento do MVP devido a:
- **Velocidade de Entrega**: Permite transformar scripts de dados em interfaces web ricas em tempo recorde.
- **Componentes Nativos**: Integração perfeita com bibliotecas de visualização como Plotly e tabelas interativas.
- **Foco no Dado**: A arquitetura do framework facilita a construção de fluxos onde o dado é o principal.

### Arquitetura de Componentes
Para manter o código limpo e escalável, a aplicação foi dividida em componentes modulares:
- **Sidebar de Filtros**: Gerenciamento dinâmico do estado dos dados.
- **Cartões de Métricas**: Visualização rápida de KPIs (Receita, Inadimplência, etc).
- **Evolução Temporal**: Gráficos detalhados sobre a saúde financeira ao longo do tempo.
- **Sidebar Analítica**: Interface de chat para interação em linguagem natural com o Agente Analítico.

## Otimizações de Performance

### Lidando com o Rerun do Streamlit
O Streamlit reexecuta todo o script a cada interação. Para mitigar isso e garantir uma experiência fluida:
- **st.cache_data**: Implementamos cache pesado nas chamadas de API. Se os parâmetros não mudarem, o frontend não solicita novos dados ao backend, economizando tráfego e tempo.
- **Async Integration**: Chamadas ao backend são feitas de forma otimizada para suportar o processamento assíncrono do FastAPI, garantindo que a UI não trave durante gerações de IA.

## Tecnologias Principais

- **Streamlit**: Core do frontend.
- **Pydantic**: Validação de esquemas de resposta da API.
- **Httpx**: Cliente HTTP assíncrono para comunicação com o backend.
- **Plotly**: Visualizações de dados dinâmicas.

## Estrutura de Pastas

- `app/api`: Cliente de integração com o backend FastAPI.
- `app/components`: Componentes de UI isolados e reutilizáveis.
- `app/models`: Definições de modelos de dados (Pydantic).
- `app/main.py`: Ponto de entrada da aplicação.

## Instalação e Execução

### Pré-requisitos
- Python 3.12+
- Backend em execução (ver README do backend).

### Passo a Passo
1. Instale as dependências:
   ```bash
   uv sync
   ```
2. Inicie a aplicação:
   ```bash
   streamlit run app/main.py
   ```

O dashboard estará disponível em `http://localhost:8501`.
