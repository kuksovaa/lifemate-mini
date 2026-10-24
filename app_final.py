# импорт необходимых библиотек
import os  
import logging                                      # модуль для записи логов 
from fastapi import FastAPI, HTTPException          # создание веб-приложения и возврата HTTP-ошибки
from pydantic import BaseModel, Field               # проверка входящих данных
from datetime import datetime, date                 # для фиксации даты записей дневника


# настройка логирования 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lifemate")              # объект для записи логов

# задаем название приложение
APP_NAME = os.getenv("APP_NAME", "LifeMate Mini")   

# создание приложения FastAPI
app = FastAPI(title=APP_NAME)                       # объект веб-приложения

# создание списка словарей для дневника
journal = []


# описание структуры записи дневника 
class JournalEntry(BaseModel):                      
    text: str = Field(min_length=1) 
    event_date: date | None = None              

# главная страница LifeMate
@app.get('/')
def home():
    return {'message': 'Welcome to LifeMate!'}

# проверка работоспособности приложения 
@app.get('/health')
def health():
    return {'status': 'ok'}

# версия приложения
@app.get('/version')
def version():
    return {'version': '0.1.0'}

# показывает содержимое дневника 
@app.get('/journal')
def get_journal():
    logger.info('Journal requested')
    return {'entries': journal}

# добавляет новую запись в дневник 
@app.post('/journal')
def add_journal(entry: JournalEntry):

    now = datetime.now().astimezone()

    event_date = entry.event_date

    if event_date is None and 'сегодня' in entry.text.lower():
        event_date = now.date()


    new_entry = {
        'id': len(journal) + 1, 
        'text': entry.text,
        'created_at': datetime.now().astimezone().isoformat(timespec='seconds'),
        'event_date': event_date.isoformat() if event_date else None
    }

    journal.append(new_entry)
    logger.info('Journal entry created: id=%s', new_entry['id'])

    return new_entry


# добавляем знакомых и близких
class PersonEntry(BaseModel):
    name: str = Field(min_length=1)
    last_meeting: date
    interests: list[str] = Field(default_factory=list)


people = {
    'marina': {
        'name': 'Марина',
        'last_meeting': '2026-09-26',
        'interests': ['путешествия', 'спорт', 'ручные поделки']
    }, 

    'elena': {
        'name': 'Лена',
        'last_meeting': '2026-09-27',
        'interests': ['йога', 'театр', 'фильмы']
    }

}

# получение информации о человеке
@app.get('/people/{name}')
def get_person_name(name:str):

    person = people.get(name.strip().lower())

    if person is None: 
        raise HTTPException(
            status_code=404, 
            detail = 'person not found'
        )
    logger.info('Person requested: %s', name)

    return person

@app.post('/people', status_code=201)
def add_person(person: PersonEntry):
    name = person.name.strip().lower()

    if not name: 
        raise HTTPException(
            status_code=422, 
            detail = 'Name cannot be empty'
        )

    if name in people: 
        raise HTTPException(
            status_code=409, 
            detail = 'Person already exists'
    )


    people[name] = {
        'name': person.name.strip(), 
        'last_meeting': person.last_meeting.isoformat(), 
        'interests': person.interests
    }

    logger.info('Person created')

    return people[name]