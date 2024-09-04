from app import create_app, db

app = create_app()

# Push application context
with app.app_context():
    db.create_all()

print("Database tables created.")
