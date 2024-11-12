from fastapi import FastAPI, HTTPException
from models import *
from datetime import datetime, timedelta
import httpx, random, locale

app = FastAPI(title="Previsão de temperatura")
locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')  #Trazer os dias da semana em português

API_Key_WeatherSite = "00ce2ac84ab3031ff8efbcc500cb79f6"
descricao_aleatoria = "Céu limpo", "Poucas nuvens", "Nuvens dispersas", "Nuvens quebradas", "Chuva leve", "Chuva", "Tempestade", "Névoa", "Neblina", "Nebuloso", "Nuvens densas"
descricao_dict = {
    "clear sky": "Céu limpo",
    "few clouds": "Poucas nuvens",
    "scattered clouds": "Nuvens dispersas",
    "broken clouds": "Nuvens quebradas",
    "shower rain": "Chuva leve",
    "rain": "Chuva",
    "thunderstorm": "Tempestade",
    "snow": "Neve",
    "mist": "Névoa",
    "fog": "Neblina",
    "haze": "Nebuloso",
    "overcast clouds": "Nuvens densas",
}

async def pegar_temperatura_real(city: str):
    url = (
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_Key_WeatherSite}&units=metric"
    )
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            print("Dados totais: ", data)
            temperatura = data["main"]["temp"]
            descricao = data["weather"][0]["description"].lower()
            descricao = descricao_dict.get(descricao, descricao.capitalize())
            sensacao_termica = data["main"]["feels_like"]
            temperatura_minima = data["main"]["temp_min"]
            temperatura_maxima = data["main"]["temp_max"]
            humidade = data["main"]["humidity"]
            return temperatura, descricao, sensacao_termica, temperatura_minima, temperatura_maxima, humidade
        else:
            raise HTTPException(status_code=response.status_code, detail="Cidade não encontrada.")
        
def previsao_hipotetica_semana():
    list = []
    for i in range(6):
        list.append(previsaoDiaSemanal(
            data=(datetime.now() + timedelta(days=i+1)).strftime('%d-%m-%Y'),
            diaSemana=(datetime.now() + timedelta(days=i+1)).strftime('%A'),
            temperatura=22 + i,  
            descricao=random.choice(descricao_aleatoria),
            sensacao_termica=20 + i,
            temperatura_minima=18 + i,
            temperatura_maxima=25 + i,
            humidade=32 + i
        ))
        # future_date = (datetime.now() + timedelta(days=i))
        # dataFormatada = future_date.strftime('%d-%m-%Y')
        # diaSemana = future_date.strftime("%A")
        # temperatura = round(random.uniform(15, 30), 1)  
        # descricao = random.choice(["Ensolarado", "Nublado", "Chuva", "Parcialmente nublado"])
        # list.append(previsaoDia(data=dataFormatada, diaSemana=diaSemana, temperatura=temperatura, descricao=descricao))
    return list

@app.get("/previsao_temperatura/{city}", response_model=previsaoDiaReal)
async def previsao_temperatura_hoje(city: str):
    try:
        temperatura, descricao, sensacao_termica, temperatura_minima, temperatura_maxima, humidade = await pegar_temperatura_real(city)
        return previsaoDiaReal(
            cidade=city.capitalize(),
            temperatura=temperatura,
            descricao=descricao,
            sensacao_termica = sensacao_termica,
            temperatura_minima = temperatura_minima,
            temperatura_maxima = temperatura_maxima,
            humidade = humidade
        )
    except HTTPException as e:
        raise e

@app.get("/previsao_temperatura_semanal/{city}", response_model=previsaoSemana)
async def predict_week_temperature(city: str):
    try:
        # Obtemos a previsão real para o dia atual
        temperatura, descricao, sensacao_termica, temperatura_minima, temperatura_maxima, humidade = await pegar_temperatura_real(city)
        today = previsaoDiaSemanal(
            data=datetime.now().strftime('%d-%m-%Y'),
                diaSemana=datetime.now().strftime('%A'),
                    temperatura=temperatura,
                        descricao=descricao,
                        sensacao_termica=sensacao_termica,
                        temperatura_minima=temperatura_minima,
                        temperatura_maxima=temperatura_maxima,
                        humidade=humidade)
        
        # Geramos previsões hipotéticas para os próximos seis dias
        hypothetical_forecast = previsao_hipotetica_semana()
        
        # Retornamos a previsão completa para a semana
        return previsaoSemana(
            cidade=city.capitalize(),
            daily_forecast=[today] + hypothetical_forecast
        )
    except HTTPException as e:
        raise e
