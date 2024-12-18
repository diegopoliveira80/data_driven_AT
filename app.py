import streamlit as st
import requests
import json
import pandas as pd
import numpy as np
from routers.agent import get_sport_specialist_comments_about_match
from routers.competitions import get_player_stats
from mplsoccer import Radar, FontManager, grid
import matplotlib.pyplot as plt


st.set_page_config(layout="wide",
                   page_title="Football Match Conversation App",
                   page_icon="⚽️")


st.title("Football Match App")
from statsbombpy import sb

######################################################### CARREGAMENTO DOS DADOS
@st.cache_data()
def load_competitions() -> json:
    api = 'http://127.0.0.1:8000/api/competicoes/'
    response = requests.get(api)
    return json.loads(response.json())

@st.cache_data()
def load_matches(competition_id: int, season_id: int) -> json:
    api = f'http://127.0.0.1:8000/api/partidas/?competition_id={competition_id}&season_id={season_id}'    
    response = requests.get(api)
    return  json.loads(response.json())


@st.cache_data()
def load_lineups(match_id: int):
    api = f'http://127.0.0.1:8000/api/escalacao/?match_id={match_id}'
    response = requests.get(api)
    return json.loads(response.json())


@st.cache_data()
def load_lineups2(match_id: int):
    api = f'http://127.0.0.1:8000/api/escalacao2/?match_id={match_id}'    
    response = requests.get(api)
    return  json.loads(response.json())
    
    
@st.cache_data()
def load_events(match_id: int):
    api = f'http://127.0.0.1:8000/api/eventos/?match_id={match_id}'    
    response = requests.get(api)
    return  json.loads(response.json())
    
    
@st.cache_data()
def load_stats(match_id: int, player_name: str) -> json:
    api = f'http://127.0.0.1:8000/api/player_profile/?match_id={match_id}&player_name={player_name}'    
    try:
        # Fazer a requisição
        response = requests.get(api)
        
        # Verificar o status da resposta
        if response.status_code != 200:
            raise Exception(f"Erro na requisição: {response.status_code} - {response.text}")
                    
        # Verificar se a resposta não está vazia
        if not response.text.strip():
            raise Exception("A resposta da API está vazia.")
        
        # Tentar carregar a resposta como JSON
        try:
            return json.loads(response.json())
        except ValueError as e:
            raise Exception(f"Erro ao decodificar JSON: {e} - Resposta: {response.text}")
    
    except requests.RequestException as e:
        raise Exception(f"Erro na requisição: {e}")
        


#def load_summary(match_details, line_ups):
    #match_details_json = json.dumps(match_details)  # Lista de dicionários para JSON
    #line_ups_json = json.dumps(line_ups)  # Dicionário para JSON
    #api = f'http://127.0.0.1:8000/api/match_summary/?match_details={match_details_json}&line_ups={line_ups_json}'    
    #response = requests.get(api)
    # return json.loads(response.json())

######################################################### Streamlit Sidebar
st.sidebar.title("Football Match Selector")
# Step 1: Selecione a competição
selected_competition = None
selected_season = None
selected_match = None
match_id = None
match_details = None
specialist_comments = None



# Step 1: Selecione a competição
st.sidebar.header("Step 1: Selecione a competição")
competitions = load_competitions()  # Função que carrega as competições
competition_names = sorted(set([comp['competition_name'] for comp in competitions]))

# Inicializando as chaves de session_state
if 'selected_competition' not in st.session_state:
    st.session_state.selected_competition = None
if 'selected_season' not in st.session_state:
    st.session_state.selected_season = None
if 'selected_match' not in st.session_state:
    st.session_state.selected_match = None

# Seleção da competição
selected_competition = st.sidebar.selectbox("Escolha uma competição", 
                                            competition_names, 
                                            index=competition_names.index(st.session_state.selected_competition) 
                                            if st.session_state.selected_competition in competition_names else 0)
