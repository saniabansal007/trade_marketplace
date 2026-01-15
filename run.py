from app import create_app, db, socketio

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database created!")
    # Use socketio.run instead of app.run
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)