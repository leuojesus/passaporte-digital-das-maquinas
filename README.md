# Passaporte Digital das Máquinas

MVP acadêmico da Tecnoação para gestão da documentação técnica das máquinas industriais.

Tecnologias: Python 3.12, Django 5.2 LTS, PostgreSQL 17, Bootstrap 5.3 e biblioteca qrcode.

Funcionalidades: acesso autenticado, cadastro de máquinas, upload de documentos privados, QR Codes, consulta de ficha técnica e histórico simplificado de manutenção.

## Executar localmente

1. Instale Python 3.12 e PostgreSQL, ou use DB_ENGINE=sqlite somente para desenvolvimento.
2. Crie um ambiente virtual: `python -m venv .venv`; ative-o.
3. Execute `pip install -r requirements.txt`.
4. Copie `.env.example` para `.env`; gere uma DJANGO_SECRET_KEY segura.
5. Execute `python manage.py migrate` e `python manage.py createsuperuser`.
6. Execute `python manage.py runserver` e acesse http://localhost:8000/ .
7. Para conceder permissões, use o Django Admin e seus grupos ou comandos de gerenciamento.

Não comite .env, segredos, banco local ou documentos industriais reais.
A aplicação está em desenvolvimento e precisa de testes funcionais e validação externa.