import os
from src.app import create_app
from src.seed import seed_db

app = create_app()

# Auto-seed on startup if database is empty or on first launch
try:
    with app.app_context():
        session = app.container.db.SessionLocal()
        user_count = session.query(app.container.user_repository().model_class).count()
        if user_count == 0:
            print('[WSGI] Database is empty. Running initial seeding...')
            seed_db()
            print('[WSGI] Database seeded successfully.')
        session.close()
except Exception as e:
    print(f'[WSGI] Seeding check notice: {e}')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
