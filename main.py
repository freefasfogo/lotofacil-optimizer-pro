"""
Ponto de entrada principal do Lotofácil Optimizer PRO
"""
import sys
import os
from pathlib import Path

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
except ImportError:
    print("=" * 60)
    print("ERRO: PySide6 não instalado!")
    print("=" * 60)
    print("\nExecute o comando:")
    print("pip install PySide6 pandas numpy openpyxl reportlab matplotlib")
    print("\nOu execute install.bat para instalar todas as dependências.")
    input("\nPressione Enter para sair...")
    sys.exit(1)

from gui.main_window import MainWindow


def setup_application():
    """Configura a aplicação"""
    app = QApplication(sys.argv)
    app.setApplicationName("Lotofácil Optimizer PRO")
    app.setOrganizationName("LotofacilOptimizer")
    
    # Estilo
    app.setStyle('Fusion')
    
    # Paleta de cores
    from PySide6.QtGui import QColor, QPalette
    palette = app.palette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.WindowText, Qt.black)
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.Text, Qt.black)
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, Qt.black)
    palette.setColor(QPalette.Highlight, QColor(0, 102, 204))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(palette)
    
    return app


def main():
    """Função principal"""
    try:
        # Configuração
        app = setup_application()
        
        # Janela principal
        window = MainWindow()
        window.show()
        
        # Executa
        sys.exit(app.exec())
    except Exception as e:
        print(f"Erro ao iniciar aplicação: {e}")
        import traceback
        traceback.print_exc()
        input("\nPressione Enter para sair...")


if __name__ == "__main__":
    main()