if selected_competition:
    st.session_state.selected_competition = selected_competition

    # Step 2: Selecione uma temporada
    st.sidebar.header("Step 2: Selecione uma temporada")
    seasons = set(comp['season_name'] for comp in competitions if comp['competition_name'] == selected_competition)
    selected_season = st.sidebar.selectbox("Escolha uma temporada", 
                                           sorted(seasons), 
                                           index=sorted(seasons).index(st.session_state.selected_season) 
                                           if st.session_state.selected_season in seasons else 0)
    
    if selected_season:
        st.session_state.selected_season = selected_season

        # Get the selected competition ID
        competition_id = next(
            (comp['competition_id'] for comp in competitions if comp['competition_name'] == selected_competition),
            None
        )
        season_id = next(
            (comp['season_id'] for comp in competitions 
            if comp['season_name'] == selected_season 
            and comp['competition_name'] == selected_competition),
            None
        )

        # Step 3: Selecione uma partida
        st.sidebar.header("Step 3: Selecione a Partida")
        matches = load_matches(competition_id, season_id)  # Função que carrega as partidas
        match_names = sorted([f"{match['home_team']} vs {match['away_team']}" for match in matches])

        if selected_match := st.sidebar.selectbox("Escolha uma partida", 
                                                  match_names, 
                                                  index=match_names.index(st.session_state.selected_match) 
                                                  if st.session_state.selected_match in match_names else 0):
            st.session_state.selected_match = selected_match
            # Get the selected match ID
            match_details = next(
                (match for match in matches if f"{match['home_team']} vs {match['away_team']}" == selected_match),
                None
            )
            match_id = match_details['match_id']

######################################################### Abas
################################################# Dados Brutos

tab1, tab2, tab3 = st.tabs(["Dados Brutos", "Resumo da partida", "Detalhes"])

with tab1:
    st.write('COMPETIÇÕES')
    dados_competicao = load_competitions()
    df_competicao = pd.DataFrame(dados_competicao)
    st.write(df_competicao)
    
    st.write('PARTIDAS')
    competicao_partidas = df_competicao[
        (df_competicao['competition_name'] == selected_competition) & 
        (df_competicao['season_name'] == selected_season)]

    dados_partidas = load_matches(competition_id=competicao_partidas['competition_id'].iloc[0], 
                                season_id=competicao_partidas['season_id'].iloc[0])
    df_partidas = pd.DataFrame(dados_partidas)
    st.write(df_partidas)

################################################# Resumo da partida
from statsbombpy import sb


