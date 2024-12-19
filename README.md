# Assessment - Marcela Mariano 

## Descrição do Projeto
O football Stats foi criado com o intuito de gerar informação para amantes do futebol. Ele é alimentado pela biblioteca statsbombpy. 

## Como iniciar o projeto?
- Crie um pyenv para instalar as dependências que constam no arquivo requirements.txt;
- Crie na pasta raiz um arquivo chamado keys.env e configure as chaves da LLM lá;
- Abra um terminal e vá até a pasta raiz do projeto;
- Execute o comando uvicorn "app.main:app --reload" sem aspas. Ele serve para iniciar a API. 
- Abra um segundo terminal e vá até a pasta raiz do projeto; 
- Execute o comando 'streamlit run "./app/main.py"' sem as aspas simples para iniciar o front-end. 



## Exemplo de Entrada e Saída da API /match_summary

- Entrada:
http POST localhost:8000/match/analyze match_id=7556 competition_id=43 season_id=3

- Saída:
tition_id=43 season_id=3
content-length: 304         
content-type: application/json
date: Tue, 17 Dec 2024 01:08:56 GMT
server: uvicorn

"Japão e Senegal empataram em 2 a 2 em um jogo eletrizante que contou com 868 passes e 
apenas um cartão amarelo.  Os gols japoneses foram marcados por Takashi Inui e Keisuke 
Honda, com assistências de Yuto Nagatomo e o próprio Inui.  Pelo Senegal, Sadio Mané e apenas um cartão amarelo.  Os gols 
Moussa Wagué balançaram as redes.\n" 

# Exemplo de Entrada e Saída API /match/player_profile

- Entrada: 

- Saída: