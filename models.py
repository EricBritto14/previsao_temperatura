from pydantic import BaseModel
from typing import List, Optional

class previsaoDiaSemanal(BaseModel):
    data: str
    diaSemana: str
    temperatura: float
    descricao: str
    sensacao_termica: Optional[float]  
    temperatura_minima: Optional[float]  
    temperatura_maxima: Optional[float]  
    humidade: Optional[int] 

class previsaoDiaReal(BaseModel):
    cidade: str  
    temperatura: float  
    descricao: str  
    sensacao_termica: float
    temperatura_minima: float
    temperatura_maxima: float
    humidade: float

class previsaoSemana(BaseModel):
    cidade: str  
    daily_forecast: List[previsaoDiaSemanal] 