with tab2:
    time1 = load_lineups(match_id=match_id)[0]
    time2 = load_lineups(match_id=match_id)[1]
    escalacao = load_lineups2(match_id=match_id)
    eventos = load_events(match_id=match_id)
    

    lista_jogadores_times = [escalacao[i] for i in escalacao]
    lista_nomes = [x['player_name'] for i in lista_jogadores_times for x in i if x['positions']['positions']]
    
    lista_statisticas = []
    for nomes in lista_nomes:
        stats_jogadores = {nomes: load_stats(match_id,nomes)}
        lista_statisticas.append(stats_jogadores)

 ################################################# Resumo LLM
    with st.container():
        dados_partida_selecionada = df_partidas[df_partidas['match_id'] == match_id].to_dict(orient='records')
        
        with st.expander('Ver resumo da partida'):
            if st.button('Resumir',key="botao1"):
                agent_prompt = """
                    Você é um comentarista esportivo com formação em futebol. Responda como
                    se você estiver fornecendo análises envolventes para um público de TV. Aqui está o
                    informações a incluir:

                    Instruções:
                    1. Visão geral do jogo:
                        - Especifique quando e onde o jogo aconteceu.
                        - Qual foi o resultado final da partida.
                        - Quais jogadores fizeram os gols
                        - Melhor jogador em campo
                    3. Análise do XI inicial:
                        - Avaliar as escalações iniciais de ambas as equipes.
                        - Destaque os principais jogadores e suas funções.
                    3. Entrega envolvente:
                        - Use um tom animado, profissional e perspicaz ao comentar
                        atraente para fãs de todos os níveis de habilidade.
                    4. Gols marcados:
                        Exemplo:
                        - Nome jogador: 1 Gols 
                    5. Cartões amarelo e vermelho:
                        Exemplo:
                        - Amarelo: Nome do Jogador 
                        - Vermelho: Nome do Jogador
                    
                    Os detalhes da partida são fornecidos abaixo: 
                    {dados1}
                    
                    Os detalhes das statisticas de cada jogador são fornecidos abaixo: 
                    {dados2}
                    
                    As escalações das equipes são fornecidas aqui:
                    {dados3}
                    
                    Forneça comentários de especialistas sobre a partida durante uma transmissão esportiva.
                    Comece sua análise agora e envolva seu público com seus insights.
                    """
                
                st.write(get_sport_specialist_comments_about_match(dados_partida_selecionada,
                                                                    lista_statisticas,
                                                                    escalacao,
                                                                    agent_prompt))
    
    
 ################################################# ESCALAÇÃO INICIAL

    st.subheader("ESCALAÇÃO INICIAL")
    col1, col2 = st.columns(2)
    with col1:
        # Filtrando apenas jogadores com posições escaladas
        escalados = [player for player in time1[list(time1.keys())[0]]]

        resultados = [[jogador['positions'][0]['position_id'], jogador['player_name'], 
                    str(jogador['jersey_number']), jogador['positions'][0]['position']]
            for jogador in escalados if jogador['positions']  and jogador['positions'][0]['from'] == '00:00' ]        
        
        escalados_info_sorted = sorted(resultados, key=lambda x: x[0])         
                
        
        for i in escalados_info_sorted:        
            st.write(i[2]," - ",i[1]," - ",i[3])
    
    with col2:
        # Filtrando apenas jogadores com posições escaladas
        escalados = [player for player in time2[list(time2.keys())[0]]]

        resultados = [[jogador['positions'][0]['position_id'], jogador['player_name'], 
                    str(jogador['jersey_number']), jogador['positions'][0]['position']]
            for jogador in escalados if jogador['positions']  and jogador['positions'][0]['from'] == '00:00' ]
        
        escalados_info_sorted = sorted(resultados, key=lambda x: x[0])         
                
        
        for i in escalados_info_sorted:        
            st.write(i[2]," - ",i[1]," - ",i[3])
    
    
################################################# Resumo do Jogador
    st.markdown("<br><br><br>", unsafe_allow_html=True)
            
    col1, col2 = st.columns(2)
    with st.container():
        with col1:
            jogadores1 = [player for player in time1[list(time1.keys())[0]]]
            jogadores1 = [i['player_name'] for i in jogadores1]
            
            selected_player = st.selectbox("ESCOLHA UM JOGADOR",jogadores1)

            st.write(load_stats(match_id,selected_player))

        with col2:
            jogadores2 = [player for player in time2[list(time2.keys())[0]]]
            jogadores2 = [i['player_name'] for i in jogadores2]
            
            selected_player2 = st.selectbox("ESCOLHA UM JOGADOR",jogadores2)

            st.write(load_stats(match_id,selected_player2))

################################################# Graficos
        def create_radar_plot():
            params = list(load_stats(match_id,selected_player2).keys())
            #lower_is_better = ['passes_completed']
            # Os limites inferior e superior das estatísticas
            low =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            high = [60, 110, 10, 10, 5, 5, 5, 10, 15, 20, 5, 5, 5]

            radar = Radar(params, low, high,
                        #lower_is_better=lower_is_better,
                        round_int=[False]*len(params),
                        num_rings=4,
                        ring_width=1, center_circle_radius=1)

            jogador1 =  list(load_stats(match_id,selected_player).values())
            jogador2 =  list(load_stats(match_id,selected_player2).values())

