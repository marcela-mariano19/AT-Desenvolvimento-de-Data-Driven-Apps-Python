import streamlit as st

from fastapi import FastAPI
from statsbombpy import sb
import requests
import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.routes.routes import router

app = FastAPI()
app.include_router(router)


def main():

    st.title('Football Stats')
    st.write('Bem-vindo ao Football Stats! Aqui você pod encontrar informações sobre partidas, times e jogadores de futebol.')


    competition = st.sidebar.selectbox('Competição', sb.competitions().competition_name.unique())

    if competition:
        st.session_state['salve_competition'] = competition

    #Salvando o ID da competição para usar na API
    competition_id = sb.competitions().loc[sb.competitions().competition_name == competition]['competition_id'].values[0]

    with st.container():
        st.subheader(f'Dados da Competição {competition} na Base StatsBomb')
        df = sb.competitions().loc[sb.competitions().competition_name == competition]
        st.dataframe(df)

        
        season  = st.sidebar.radio('Selecione a temporada para análise', df['season_name'],horizontal=True)
        
        #Salvando sessão da temporada
        if season:
            st.session_state['salve_season'] = season

        st.subheader(f'Dados da Temporada {season} na Base StatsBomb')
        
        #Salvando o ID da temporada para usar na API
        season_id = df[df['season_name'] == season]['season_id'].values[0]

        #Carregando partidas da temporada
        df_macthes = sb.matches(competition_id=df['competition_id'].values[0],season_id=season_id)


        team = st.multiselect('Caso queira selecione os times mandantes que deseja visualizar', df_macthes['home_team'].unique())
        if team:
            df_macthes_selected = df_macthes[df_macthes['home_team'].isin(team)]
            st.dataframe(df_macthes_selected)
        else:
            st.dataframe(df_macthes)

        st.subheader('Estatísticas da Partida')

        match = st.selectbox('Selecione a partida para análise', sorted(df_macthes['home_team'] + ' x ' + df_macthes['away_team'])) 
        match_id = df_macthes.loc[df_macthes['home_team'] + ' x ' + df_macthes['away_team'] == match]['match_id'].values[0]

        #Carregando estatísticas da partida
        url_api_stats = "http://localhost:8000/match/stats"

        col1, col2 = st.columns(2)
        

        if st.button('Estatísticas'):
            response = requests.post(url_api_stats, json={"match_id": int(match_id),
                                                            "competition_id": int(competition_id),
                                                            "season_id": int(season_id)})
            stats = response.json()
            with col1:
                st.metric('Total de Passes', stats['passes'])
                st.metric('Total de Chutes', stats['shots'])
                st.metric('Total de Dribles', stats['dribbles'])
            with col2:
                st.metric('Total de Recuperações de Bola', stats['ball_recoveries'])
                st.metric('Total de Cartões Amarelos', stats['yellow_cards'])
                st.metric('Total de Cartões Vermelhos', stats['red_cards'])

        
        st.markdown('---') #Separador

        st.subheader('Perfil de Jogadores')
        match_seleted = df_macthes.loc[df_macthes['match_id'] == match_id]

        home_team = match_seleted['home_team'].values[0]
        away_team = match_seleted['away_team'].values[0]

        lineup_home_time = sb.lineups(match_id=match_id)[home_team]
        lineup_away_time = sb.lineups(match_id=match_id)[away_team]
        lineup_all = pd.concat([lineup_home_time,lineup_away_time])

        #seleção de jogador
        player = st.selectbox('Selecione o jogador para análise', lineup_all['player_name'],key='player')


        player_id = lineup_all.loc[lineup_all['player_name'] == player]['player_id'].values[0]
        player_data = lineup_all[lineup_all['player_id'] ==player_id].to_dict('records')[0]

        #st.dataframe(player_data)
        url_api_players = "http://localhost:8000/match/player_profile"


        if st.button('Estatísticas do Jogador'):
            response = requests.post(url_api_players, json={"player_id": int(player_id),
                                                            "match_id": int(match_id),
                                                            "player_data": player_data})
            stats_player = response.json()

            st.markdown('---')
            col3, col4, col5 = st.columns([2,1,1])
            with col3:
                st.metric('Nome', stats_player['player_name'])
                st.metric('País', stats_player['country'])
        
            with col4:
                st.metric('Total de Passes', stats_player['passes'])
                st.metric('Total de Chutes', stats_player['shots'])
                st.metric('Total de Dribles', stats_player['dribbles'])
            with col5:
                st.metric('Bolas Recuperadas', stats_player['ball_recoveries'])
                st.metric('Total de Cartões Amarelos', stats_player['yellow_cards'])
                st.metric('Total de Cartões Vermelhos', stats_player['red_cards'])


        st.markdown('---')





if __name__ == '__main__':
    main()