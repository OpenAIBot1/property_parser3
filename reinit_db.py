from src.database.engine import init_db

if __name__ == '__main__':
    print("Reinitializing database...")
    init_db(drop_all=True)
    print("Database reinitialized successfully")