# creating the figure using the grid function from mplsoccer:
            fig, axs = grid(figheight=14, grid_height=0.915, title_height=0.06, endnote_height=0.025,
                            title_space=0, endnote_space=0, grid_key='radar', axis=False)

            # plot radar
            radar.setup_axis(ax=axs['radar'])  # format axis as a radar
            rings_inner = radar.draw_circles(ax=axs['radar'], facecolor='#d1d6d0', edgecolor='#929692')
            radar_output = radar.draw_radar_compare(jogador1, jogador2, ax=axs['radar'],
                                                    kwargs_radar={'facecolor': '#00f2c1', 'alpha': 0.6},
                                                    kwargs_compare={'facecolor': '#d80499', 'alpha': 0.6})
            radar_poly, radar_poly2, vertices1, vertices2 = radar_output
            range_labels = radar.draw_range_labels(ax=axs['radar'], fontsize=25)
            param_labels = radar.draw_param_labels(ax=axs['radar'], fontsize=25)
            axs['radar'].scatter(vertices1[:, 0], vertices1[:, 1],
                                c='#00f2c1', edgecolors='#6d6c6d', marker='o', s=150, zorder=2)
            axs['radar'].scatter(vertices2[:, 0], vertices2[:, 1],
                                c='#d80499', edgecolors='#6d6c6d', marker='o', s=150, zorder=2)

            # adding the endnote and title text (these axes range from 0-1, i.e. 0, 0 is the bottom left)
            # Note we are slightly offsetting the text from the edges by 0.01 (1%, e.g. 0.99)
            endnote_text = axs['endnote'].text(0.99, 0.5, 'Inspired By: StatsBomb / Rami Moghadam', fontsize=15, ha='right', va='center')
            title1_text = axs['title'].text(0.01, 0.65, selected_player, fontsize=25, color='#01c49d', ha='left', va='center')
            title3_text = axs['title'].text(0.99, 0.65, selected_player2, fontsize=25,ha='right', va='center', color='#d80499')

            
            return fig

        st.title("Radar Chart Visualization")
        fig = create_radar_plot()
        st.pyplot(fig)


    ################################################# Resumo do Jogador LLM
        stats_jogador1 = {selected_player: load_stats(match_id,selected_player)}
        stats_jogador2 = {selected_player2: load_stats(match_id,selected_player2)}

        with st.expander('Ver comparativo entre os Jogadores'):
            if st.button('Resumir',key="botao2"):
                agent_prompt = """
                    Você é um especialista em analisar partidas de futebol, e seu objetivo é analisar as 
                    estatisticas de dois jogadores e comparar a performace entre eles:

                    Analise e compare o desempenho de Jogador A e Jogador B em uma partida de futebol usando os 
                    seguintes dados estatísticos:
                        -Passes Completados: Indica a precisão no passe e a contribuição para a construção do jogo.
                        -Passes Tentados: Mostra a frequência de envolvimento na distribuição da bola.
                        -Finalizações: Reflete o impacto ofensivo.
                        -Finalizações no Alvo: Mostra a precisão das tentativas de gol.
                        -Faltas Cometidas e Sofridas: Avalia o comportamento defensivo e ofensivo nas disputas físicas.
                        -Desarmes e Interceptações: Indicam a eficácia defensiva.
                        -Dribles Bem-Sucedidos e Tentados: Avaliam a habilidade de vencer defensores.
                        -Gols Marcados: O resultado direto do desempenho ofensivo.
                        -Cartões Amarelos e Vermelhos: Demonstram o comportamento disciplinar.
                    
                    As escalações das equipes são fornecidas aqui:
                    {dados1}
                    
                    Os detalhes do jogador1: 
                    {dados2}
                    
                    Os detalhes do jogador1: 
                    {dados3}
                    
                    Baseando-se nesses números, forneça uma análise detalhada que responda:
                        Qual jogador teve maior impacto no jogo ofensivamente e por quê?
                        Qual jogador foi mais eficaz defensivamente?
                        Quem teve melhor precisão em passes e contribuições gerais?
                        Quem demonstrou melhor habilidade em situações de um contra um (dribles)?
                        Quem teve melhor comportamento disciplinar?

                    Finalize com uma conclusão comparativa geral destacando o jogador com maior impacto no jogo."
                    """
                
                st.write(get_sport_specialist_comments_about_match(stats_jogador1,
                                                                       stats_jogador2,
                                                                       escalacao,
                                                                       agent_prompt))
