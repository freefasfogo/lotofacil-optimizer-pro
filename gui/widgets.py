"""
Widgets personalizados para a interface gráfica
"""
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from typing import Optional, List, Callable
import sys


class ProgressWidget(QWidget):
    """Widget personalizado para exibir progresso"""
    
    progress_updated = Signal(float)
    status_updated = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # Label de status
        self.status_label = QLabel("Aguardando...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Label de tempo
        self.time_label = QLabel("Tempo: 0.0s")
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)
        
        # Timer para atualização
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_time)
        self.start_time = None
        self.elapsed = 0.0
        
    def set_progress(self, value: float):
        """Atualiza o progresso (0 a 1)"""
        percent = int(value * 100)
        self.progress_bar.setValue(percent)
        self.progress_updated.emit(value)
        
    def set_status(self, status: str):
        """Atualiza o status"""
        self.status_label.setText(status)
        self.status_updated.emit(status)
        
    def start_timer(self):
        """Inicia o cronômetro"""
        self.start_time = QTime.currentTime()
        self.timer.start(100)  # Atualiza a cada 100ms
        
    def stop_timer(self):
        """Para o cronômetro"""
        self.timer.stop()
        self.start_time = None
        
    def reset_timer(self):
        """Reseta o cronômetro"""
        self.stop_timer()
        self.time_label.setText("Tempo: 0.0s")
        self.elapsed = 0.0
        
    def _update_time(self):
        """Atualiza o tempo decorrido"""
        if self.start_time:
            elapsed = self.start_time.msecsTo(QTime.currentTime()) / 1000.0
            self.time_label.setText(f"Tempo: {elapsed:.1f}s")
            self.elapsed = elapsed


class GameDisplayWidget(QWidget):
    """Widget para exibir jogos da Lotofácil"""
    
    game_selected = Signal(int)  # Emite o índice do jogo selecionado
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.games = []
        self.selected_index = -1
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("📋 Jogos Gerados")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        
        # Lista de jogos
        self.game_list = QListWidget()
        self.game_list.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.game_list)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        
        self.copy_btn = QPushButton("📋 Copiar")
        self.copy_btn.clicked.connect(self._copy_selected)
        btn_layout.addWidget(self.copy_btn)
        
        self.remove_btn = QPushButton("❌ Remover")
        self.remove_btn.clicked.connect(self._remove_selected)
        btn_layout.addWidget(self.remove_btn)
        
        self.clear_btn = QPushButton("🗑️ Limpar Tudo")
        self.clear_btn.clicked.connect(self._clear_all)
        btn_layout.addWidget(self.clear_btn)
        
        layout.addLayout(btn_layout)
        
    def set_games(self, games: List, highlight_best: bool = True):
        """Atualiza a lista de jogos"""
        self.games = games
        self.game_list.clear()
        
        if not games:
            return
            
        # Encontra o melhor score para destacar
        best_score = max([g.score for g in games]) if games else 0
        
        for i, game in enumerate(games):
            # Formata o jogo
            numbers_str = " ".join(f"{n:02d}" for n in game.numbers)
            score_percent = game.score * 100
            score_str = f"Score: {score_percent:.1f}%"
            
            item_text = f"Jogo {i+1}: {numbers_str}  |  {score_str}"
            item = QListWidgetItem(item_text)
            
            # Colore baseado no score (em porcentagem)
            if highlight_best and hasattr(game, 'score'):
                if game.score >= 0.80:  # 80%+
                    item.setBackground(QColor(144, 238, 144))  # Verde claro
                    item.setForeground(QColor(0, 100, 0))
                elif game.score >= 0.70:  # 70-79%
                    item.setBackground(QColor(255, 255, 200))  # Amarelo claro
                    item.setForeground(QColor(100, 100, 0))
                elif game.score >= 0.60:  # 60-69%
                    item.setBackground(QColor(255, 200, 200))  # Rosa claro
                    item.setForeground(QColor(100, 0, 0))
                else:  # < 60%
                    item.setBackground(QColor(255, 150, 150))  # Vermelho claro
                    item.setForeground(QColor(139, 0, 0))
                
                # Destaque o melhor jogo
                if game.score == best_score and best_score > 0:
                    item.setBackground(QColor(0, 200, 0))  # Verde forte
                    item.setForeground(QColor(255, 255, 255))
            
            self.game_list.addItem(item)
            
    def _on_item_clicked(self, item):
        """Handler para clique em item"""
        index = self.game_list.row(item)
        self.selected_index = index
        self.game_selected.emit(index)
        
    def _copy_selected(self):
        """Copia o jogo selecionado para o clipboard"""
        if self.selected_index >= 0 and self.selected_index < len(self.games):
            game = self.games[self.selected_index]
            text = " ".join(f"{n:02d}" for n in game.numbers)
            QApplication.clipboard().setText(text)
            
            QMessageBox.information(self, "Sucesso", "✅ Jogo copiado para a área de transferência!")
            
    def _remove_selected(self):
        """Remove o jogo selecionado"""
        if self.selected_index >= 0 and self.selected_index < len(self.games):
            self.games.pop(self.selected_index)
            self.set_games(self.games)
            self.selected_index = -1
            
    def _clear_all(self):
        """Limpa todos os jogos"""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "Tem certeza que deseja limpar todos os jogos?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.games.clear()
            self.set_games(self.games)
            self.selected_index = -1


