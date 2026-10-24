from fastapi.testclient import TestClient                       # тестовые HTTP-запросы
from app_final import app                                       # импорт LifeMate app

client = TestClient(app)                                        # создание тестового клиента

# проверка health
def test_health():
    response = client.get('/health')

    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}

# проверка версии
def test_version():
    response = client.get('/version')

    assert response.status_code == 200
    assert response.json()['version'] == '0.1.0'

# проверка поиска человека
def test_person_found():
    response = client.get('/people/marina')

    assert response.status_code == 200
    assert response.json()['name'] == 'Марина'

# проверка несуществующего человека
def test_person_not_found():
    response = client.get('/people/unknown')

    assert response.status_code == 404

# проверка дневника
def test_journal():
    response = client.post(
        '/journal',
        json={
            'text': 'Тестовая запись LifeMate',
            'event_date': '2026-10-20'
        }
    )

    assert response.status_code == 200
    assert response.json()['event_date'] == '2026-10-20'

    journal_response = client.get('/journal')

    assert journal_response.status_code == 200
    assert response.json() in journal_response.json()['entries']

# проверка рекомендаций по интересам
def test_ideas():
    response = client.get('/ideas/музыка')

    assert response.status_code == 200
    assert response.json()['interest'] == 'музыка'
    assert len(response.json()['recommendations']) > 0

# проверка напоминаний о встречах
def test_reminders():
    response = client.get('/reminders', params={'days': 20})

    assert response.status_code == 200

    reminders = response.json()['reminders']
    names = [person['name'] for person in reminders]

    assert 'Марина' in names