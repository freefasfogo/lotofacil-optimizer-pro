"""
Módulo de exportação para PDF
"""
from typing import List, Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import numpy as np
from datetime import datetime

from core.game import Game
from core.population import Population
from core.statistics import StatisticsAnalyzer


class PDFExporter:
    """
    Exportador para PDF com relatório completo
    
    Gera:
    - Capa
    - Lista de jogos
    - Estatísticas
    - Gráficos
    - Análises
    """
    
    def __init__(self):
        self.stats_analyzer = StatisticsAnalyzer()
        self.styles = getSampleStyleSheet()
        
    def export(self, games: List[Game], filename: str, config: Dict[str, Any]):
        """
        Exporta jogos para arquivo PDF
        
        Args:
            games: Lista de jogos
            filename: Nome do arquivo
            config: Configurações do sistema
        """
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Conteúdo
        story = []
        
        # Capa
        story.extend(self._create_cover(config))
        story.append(PageBreak())
        
        # Jogos
        story.extend(self._create_games_section(games))
        story.append(PageBreak())
        
        # Estatísticas
        stats = self.stats_analyzer.analyze_population(Population(games))
        story.extend(self._create_statistics_section(games, stats))
        story.append(PageBreak())
        
        # Gráficos
        story.extend(self._create_charts_section(games, stats))
        story.append(PageBreak())
        
        # Análises
        story.extend(self._create_analysis_section(games, stats))
        
        # Gera PDF
        doc.build(story)
    
    def _create_cover(self, config: Dict[str, Any]) -> List:
        """Cria a capa do relatório"""
        story = []
        
        # Título principal
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=self.styles['Title'],
            fontSize=28,
            textColor=colors.HexColor('#0066CC'),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        story.append(Paragraph("Lotofácil Optimizer PRO", title_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Subtítulo
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#333333'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        story.append(Paragraph("Relatório de Otimização", subtitle_style))
        story.append(Spacer(1, 2*cm))
        
        # Informações
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=10
        )
        
        story.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", info_style))
        story.append(Paragraph(f"Algoritmo: {config.get('algoritmo', 'Genetic Algorithm')}", info_style))
        story.append(Paragraph(f"Gerações: {config.get('geracoes', 500)}", info_style))
        story.append(Paragraph(f"População: {config.get('populacao', 1000)}", info_style))
        
        return story
    
    def _create_games_section(self, games: List[Game]) -> List:
        """Cria seção com lista de jogos"""
        story = []
        
        # Título
        story.append(Paragraph("Jogos Gerados", self.styles['Heading1']))
        story.append(Spacer(1, 0.5*cm))
        
        # Tabela de jogos
        data = [["Jogo"] + [f"N{i+1}" for i in range(15)] + ["Score"]]
        
        for i, game in enumerate(games[:50], 1):  # Limita a 50 jogos no PDF
            row = [f"#{i}"] + list(game.numbers) + [f"{game.score:.4f}"]
            data.append(row)
        
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066CC')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ]))
        
        story.append(table)
        
        if len(games) > 50:
            story.append(Spacer(1, 0.5*cm))
            story.append(Paragraph(f"* Mostrando apenas os 50 primeiros jogos de {len(games)}", self.styles['Normal']))
        
        return story
    
    def _create_statistics_section(self, games: List[Game], stats) -> List:
        """Cria seção de estatísticas"""
        story = []
        
        story.append(Paragraph("Estatísticas", self.styles['Heading1']))
        story.append(Spacer(1, 0.5*cm))
        
        # Estatísticas básicas
        data = [
            ["Métrica", "Valor"],
            ["Total de Jogos", str(len(games))],
            ["Score Médio", f"{sum(g.score for g in games) / len(games):.4f}" if games else "0"],
            ["Melhor Score", f"{max(g.score for g in games):.4f}" if games else "0"],
            ["Pior Score", f"{min(g.score for g in games):.4f}" if games else "0"],
            ["Desvio Padrão", f"{np.std([g.score for g in games]):.4f}" if games else "0"],
            ["Frequência STD", f"{stats.frequency_std:.4f}"],
            ["Entropia", f"{stats.frequency_entropy:.4f}"],
        ]
        
        table = Table(data, colWidths=[6*cm, 6*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066CC')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        story.append(table)
        
        return story
    
    def _create_charts_section(self, games: List[Game], stats) -> List:
        """Cria seção com gráficos"""
        story = []
        
        story.append(Paragraph("Gráficos", self.styles['Heading1']))
        story.append(Spacer(1, 0.5*cm))
        
        # Gráfico de frequência
        freq_data = stats.number_frequencies
        
        drawing = Drawing(400, 200)
        chart = HorizontalBarChart()
        chart.x = 50
        chart.y = 50
        chart.width = 300
        chart.height = 120
        
        chart.data = [freq_data[:15], freq_data[15:]]
        chart.categoryAxis.categoryNames = [str(i+1) for i in range(15)]
        chart.categoryAxis.labels.angle = 45
        chart.categoryAxis.labels.fontSize = 8
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = max(freq_data) * 1.2
        
        drawing.add(chart)
        story.append(drawing)
        story.append(Spacer(1, 0.5*cm))
        
        # Tabela de frequências
        freq_table = [["Dezena", "Frequência", "%"]]
        total = sum(freq_data)
        
        for i, count in enumerate(freq_data, 1):
            freq_table.append([str(i), str(count), f"{count/total*100:.1f}%"])
        
        table = Table(freq_table, colWidths=[3*cm, 3*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066CC')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(table)
        
        return story
    
    def _create_analysis_section(self, games: List[Game], stats) -> List:
        """Cria seção de análises"""
        story = []
        
        story.append(Paragraph("Análises Detalhadas", self.styles['Heading1']))
        story.append(Spacer(1, 0.5*cm))
        
        # Análise de Linhas
        story.append(Paragraph("Distribuição por Linhas", self.styles['Heading2']))
        story.append(Spacer(1, 0.3*cm))
        
        line_data = [["Linha", "Média", "Mínimo", "Máximo"]]
        for line in range(5):
            values = [game.linhas[line] for game in games]
            line_data.append([
                f"Linha {line+1}",
                f"{np.mean(values):.2f}",
                str(min(values)),
                str(max(values))
            ])
        
        table = Table(line_data, colWidths=[4*cm, 3*cm, 3*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066CC')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.5*cm))
        
        # Análise de Colunas
        story.append(Paragraph("Distribuição por Colunas", self.styles['Heading2']))
        story.append(Spacer(1, 0.3*cm))
        
        col_data = [["Coluna", "Média", "Mínimo", "Máximo"]]
        for col in range(5):
            values = [game.colunas[col] for game in games]
            col_data.append([
                f"Coluna {col+1}",
                f"{np.mean(values):.2f}",
                str(min(values)),
                str(max(values))
            ])
        
        table = Table(col_data, colWidths=[4*cm, 3*cm, 3*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066CC')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.5*cm))
        
        # Consecutivos
        story.append(Paragraph("Análise de Consecutivos", self.styles['Heading2']))
        story.append(Spacer(1, 0.3*cm))
        
        consec_data = [["Consecutivos", "Frequência", "%"]]
        total = len(games)
        
        for consec, freq in sorted(stats.consecutive_analysis.items()):
            consec_data.append([
                str(consec),
                str(freq),
                f"{freq/total*100:.1f}%"
            ])
        
        table = Table(consec_data, colWidths=[4*cm, 3*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066CC')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        
        story.append(table)
        
        return story
