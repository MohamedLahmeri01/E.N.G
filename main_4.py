import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                            QListWidget, QMessageBox, QFrame, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import networkx as nx
from typing import Dict, List, Set

class KnowledgeBase:
    def __init__(self):
        self.rules = {}
        self.facts = set()
        self.history = []
        
    def add_rule(self, conditions: List[str], conclusion: str, confidence: float):
        rule_id = len(self.rules)
        self.rules[rule_id] = {
            'conditions': conditions,
            'conclusion': conclusion,
            'confidence': confidence
        }
        
    def add_fact(self, fact: str):
        self.facts.add(fact)
        self.history.append(f"Added indicator: {fact}")
        
    def evaluate_rules(self) -> List[Dict]:
        conclusions = []
        for rule_id, rule in self.rules.items():
            if all(cond in self.facts for cond in rule['conditions']):
                conclusions.append({
                    'conclusion': rule['conclusion'],
                    'confidence': rule['confidence'],
                    'rule_id': rule_id
                })
        return conclusions

class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        
    def add_rule_to_graph(self, conditions: List[str], conclusion: str):
        for condition in conditions:
            self.graph.add_edge(condition, conclusion)
            
    def plot(self, canvas: FigureCanvas):
        canvas.figure.clear()
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_color='lightgreen', 
                node_size=2000, font_size=8, arrows=True,
                edge_color='gray', ax=canvas.figure.add_subplot(111))
        canvas.draw()

class StyledButton(QPushButton):
    def __init__(self, text, primary=False):
        super().__init__(text)
        self.setMinimumHeight(40)
        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #1565C0;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)

class ManufacturingExpertSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.kb = KnowledgeBase()
        self.kg = KnowledgeGraph()
        self.setup_manufacturing_knowledge()
        self.init_ui()
        
    def setup_manufacturing_knowledge(self):
        # Quality Control Issues
        self.kb.add_rule(['dimensional_variation', 'tool_wear'], 'possible_tooling_problem', 0.7)
        self.kb.add_rule(['dimensional_variation', 'tool_wear', 'vibration'], 'severe_tooling_issue', 0.9)
        self.kb.add_rule(['surface_defects', 'irregular_finish'], 'quality_control_issue', 0.8)

        # Machine Maintenance Issues
        self.kb.add_rule(['unusual_noise', 'vibration'], 'mechanical_problem', 0.75)
        self.kb.add_rule(['unusual_noise', 'vibration', 'overheating'], 'serious_mechanical_issue', 0.9)
        self.kb.add_rule(['power_fluctuation', 'system_trips'], 'electrical_problem', 0.85)

        # Process Control Issues
        self.kb.add_rule(['temperature_variation', 'pressure_fluctuation'], 'process_control_issue', 0.7)
        self.kb.add_rule(['temperature_variation', 'pressure_fluctuation', 'flow_rate_unstable'], 
                        'severe_process_control', 0.9)

        # Material Handling Issues
        self.kb.add_rule(['feed_rate_unstable', 'material_buildup'], 'material_handling_problem', 0.8)
        self.kb.add_rule(['feed_rate_unstable', 'material_buildup', 'jamming'], 
                        'severe_material_handling', 0.95)

        # Production Efficiency Issues
        self.kb.add_rule(['cycle_time_increase', 'output_decrease'], 'efficiency_problem', 0.75)
        self.kb.add_rule(['cycle_time_increase', 'output_decrease', 'high_reject_rate'], 
                        'serious_efficiency_issue', 0.9)

        # Add rules to knowledge graph
        for rule in self.kb.rules.values():
            self.kg.add_rule_to_graph(rule['conditions'], rule['conclusion'])

    def init_ui(self):
        self.setWindowTitle('Manufacturing Process Expert System')
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 13px;
                color: #333;
                font-weight: bold;
                margin-top: 10px;
            }
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                padding: 5px;
            }
        """)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout()
        
        # Left panel
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                margin: 5px;
            }
        """)
        left_layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("Manufacturing Process Diagnosis")
        header_label.setStyleSheet("""
            font-size: 18px;
            color: #1976D2;
            padding: 10px;
        """)
        left_layout.addWidget(header_label)
        
        # Create scrollable area for indicator buttons
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # Indicators section
        indicators_section = QFrame()
        indicators_layout = QVBoxLayout()
        indicators_label = QLabel("Common Manufacturing Indicators:")
        indicators_layout.addWidget(indicators_label)
        
        # Organize indicators by category
        indicator_categories = {
            "Quality Control": [
                'dimensional_variation', 'tool_wear', 'surface_defects',
                'irregular_finish'
            ],
            "Machine Status": [
                'vibration', 'unusual_noise', 'overheating', 'power_fluctuation',
                'system_trips'
            ],
            "Process Parameters": [
                'temperature_variation', 'pressure_fluctuation',
                'flow_rate_unstable'
            ],
            "Production Issues": [
                'feed_rate_unstable', 'material_buildup', 'jamming',
                'cycle_time_increase', 'output_decrease', 'high_reject_rate'
            ]
        }
        
        for category, indicators in indicator_categories.items():
            category_label = QLabel(category)
            category_label.setStyleSheet("color: #666; font-size: 14px; margin-top: 15px;")
            scroll_layout.addWidget(category_label)
            
            for indicator in indicators:
                btn = StyledButton(indicator.replace('_', ' ').title())
                btn.clicked.connect(lambda checked, s=indicator: self.quick_add_indicator(s))
                scroll_layout.addWidget(btn)
                
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        indicators_layout.addWidget(scroll_area)
        indicators_section.setLayout(indicators_layout)
        left_layout.addWidget(indicators_section)
        
        # Custom indicator input
        input_section = QFrame()
        input_layout = QVBoxLayout()
        input_label = QLabel("Add Custom Indicator:")
        self.indicator_input = QTextEdit()
        self.indicator_input.setPlaceholderText("Enter custom indicator...")
        self.indicator_input.setMaximumHeight(50)
        add_indicator_btn = StyledButton("Add Custom Indicator")
        add_indicator_btn.clicked.connect(self.add_indicator)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.indicator_input)
        input_layout.addWidget(add_indicator_btn)
        input_section.setLayout(input_layout)
        left_layout.addWidget(input_section)
        
        # Current indicators list
        current_section = QFrame()
        current_layout = QVBoxLayout()
        current_label = QLabel("Selected Indicators:")
        self.indicators_list = QListWidget()
        clear_btn = StyledButton("Clear All Indicators")
        clear_btn.clicked.connect(self.clear_indicators)
        
        current_layout.addWidget(current_label)
        current_layout.addWidget(self.indicators_list)
        current_layout.addWidget(clear_btn)
        current_section.setLayout(current_layout)
        left_layout.addWidget(current_section)
        
        # Analysis button
        analyze_btn = StyledButton("START MANUFACTURING ANALYSIS", primary=True)
        analyze_btn.clicked.connect(self.analyze)
        left_layout.addWidget(analyze_btn)
        
        left_panel.setLayout(left_layout)
        
        # Right panel
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                margin: 5px;
            }
        """)
        right_layout = QVBoxLayout()
        
        # Knowledge graph visualization
        graph_label = QLabel("Manufacturing Knowledge Graph")
        self.figure = plt.figure(figsize=(8, 8))
        self.canvas = FigureCanvas(self.figure)
        self.kg.plot(self.canvas)
        
        # Analysis history
        history_label = QLabel("Analysis History")
        self.history_list = QListWidget()
        
        right_layout.addWidget(graph_label)
        right_layout.addWidget(self.canvas)
        right_layout.addWidget(history_label)
        right_layout.addWidget(self.history_list)
        right_panel.setLayout(right_layout)
        
        # Add panels to main layout
        layout.addWidget(left_panel, 40)
        layout.addWidget(right_panel, 60)
        main_widget.setLayout(layout)

    def quick_add_indicator(self, indicator: str):
        self.kb.add_fact(indicator)
        self.indicators_list.addItem(indicator.replace('_', ' ').title())
        self.update_history()

    def add_indicator(self):
        indicator = self.indicator_input.toPlainText().strip().lower()
        if indicator:
            self.kb.add_fact(indicator)
            self.indicators_list.addItem(indicator)
            self.indicator_input.clear()
            self.update_history()

    def clear_indicators(self):
        self.kb.facts.clear()
        self.indicators_list.clear()
        self.kb.history.append("Cleared all indicators")
        self.update_history()

    def analyze(self):
        conclusions = self.kb.evaluate_rules()
        if conclusions:
            conclusions.sort(key=lambda x: x['confidence'], reverse=True)
            analysis_text = "Analysis Results:\n"
            for c in conclusions:
                analysis_text += f"- {c['conclusion'].replace('_', ' ').title()}\n"
                analysis_text += f"  Confidence: {c['confidence']*100}%\n"
            
            QMessageBox.information(self, "Analysis Results", analysis_text)
            self.kb.history.append(analysis_text)
            self.update_history()
        else:
            QMessageBox.information(self, "Analysis Results", 
                                  "No issues identified with current indicators.")

    def update_history(self):
        self.history_list.clear()
        for item in self.kb.history:
            self.history_list.addItem(item)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = ManufacturingExpertSystem()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
    
   
    """
    "Dimensional Variation"
    "Tool Wear"
    "Vibration"
    """
    """
    "Unusual Noise"
"Vibration"
"Overheating"
"Power Fluctuation"
    """

   