class StatisticsWidget(QWidget):
    """Widget para exibir estatísticas"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("📊 Estatísticas")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        
        # Grid de estatísticas
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(10)
        
        # Labels de estatísticas
        self.stats_labels = {}
        stats = [
            ("Total de Jogos:", "0"),
            ("Score Médio:", "0%"),
            ("Melhor Score:", "0%"),
            ("Pior Score:", "0%"),
            ("Diversidade:", "0%"),
            ("Soma Média:", "0"),
            ("Média de Pares:", "0"),
            ("Média de Ímpares:", "0")
        ]
        
        for i, (label, value) in enumerate(stats):
            row = i // 2
            col = (i % 2) * 2
            
            label_widget = QLabel(label)
            label_widget.setStyleSheet("font-weight: bold; color: #333;")
            self.stats_grid.addWidget(label_widget, row, col)
            
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #0066CC; font-weight: bold; font-size: 12px;")
            self.stats_grid.addWidget(value_widget, row, col + 1)
            
            self.stats_labels[label] = value_widget
        
        layout.addLayout(self.stats_grid)
        
        # Botão para atualizar
        self.refresh_btn = QPushButton("🔄 Atualizar Estatísticas")
        self.refresh_btn.clicked.connect(self.refresh)
        layout.addWidget(self.refresh_btn)
        
        layout.addStretch()
        
    def update_stats(self, stats: dict):
        """Atualiza as estatísticas exibidas"""
        if not stats:
            return
            
        mapping = {
            "Total de Jogos:": str(stats.get('total_games', 0)),
            "Score Médio:": stats.get('avg_score', "0%"),
            "Melhor Score:": stats.get('max_score', "0%"),
            "Pior Score:": stats.get('min_score', "0%"),
            "Diversidade:": stats.get('diversity', "0%"),
            "Soma Média:": stats.get('avg_sum', "0"),
            "Média de Pares:": stats.get('avg_pairs', "0"),
            "Média de Ímpares:": stats.get('avg_odd', "0")
        }
        
        for label, widget in self.stats_labels.items():
            if label in mapping:
                widget.setText(mapping[label])
                
    def refresh(self):
        """Força a atualização das estatísticas"""
        # Emite sinal para atualizar
        pass


class FrequencyChartWidget(QWidget):
    """Widget para exibir gráfico de frequência"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.frequencies = [0] * 25
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("📊 Frequência das Dezenas")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        
        # Canvas para desenho
        self.canvas = QLabel()
        self.canvas.setMinimumHeight(280)
        self.canvas.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 5px;")
        self.canvas.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.canvas)
        
        # Informações
        self.info_label = QLabel("Nenhum dado disponível")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.info_label)
        
    def update_frequencies(self, frequencies: List[int]):
        """Atualiza o gráfico de frequência"""
        self.frequencies = frequencies[:25]
        self._draw_chart()
        
    def _draw_chart(self):
        """Desenha o gráfico de barras"""
        if not any(self.frequencies):
            self.canvas.setText("📭 Sem dados para exibir")
            self.info_label.setText("Nenhum jogo gerado")
            return
            
        # Cria imagem
        width = 650
        height = 300
        image = QImage(width, height, QImage.Format_RGB32)
        image.fill(Qt.white)
        
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Margens
        margin_left = 50
        margin_right = 20
        margin_top = 40
        margin_bottom = 40
        chart_width = width - margin_left - margin_right
        chart_height = height - margin_top - margin_bottom
        
        # Calcula escalas
        max_freq = max(self.frequencies) if any(self.frequencies) else 1
        bar_width = chart_width / 25
        max_bar_height = chart_height * 0.9
        
        # Desenha título e informações
        painter.setPen(QColor(0, 102, 204))
        font = painter.font()
        font.setBold(True)
        font.setPointSize(10)
        painter.setFont(font)
        
        total = sum(self.frequencies)
        avg = total / 25 if total > 0 else 0
        
        title_text = f"Total: {total}  |  Média: {avg:.1f}  |  Máx: {max_freq}"
        painter.drawText(10, 25, title_text)
        
        # Desenha eixos
        painter.setPen(QColor(100, 100, 100))
        painter.drawLine(margin_left, height - margin_bottom, width - margin_right, height - margin_bottom)  # Eixo X
        painter.drawLine(margin_left, margin_top, margin_left, height - margin_bottom)  # Eixo Y
        
        # Desenha grade horizontal
        painter.setPen(QColor(220, 220, 220))
        for i in range(5):
            y = height - margin_bottom - (i / 5) * chart_height
            painter.drawLine(margin_left, y, width - margin_right, y)
        
        # Desenha barras
        for i, freq in enumerate(self.frequencies):
            x = margin_left + i * bar_width + 2
            bar_height = (freq / max_freq) * max_bar_height
            y = height - margin_bottom - bar_height
            
            # Cor da barra baseada na frequência
            if freq > 0:
                if freq >= max_freq * 0.8:
                    color = QColor(255, 0, 0)  # Vermelho - alta frequência
                elif freq >= max_freq * 0.5:
                    color = QColor(255, 165, 0)  # Laranja - média alta
                elif freq >= max_freq * 0.3:
                    color = QColor(255, 215, 0)  # Amarelo - média
                else:
                    color = QColor(0, 102, 204)  # Azul - baixa frequência
            else:
                color = QColor(200, 200, 200)  # Cinza - zero
                
            painter.fillRect(
                int(x), 
                int(y), 
                int(bar_width - 4), 
                int(bar_height),
                color
            )
            
            # Desenha borda da barra
            painter.setPen(QColor(150, 150, 150))
            painter.drawRect(
                int(x), 
                int(y), 
                int(bar_width - 4), 
                int(bar_height)
            )
            
            # Desenha número da dezena
            painter.setPen(QColor(50, 50, 50))
            painter.setFont(QFont("Arial", 7))
            text = str(i + 1)
            text_rect = QRectF(
                int(x), 
                height - margin_bottom + 2, 
                int(bar_width - 4), 
                15
            )
            painter.drawText(text_rect, Qt.AlignCenter, text)
            
            # Desenha valor da frequência
            if freq > 0:
                painter.setPen(QColor(0, 0, 0))
                painter.setFont(QFont("Arial", 6))
                freq_text = str(freq)
                painter.drawText(
                    int(x + (bar_width - 4) / 2 - 5),
                    int(y - 5),
                    freq_text
                )
        
        painter.end()
        
        # Atualiza o label
        pixmap = QPixmap.fromImage(image)
        self.canvas.setPixmap(pixmap.scaled(
            self.canvas.width(), 
            self.canvas.height(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        ))
        
        # Atualiza info
        total = sum(self.frequencies)
        avg = total / 25 if total > 0 else 0
        
        if any(self.frequencies):
            max_num = self.frequencies.index(max(self.frequencies)) + 1
            min_freq = min([f for f in self.frequencies if f > 0])
            min_num = self.frequencies.index(min_freq) + 1
            
            self.info_label.setText(
                f"📌 Dezena mais frequente: {max_num} ({max(self.frequencies)}x)  |  "
                f"Dezena menos frequente: {min_num} ({min_freq}x)"
            )
        else:
            self.info_label.setText("Nenhum dado disponível")


class BestGamesWidget(QWidget):
    """Widget para exibir os melhores jogos"""
    
    game_selected = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.games = []
        self.selected_index = -1
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título com ícone
        title = QLabel("⭐ Melhores Jogos")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #9C27B0;")
        layout.addWidget(title)
        
        # Informação de quantidade
        self.info_label = QLabel("Nenhum jogo selecionado")
        self.info_label.setStyleSheet("color: #666; padding: 5px; background-color: #f5f5f5; border-radius: 3px;")
        layout.addWidget(self.info_label)
        
        # Lista de jogos
        self.game_list = QListWidget()
        self.game_list.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.game_list)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        
        self.copy_btn = QPushButton("📋 Copiar")
        self.copy_btn.clicked.connect(self._copy_selected)
        btn_layout.addWidget(self.copy_btn)
        
        self.remove_btn = QPushButton("❌ Remover")
        self.remove_btn.clicked.connect(self._remove_selected)
        btn_layout.addWidget(self.remove_btn)
        
        self.clear_btn = QPushButton("🗑️ Limpar Tudo")
        self.clear_btn.clicked.connect(self._clear_all)
        btn_layout.addWidget(self.clear_btn)
        
        # Botão para exportar melhores
        self.export_btn = QPushButton("📤 Exportar Melhores")
        self.export_btn.clicked.connect(self._export_best)
        btn_layout.addWidget(self.export_btn)
        
        layout.addLayout(btn_layout)
        
    def set_games(self, games: List):
        """Atualiza a lista de jogos"""
        self.games = games
        self.game_list.clear()
        
        if not games:
            self.info_label.setText("Nenhum jogo selecionado")
            return
        
        # Atualiza info
        best_score = games[0].score * 100 if games else 0
        avg_score = sum(g.score for g in games) / len(games) * 100 if games else 0
        self.info_label.setText(
            f"📊 Total: {len(games)} jogos  |  "
            f"🏆 Melhor Score: {best_score:.1f}%  |  "
            f"📈 Média: {avg_score:.1f}%"
        )
        
        for i, game in enumerate(games):
            numbers_str = " ".join(f"{n:02d}" for n in game.numbers)
            score_percent = game.score * 100
            position = i + 1
            
            # Medalhas para os top 3
            medal = ""
            if position == 1:
                medal = "🥇 "
            elif position == 2:
                medal = "🥈 "
            elif position == 3:
                medal = "🥉 "
            
            item_text = f"{medal}#{position:02d}: {numbers_str}  |  Score: {score_percent:.1f}%"
            item = QListWidgetItem(item_text)
            
            # Cores diferentes para os top 3
            if position == 1:
                item.setBackground(QColor(255, 215, 0))  # Dourado
                item.setForeground(QColor(0, 0, 0))
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            elif position == 2:
                item.setBackground(QColor(192, 192, 192))  # Prata
                item.setForeground(QColor(0, 0, 0))
            elif position == 3:
                item.setBackground(QColor(205, 127, 50))  # Bronze
                item.setForeground(QColor(255, 255, 255))
            elif score_percent >= 70:
                item.setBackground(QColor(144, 238, 144))  # Verde
            elif score_percent >= 60:
                item.setBackground(QColor(255, 255, 200))  # Amarelo
            else:
                item.setBackground(QColor(255, 200, 200))  # Vermelho
            
            self.game_list.addItem(item)
            
    def _on_item_clicked(self, item):
        """Handler para clique em item"""
        index = self.game_list.row(item)
        self.selected_index = index
        self.game_selected.emit(index)
        
    def _copy_selected(self):
        """Copia o jogo selecionado"""
        if self.selected_index >= 0 and self.selected_index < len(self.games):
            game = self.games[self.selected_index]
            text = " ".join(f"{n:02d}" for n in game.numbers)
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "Sucesso", "✅ Jogo copiado para a área de transferência!")
            
    def _remove_selected(self):
        """Remove o jogo selecionado"""
        if self.selected_index >= 0 and self.selected_index < len(self.games):
            self.games.pop(self.selected_index)
            self.set_games(self.games)
            self.selected_index = -1
            
    def _clear_all(self):
        """Limpa todos os jogos"""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "Tem certeza que deseja limpar todos os melhores jogos?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.games.clear()
            self.set_games(self.games)
            self.selected_index = -1
    
    def _export_best(self):
        """Exporta os melhores jogos"""
        if not self.games:
            QMessageBox.warning(self, "Aviso", "Nenhum jogo para exportar")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Melhores Jogos",
            "melhores_jogos.txt",
            "Arquivos de Texto (*.txt)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("=" * 70 + "\n")
                    f.write("⭐ MELHORES JOGOS - LOTOFÁCIL OPTIMIZER PRO\n")
                    f.write("=" * 70 + "\n\n")
                    
                    for i, game in enumerate(self.games, 1):
                        score_percent = game.score * 100
                        numbers_str = " ".join(f"{n:02d}" for n in game.numbers)
                        f.write(f"#{i:02d}: {numbers_str}  |  Score: {score_percent:.1f}%\n")
                    
                    f.write("\n" + "=" * 70 + "\n")
                    f.write(f"Total: {len(self.games)} melhores jogos\n")
                    
                    if self.games:
                        best_score = self.games[0].score * 100
                        f.write(f"Melhor Score: {best_score:.1f}%\n")
                
                QMessageBox.information(self, "Sucesso", f"✅ Exportado para {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar: {str(e)}")
