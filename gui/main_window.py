"""
Janela principal da aplicação - Com Aba Melhores Jogos e Correções
"""
import sys
import os
import json
import threading
from typing import Optional, List

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# Adiciona o diretório pai ao path para importações
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .widgets import (
    ProgressWidget, 
    GameDisplayWidget, 
    StatisticsWidget, 
    FrequencyChartWidget,
    BestGamesWidget
)
from core.game import Game, GameGenerator
from core.population import Population
from core.scorer import GameScorer
from core.statistics import StatisticsAnalyzer
from optimization.optimizer import OptimizationOrchestrator
from export.excel_export import ExcelExporter
from export.pdf_export import PDFExporter
from export.txt_export import TXTExporter
from database.database import Database


class MainWindow(QMainWindow):
    """Janela principal do Lotofácil Optimizer PRO"""
    
    # Definindo sinais personalizados
    optimization_finished_signal = Signal(float, float)  # best_score, duration
    optimization_error_signal = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.config = self._load_config()
        self.scorer = GameScorer(self.config)
        self.db = Database()
        self.current_games = []
        self.best_games = []
        self.optimization_running = False
        self.orchestrator = None
        self.optimization_thread = None
        self.best_games_result = []
        
        # Conecta os sinais
        self.optimization_finished_signal.connect(self._on_optimization_finished)
        self.optimization_error_signal.connect(self._on_optimization_error)
        
        self.init_ui()
        self._load_history()
        
    def _load_config(self) -> dict:
        """Carrega configurações"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                "jogos": 20,
                "dezenas": 15,
                "max_overlap": 8,
                "geracoes": 500,
                "populacao": 1000,
                "taxa_mutacao": 0.1,
                "taxa_crossover": 0.8,
                "temperatura_inicial": 1000,
                "temperatura_final": 1,
                "cooling_rate": 0.95,
                "tabu_tenure": 10,
                "mostrar_porcentagem": True,
                "pesos": {
                    "frequencia": 0.25,
                    "sobreposicao": 0.25,
                    "linhas": 0.15,
                    "colunas": 0.15,
                    "pares": 0.10,
                    "moldura": 0.05,
                    "consecutivo": 0.05
                },
                "validacoes": {
                    "min_pares": 6,
                    "max_pares": 9,
                    "min_impares": 6,
                    "max_impares": 9,
                    "min_soma": 100,
                    "max_soma": 200,
                    "max_consecutivos": 2
                }
            }
    
    def init_ui(self):
        """Inicializa a interface"""
        self.setWindowTitle("Lotofácil Optimizer PRO")
        self.setGeometry(100, 100, 1400, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Painel esquerdo - Controles
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Painel direito - Visualização
        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel, 2)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Pronto")
        
        # Menu
        self._create_menu()
        
    def _create_left_panel(self) -> QWidget:
        """Cria o painel esquerdo com controles"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Título
        title = QLabel("Lotofácil Optimizer PRO")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #0066CC;")
        layout.addWidget(title)
        
        # Seção: Gerar Jogos
        generate_group = QGroupBox("Gerar Jogos")
        gen_layout = QVBoxLayout(generate_group)
        
        # Quantidade
        qty_layout = QHBoxLayout()
        qty_layout.addWidget(QLabel("Quantidade:"))
        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 10000)
        self.qty_spin.setValue(self.config.get('jogos', 20))
        qty_layout.addWidget(self.qty_spin)
        gen_layout.addLayout(qty_layout)
        
        # Botão gerar
        self.generate_btn = QPushButton("Gerar Jogos")
        self.generate_btn.clicked.connect(self.generate_games)
        self.generate_btn.setStyleSheet("font-weight: bold; padding: 5px; background-color: #2196F3; color: white;")
        gen_layout.addWidget(self.generate_btn)
        
        layout.addWidget(generate_group)
        
        # Seção: Melhores Jogos
        best_group = QGroupBox("Melhores Jogos")
        best_layout = QVBoxLayout(best_group)
        
        # Quantos melhores
        best_qty_layout = QHBoxLayout()
        best_qty_layout.addWidget(QLabel("Quantidade:"))
        self.best_qty_spin = QSpinBox()
        self.best_qty_spin.setRange(1, 1000)
        self.best_qty_spin.setValue(10)
        best_qty_layout.addWidget(self.best_qty_spin)
        best_layout.addLayout(best_qty_layout)
        
        # Botão selecionar melhores
        self.best_btn = QPushButton("Selecionar Melhores")
        self.best_btn.clicked.connect(self.select_best_games)
        self.best_btn.setStyleSheet("font-weight: bold; padding: 5px; background-color: #9C27B0; color: white;")
        best_layout.addWidget(self.best_btn)
        
        layout.addWidget(best_group)
        
        # Seção: Otimização
        opt_group = QGroupBox("Otimização")
        opt_layout = QVBoxLayout(opt_group)
        
        # Algoritmo
        algo_layout = QHBoxLayout()
        algo_layout.addWidget(QLabel("Algoritmo:"))
        self.algo_combo = QComboBox()
        self.algo_combo.addItems([
            "Hill Climbing",
            "Simulated Annealing",
            "Genetic Algorithm",
            "Tabu Search"
        ])
        algo_layout.addWidget(self.algo_combo)
        opt_layout.addLayout(algo_layout)
        
        # Parâmetros
        params_layout = QGridLayout()
        
        params_layout.addWidget(QLabel("Gerações:"), 0, 0)
        self.generations_spin = QSpinBox()
        self.generations_spin.setRange(1, 10000)
        self.generations_spin.setValue(self.config.get('geracoes', 500))
        params_layout.addWidget(self.generations_spin, 0, 1)
        
        params_layout.addWidget(QLabel("População:"), 1, 0)
        self.population_spin = QSpinBox()
        self.population_spin.setRange(1, 10000)
        self.population_spin.setValue(self.config.get('populacao', 1000))
        params_layout.addWidget(self.population_spin, 1, 1)
        
        opt_layout.addLayout(params_layout)
        
        # Botões otimização
        opt_btn_layout = QHBoxLayout()
        self.optimize_btn = QPushButton("Otimizar")
        self.optimize_btn.clicked.connect(self.optimize_games)
        self.optimize_btn.setStyleSheet("font-weight: bold; padding: 5px; background-color: #4CAF50; color: white;")
        opt_btn_layout.addWidget(self.optimize_btn)
        
        self.stop_btn = QPushButton("Parar")
        self.stop_btn.clicked.connect(self.stop_optimization)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("font-weight: bold; padding: 5px; background-color: #f44336; color: white;")
        opt_btn_layout.addWidget(self.stop_btn)
        
        opt_layout.addLayout(opt_btn_layout)
        
        layout.addWidget(opt_group)
        
        # Seção: Exportação
        export_group = QGroupBox("Exportar")
        export_layout = QVBoxLayout(export_group)
        
        export_btn_layout = QGridLayout()
        
        self.export_txt_btn = QPushButton("Exportar TXT")
        self.export_txt_btn.clicked.connect(self.export_txt)
        self.export_txt_btn.setStyleSheet("background-color: #FF9800; color: white;")
        export_btn_layout.addWidget(self.export_txt_btn, 0, 0)
        
        self.export_excel_btn = QPushButton("Exportar Excel")
        self.export_excel_btn.clicked.connect(self.export_excel)
        self.export_excel_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        export_btn_layout.addWidget(self.export_excel_btn, 0, 1)
        
        self.export_pdf_btn = QPushButton("Exportar PDF")
        self.export_pdf_btn.clicked.connect(self.export_pdf)
        self.export_pdf_btn.setStyleSheet("background-color: #f44336; color: white;")
        export_btn_layout.addWidget(self.export_pdf_btn, 1, 0, 1, 2)
        
        export_layout.addLayout(export_btn_layout)
        layout.addWidget(export_group)
        
        # Progresso
        self.progress_widget = ProgressWidget()
        layout.addWidget(self.progress_widget)
        
        layout.addStretch()
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Cria o painel direito com visualizações"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Tab: Jogos
        self.game_widget = GameDisplayWidget()
        self.tabs.addTab(self.game_widget, "Jogos")
        
        # Tab: Melhores Jogos
        self.best_widget = BestGamesWidget()
        self.tabs.addTab(self.best_widget, "⭐ Melhores Jogos")
        
        # Tab: Estatísticas
        self.stats_widget = StatisticsWidget()
        self.tabs.addTab(self.stats_widget, "Estatísticas")
        
        # Tab: Frequência
        self.freq_widget = FrequencyChartWidget()
        self.tabs.addTab(self.freq_widget, "Frequência")
        
        # Tab: Histórico
        self.history_widget = self._create_history_tab()
        self.tabs.addTab(self.history_widget, "Histórico")
        
        layout.addWidget(self.tabs)
        
        return panel
    
    def _create_history_tab(self) -> QWidget:
        """Cria a tab de histórico"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self._show_history_details)
        layout.addWidget(self.history_list)
        
        self.history_details = QTextEdit()
        self.history_details.setReadOnly(True)
        self.history_details.setMaximumHeight(150)
        layout.addWidget(self.history_details)
        
        reload_btn = QPushButton("Recarregar Histórico")
        reload_btn.clicked.connect(self._load_history)
        layout.addWidget(reload_btn)
        
        return widget
    
    def _create_menu(self):
        """Cria o menu da aplicação"""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("Arquivo")
        
        import_action = QAction("Importar Jogos", self)
        import_action.triggered.connect(self.import_games)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        tools_menu = menubar.addMenu("Ferramentas")
        
        clear_action = QAction("Limpar Todos os Dados", self)
        clear_action.triggered.connect(self.clear_all_data)
        tools_menu.addAction(clear_action)
        
        compare_action = QAction("Comparar Algoritmos", self)
        compare_action.triggered.connect(self.compare_algorithms)
        tools_menu.addAction(compare_action)
        
        help_menu = menubar.addMenu("Ajuda")
        
        about_action = QAction("Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    @Slot()
    def generate_games(self):
        """Gera jogos"""
        try:
            count = self.qty_spin.value()
            self.status_bar.showMessage(f"Gerando {count} jogos...")
            self.progress_widget.set_status(f"Gerando {count} jogos...")
            
            games = GameGenerator.generate_many(count)
            
            for game in games:
                game.score = self.scorer.score_individual(game)
            
            self.current_games = games
            
            self.game_widget.set_games(games)
            self._update_statistics()
            self._update_frequency()
            
            self.status_bar.showMessage(f"✅ {len(games)} jogos gerados com sucesso!")
            self.progress_widget.set_status("Pronto")
            self.progress_widget.set_progress(1.0)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar jogos: {str(e)}")
            self.status_bar.showMessage("❌ Erro ao gerar jogos")
            self.progress_widget.set_status("Erro")
    
    @Slot()
    def select_best_games(self):
        """Seleciona os melhores jogos"""
        if not self.current_games:
            QMessageBox.warning(self, "Aviso", "Gere jogos primeiro!")
            return
        
        try:
            count = self.best_qty_spin.value()
            
            # Ordena jogos por score (do maior para o menor)
            sorted_games = sorted(self.current_games, key=lambda g: g.score, reverse=True)
            
            # Pega os melhores
            self.best_games = sorted_games[:count]
            
            # Atualiza a aba de melhores jogos
            self.best_widget.set_games(self.best_games)
            
            # Mostra mensagem
            best_score = self.best_games[0].score * 100 if self.best_games else 0
            self.status_bar.showMessage(
                f"✅ {len(self.best_games)} melhores jogos selecionados! "
                f"Melhor score: {best_score:.1f}%"
            )
            
            # Muda para a aba de melhores jogos
            self.tabs.setCurrentIndex(1)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao selecionar melhores: {str(e)}")
    
    @Slot()
    def optimize_games(self):
        """Executa otimização"""
        if self.optimization_running:
            return
            
        if not self.current_games:
            self.generate_games()
            if not self.current_games:
                return
        
        algorithm_map = {
            "Hill Climbing": "hill_climbing",
            "Simulated Annealing": "simulated_annealing",
            "Genetic Algorithm": "genetic",
            "Tabu Search": "tabu_search"
        }
        
        algo_name = algorithm_map[self.algo_combo.currentText()]
        
        self.config['geracoes'] = self.generations_spin.value()
        self.config['populacao'] = self.population_spin.value()
        self.config['algoritmo'] = algo_name
        
        self.orchestrator = OptimizationOrchestrator(self.config)
        population = Population(self.current_games, self.scorer)
        
        self.optimize_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.optimization_running = True
        
        self.progress_widget.set_status(f"Otimizando com {algo_name}...")
        self.progress_widget.start_timer()
        self.progress_widget.set_progress(0.0)
        
        self.optimization_thread = threading.Thread(
            target=self._run_optimization,
            args=(algo_name, population)
        )
        self.optimization_thread.daemon = True
        self.optimization_thread.start()
    
    def _run_optimization(self, algo_name: str, population: Population):
        """Executa otimização em thread separada"""
        try:
            result = self.orchestrator.optimize(
                algo_name,
                population,
                parallel=False
            )
            
            if result and len(result) > 0:
                self.best_games_result = result[0].best_games
                best_score = result[0].best_score
                duration = result[0].duration
                
                self.optimization_finished_signal.emit(best_score, duration)
            else:
                self.optimization_error_signal.emit("Resultado vazio")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.optimization_error_signal.emit(str(e))
    
    @Slot(float, float)
    def _on_optimization_finished(self, best_score: float, duration: float):
        """Finaliza otimização - chamado pelo sinal"""
        try:
            if self.best_games_result:
                # Atualiza jogos
                self.current_games = self.best_games_result
                self.game_widget.set_games(self.best_games_result)
                self._update_statistics()
                self._update_frequency()
                
                # Mensagem
                score_percent = best_score * 100
                self.status_bar.showMessage(
                    f"✅ Otimização concluída! Score: {score_percent:.1f}% "
                    f"em {duration:.1f}s"
                )
                
                # Para o timer
                self.progress_widget.stop_timer()
                self.progress_widget.set_status(f"Concluído - Score: {score_percent:.1f}%")
                self.progress_widget.set_progress(1.0)
                
        except Exception as e:
            print(f"Erro ao finalizar otimização: {e}")
            
        # Restaura UI
        self.optimize_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.optimization_running = False
    
    @Slot(str)
    def _on_optimization_error(self, error_msg: str):
        """Erro na otimização - chamado pelo sinal"""
        QMessageBox.critical(self, "Erro", f"Erro na otimização: {error_msg}")
        
        self.optimize_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.optimization_running = False
        self.progress_widget.stop_timer()
        self.progress_widget.set_status("Erro")
        self.status_bar.showMessage("❌ Erro na otimização")
    
    @Slot()
    def stop_optimization(self):
        """Para a otimização"""
        self.optimization_running = False
        self.status_bar.showMessage("⏹️ Otimização interrompida pelo usuário")
        self.progress_widget.set_status("Interrompido")
        self.optimize_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_widget.stop_timer()
    
    def _update_statistics(self):
        """Atualiza estatísticas"""
        if not self.current_games:
            return
            
        try:
            from core.statistics import StatisticsAnalyzer
            from core.population import Population
            
            analyzer = StatisticsAnalyzer()
            stats = analyzer.analyze_population(Population(self.current_games))
            
            scores = [g.score for g in self.current_games]
            sums = [g.soma for g in self.current_games]
            pairs = [g.pares for g in self.current_games]
            
            avg_score = (sum(scores) / len(scores) * 100) if scores else 0.0
            max_score = (max(scores) * 100) if scores else 0.0
            min_score = (min(scores) * 100) if scores else 0.0
            
            diversity = (1.0 - (stats.frequency_std / 15) if stats.frequency_std else 0) * 100
            avg_sum = sum(sums) / len(sums) if sums else 0.0
            avg_pairs = sum(pairs) / len(pairs) if pairs else 0.0
            avg_odd = 15.0 - avg_pairs
            
            stats_dict = {
                'total_games': str(len(self.current_games)),
                'avg_score': f"{avg_score:.1f}%",
                'max_score': f"{max_score:.1f}%",
                'min_score': f"{min_score:.1f}%",
                'diversity': f"{diversity:.1f}%",
                'avg_sum': f"{avg_sum:.1f}",
                'avg_pairs': f"{avg_pairs:.1f}",
                'avg_odd': f"{avg_odd:.1f}"
            }
            
            self.stats_widget.update_stats(stats_dict)
        except Exception as e:
            print(f"Erro ao atualizar estatísticas: {e}")
    
    def _update_frequency(self):
        """Atualiza gráfico de frequência"""
        if not self.current_games:
            return
            
        try:
            from core.statistics import StatisticsAnalyzer
            from core.population import Population
            
            analyzer = StatisticsAnalyzer()
            stats = analyzer.analyze_population(Population(self.current_games))
            self.freq_widget.update_frequencies(stats.number_frequencies)
        except Exception as e:
            print(f"Erro ao atualizar frequência: {e}")
    
    @Slot()
    def export_txt(self):
        """Exporta para TXT"""
        games_to_export = self.best_games if self.best_games else self.current_games
        
        if not games_to_export:
            QMessageBox.warning(self, "Aviso", "Nenhum jogo para exportar")
            return
            
        os.makedirs("output", exist_ok=True)
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar como TXT",
            "output/jogos.txt",
            "Arquivos TXT (*.txt)"
        )
        
        if filename:
            try:
                from export.txt_export import TXTExporter
                exporter = TXTExporter()
                exporter.export(games_to_export, filename)
                QMessageBox.information(self, "Sucesso", f"Exportado para {filename}")
                self.status_bar.showMessage(f"✅ Exportado para {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar: {str(e)}")
    
    @Slot()
    def export_excel(self):
        """Exporta para Excel"""
        games_to_export = self.best_games if self.best_games else self.current_games
        
        if not games_to_export:
            QMessageBox.warning(self, "Aviso", "Nenhum jogo para exportar")
            return
            
        os.makedirs("output", exist_ok=True)
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar como Excel",
            "output/jogos.xlsx",
            "Arquivos Excel (*.xlsx)"
        )
        
        if filename:
            try:
                from export.excel_export import ExcelExporter
                exporter = ExcelExporter()
                exporter.export(games_to_export, filename, self.config)
                QMessageBox.information(self, "Sucesso", f"Exportado para {filename}")
                self.status_bar.showMessage(f"✅ Exportado para {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar: {str(e)}")
    
    @Slot()
    def export_pdf(self):
        """Exporta para PDF"""
        games_to_export = self.best_games if self.best_games else self.current_games
        
        if not games_to_export:
            QMessageBox.warning(self, "Aviso", "Nenhum jogo para exportar")
            return
            
        os.makedirs("output", exist_ok=True)
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar como PDF",
            "output/relatorio.pdf",
            "Arquivos PDF (*.pdf)"
        )
        
        if filename:
            try:
                from export.pdf_export import PDFExporter
                exporter = PDFExporter()
                exporter.export(games_to_export, filename, self.config)
                QMessageBox.information(self, "Sucesso", f"Exportado para {filename}")
                self.status_bar.showMessage(f"✅ Exportado para {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar: {str(e)}")
    
    @Slot()
    def import_games(self):
        """Importa jogos de arquivo"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Importar Jogos",
            "",
            "Arquivos de Texto (*.txt);;Arquivos Excel (*.xlsx)"
        )
        
        if not filename:
            return
            
        try:
            if filename.endswith('.txt'):
                games = []
                with open(filename, 'r', encoding='utf-8') as f:
                    for line in f:
                        if 'Jogo' in line and ':' in line:
                            parts = line.split(':')
                            if len(parts) > 1:
                                numbers_str = parts[1].strip().split()
                                numbers = [int(n) for n in numbers_str if n.isdigit()]
                                if len(numbers) == 15:
                                    game = Game(numbers)
                                    game.score = self.scorer.score_individual(game)
                                    games.append(game)
                
                if games:
                    self.current_games = games
                    self.game_widget.set_games(games)
                    self._update_statistics()
                    self._update_frequency()
                    self.status_bar.showMessage(f"✅ {len(games)} jogos importados com sucesso!")
                    QMessageBox.information(self, "Sucesso", f"Importados {len(games)} jogos!")
                else:
                    QMessageBox.warning(self, "Aviso", "Nenhum jogo válido encontrado no arquivo")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao importar: {str(e)}")
    
    @Slot()
    def clear_all_data(self):
        """Limpa todos os dados"""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "Tem certeza que deseja limpar todos os dados do banco?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.clear_all()
                self.current_games = []
                self.best_games = []
                self.game_widget.set_games([])
                self.best_widget.set_games([])
                self._update_statistics()
                self._update_frequency()
                self.status_bar.showMessage("✅ Todos os dados foram limpos")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao limpar dados: {str(e)}")
    
    @Slot()
    def compare_algorithms(self):
        """Compara algoritmos"""
        if not self.current_games:
            QMessageBox.warning(self, "Aviso", "Gere jogos primeiro!")
            return
            
        try:
            self.status_bar.showMessage("Comparando algoritmos...")
            
            algorithms = ["hill_climbing", "simulated_annealing", "genetic", "tabu_search"]
            results = {}
            
            for algo in algorithms:
                config = self.config.copy()
                config['geracoes'] = 50
                config['populacao'] = 50
                
                orchestrator = OptimizationOrchestrator(config)
                population = Population(self.current_games[:10], self.scorer)
                result = orchestrator.optimize(algo, population, parallel=False)
                
                if result and len(result) > 0:
                    results[algo] = {
                        'score': result[0].best_score * 100,
                        'time': result[0].duration,
                        'iterations': result[0].iterations
                    }
            
            msg = "🏆 Comparação de Algoritmos:\n\n"
            for algo, data in results.items():
                msg += f"🔹 {algo}:\n"
                msg += f"   Score: {data['score']:.1f}%\n"
                msg += f"   Tempo: {data['time']:.2f}s\n"
                msg += f"   Iterações: {data['iterations']}\n\n"
            
            QMessageBox.information(self, "Comparação", msg)
            self.status_bar.showMessage("✅ Comparação concluída")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na comparação: {str(e)}")
    
    @Slot()
    def show_about(self):
        """Mostra sobre"""
        QMessageBox.about(
            self,
            "Sobre",
            "Lotofácil Optimizer PRO\n\n"
            "Versão: 1.0.0\n\n"
            "Sistema de otimização de jogos da Lotofácil\n"
            "usando algoritmos matemáticos e inteligência computacional.\n\n"
            "⚠️ Este sistema NÃO prevê resultados ou aumenta\n"
            "a probabilidade matemática de acerto.\n\n"
            "Desenvolvido com Python 3.12+ e PySide6"
        )
    
    def _load_history(self):
        """Carrega histórico do banco"""
        try:
            runs = self.db.get_optimization_history(20)
            self.history_list.clear()
            
            for run in runs:
                score_percent = run.best_score * 100
                item_text = f"{run.algorithm} - Score: {score_percent:.1f}% - {run.created_at.strftime('%d/%m/%Y %H:%M')}"
                self.history_list.addItem(item_text)
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")
    
    def _show_history_details(self, item):
        """Mostra detalhes do histórico"""
        try:
            index = self.history_list.row(item)
            runs = self.db.get_optimization_history(20)
            
            if index < len(runs):
                run = runs[index]
                score_percent = run.best_score * 100
                details = f"""
                📊 Detalhes da Execução
                {'='*40}
                
                Algoritmo: {run.algorithm}
                Gerações: {run.generation}
                População: {run.population_size}
                Melhor Score: {score_percent:.1f}%
                Duração: {run.duration:.2f}s
                Data: {run.created_at.strftime('%d/%m/%Y %H:%M:%S')}
                
                Configurações:
                {run.config}
                """
                self.history_details.setText(details)
        except Exception as e:
            print(f"Erro ao mostrar detalhes: {e}")
