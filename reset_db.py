"""
Script para resetar o banco de dados
"""
import os
import shutil

def reset_database():
    """Remove e recria o banco de dados"""
    db_path = "data/lotofacil.db"
    
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✅ Banco de dados removido: {db_path}")
    
    # Recria o diretório
    os.makedirs("data", exist_ok=True)
    
    # Recria o banco
    from database.database import Database
    db = Database()
    print("✅ Banco de dados recriado com sucesso!")
    
if __name__ == "__main__":
    reset_database()
