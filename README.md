# Descrição do projeto e objetivo.
O objetivo do projeto é disponibilizar uma ferramente com dados dos principais campeonatos de futebol, com dados da liga, temporada, partida e statisticas de cada jogador. 
Tambem uma integração com LLM para ser capaz não apenas de trazer os dados da partida mas também dizer o que aconteceu naquela partida, o comparativo entre os jogadores escolhido. 

# Instruções para configurar o ambiente e executar o código.
1. Execultar o download da aplicação no github https://github.com/diegopoliveira80/Data_driven_AT
2. Salvar a aplcação em um diretorio separado
3. Abrir pasta my_app em um notebook
4. Criar ambiente virtual para receber as instalações das bibliotecas necessarias
```python
python -m venv venv
```

5. Ativar o ambiente
```python
venv/scripts/activate
```

6. Instalar dependências requirements.txt
```python
pip install -r requirements.txt
```

7. Criar arquivo .env e inserir API_KEY GEMINI para funcionamento do LLM conforme estrutura mencionada acima
comando para ios ou windows
```python
export GOOGLE_API_KEY=<token>
$env:GEMINI_API_KEY_PRO<token>
```

8. Iniciar uvicorn app/main.py no terminal para criar o localhost
```python
uvicorn main:app --reload
```


9. Iniciar streamlit run app.py no terminal para visualizar o front-end
```python
streamlit run app.py
```

Após o passo a passo acima a aplicação estará funcionando em seu localhost

# Exemplos de entrada e saída das funcionalidades.
```

