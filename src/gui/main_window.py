"""
Pääikkuna NHL 26 HUT Team Builder -sovellukselle.
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLabel, QLineEdit, QComboBox, 
                             QSpinBox, QTextEdit, QSplitter, QGroupBox,
                             QHeaderView, QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import sys
import os

# Lisää src-kansio Python-polkuun
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ..database.database_manager import DatabaseManager
from ..optimization.chemistry_system import ChemistrySystem
from ..optimization.team_optimizer import TeamOptimizer

class OptimizationThread(QThread):
    """Säie joukkueen optimointia varten."""
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, optimizer, max_salary, min_ovr, preferred_teams, preferred_nationalities):
        super().__init__()
        self.optimizer = optimizer
        self.max_salary = max_salary
        self.min_ovr = min_ovr
        self.preferred_teams = preferred_teams
        self.preferred_nationalities = preferred_nationalities
    
    def run(self):
        try:
            self.progress.emit(10)
            teams = self.optimizer.find_optimal_team(
                max_salary=self.max_salary,
                min_ovr=self.min_ovr,
                preferred_teams=self.preferred_teams,
                preferred_nationalities=self.preferred_nationalities
            )
            self.progress.emit(100)
            self.finished.emit(teams)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    """Pääikkuna."""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.chemistry_system = ChemistrySystem()
        self.team_optimizer = TeamOptimizer(self.db_manager, self.chemistry_system)
        self.current_teams = []
        
        self.init_ui()
        self.load_initial_data()
    
    def init_ui(self):
        """Alustaa käyttöliittymän."""
        self.setWindowTitle("NHL 26 HUT Team Builder")
        self.setGeometry(100, 100, 1400, 900)
        
        # Pääwidget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Päälayout
        main_layout = QVBoxLayout(central_widget)
        
        # Otsikko
        title_label = QLabel("NHL 26 HUT Team Builder")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Tab-widget
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # Joukkueen optimointi -tab
        self.optimization_tab = self.create_optimization_tab()
        tab_widget.addTab(self.optimization_tab, "Joukkueen Optimointi")
        
        # Pelaajakortit -tab
        self.players_tab = self.create_players_tab()
        tab_widget.addTab(self.players_tab, "Pelaajakortit")
        
        # Kemiat -tab
        self.chemistry_tab = self.create_chemistry_tab()
        tab_widget.addTab(self.chemistry_tab, "Kemiat")
        
        # Statusbar
        self.statusBar().showMessage("Valmis")
    
    def create_optimization_tab(self):
        """Luo joukkueen optimointi -tabin."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Asetukset
        settings_group = QGroupBox("Optimointiasetukset")
        settings_layout = QHBoxLayout(settings_group)
        
        # Maksimipalkka
        settings_layout.addWidget(QLabel("Maksimipalkka:"))
        self.max_salary_spinbox = QSpinBox()
        self.max_salary_spinbox.setRange(10000000, 200000000)
        self.max_salary_spinbox.setValue(100000000)
        self.max_salary_spinbox.setSuffix(" $")
        settings_layout.addWidget(self.max_salary_spinbox)
        
        # Minimikokonaisarvo
        settings_layout.addWidget(QLabel("Minimikokonaisarvo:"))
        self.min_ovr_spinbox = QSpinBox()
        self.min_ovr_spinbox.setRange(60, 99)
        self.min_ovr_spinbox.setValue(80)
        settings_layout.addWidget(self.min_ovr_spinbox)
        
        # Suositellut joukkueet
        settings_layout.addWidget(QLabel("Suositellut joukkueet:"))
        self.preferred_teams_edit = QLineEdit()
        self.preferred_teams_edit.setPlaceholderText("Esim: Chicago Blackhawks, Boston Bruins")
        settings_layout.addWidget(self.preferred_teams_edit)
        
        # Suositellut kansallisuudet
        settings_layout.addWidget(QLabel("Suositellut kansallisuudet:"))
        self.preferred_nationalities_edit = QLineEdit()
        self.preferred_nationalities_edit.setPlaceholderText("Esim: Finland, Canada, USA")
        settings_layout.addWidget(self.preferred_nationalities_edit)
        
        # Optimoi-painike
        self.optimize_button = QPushButton("Optimoi Joukkue")
        self.optimize_button.clicked.connect(self.start_optimization)
        settings_layout.addWidget(self.optimize_button)
        
        layout.addWidget(settings_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Tulokset
        results_group = QGroupBox("Optimoidut Joukkueet")
        results_layout = QVBoxLayout(results_group)
        
        # Joukkueet-taulukko
        self.teams_table = QTableWidget()
        self.teams_table.setColumnCount(7)
        self.teams_table.setHorizontalHeaderLabels([
            "Kokonaisarvo", "Palkka", "AP", "OVR Boost", "Salary Cap Boost", "AP Boost", "Tehokkuus"
        ])
        self.teams_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.teams_table.itemSelectionChanged.connect(self.on_team_selected)
        results_layout.addWidget(self.teams_table)
        
        layout.addWidget(results_group)
        
        # Splitter joukkueen ja pelaajien välillä
        splitter = QSplitter(Qt.Horizontal)
        
        # Valitun joukkueen tiedot
        team_details_group = QGroupBox("Valitun Joukkueen Tiedot")
        team_details_layout = QVBoxLayout(team_details_group)
        
        self.team_details_text = QTextEdit()
        self.team_details_text.setReadOnly(True)
        team_details_layout.addWidget(self.team_details_text)
        
        splitter.addWidget(team_details_group)
        
        # Pelaajien tiedot
        players_group = QGroupBox("Pelaajat")
        players_layout = QVBoxLayout(players_group)
        
        self.team_players_table = QTableWidget()
        self.team_players_table.setColumnCount(6)
        self.team_players_table.setHorizontalHeaderLabels([
            "Nimi", "Joukkue", "Kansallisuus", "Asema", "OVR", "Palkka"
        ])
        self.team_players_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        players_layout.addWidget(self.team_players_table)
        
        splitter.addWidget(players_group)
        
        layout.addWidget(splitter)
        
        return widget
    
    def create_players_tab(self):
        """Luo pelaajakortit -tabin."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Hakuasetukset
        search_group = QGroupBox("Haku")
        search_layout = QHBoxLayout(search_group)
        
        search_layout.addWidget(QLabel("Hakusana:"))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.search_players)
        search_layout.addWidget(self.search_edit)
        
        search_layout.addWidget(QLabel("Asema:"))
        self.position_combo = QComboBox()
        self.position_combo.addItems(["Kaikki", "C", "LW", "RW", "LD", "RD", "G"])
        self.position_combo.currentTextChanged.connect(self.search_players)
        search_layout.addWidget(self.position_combo)
        
        search_layout.addWidget(QLabel("Joukkue:"))
        self.team_combo = QComboBox()
        self.team_combo.addItem("Kaikki")
        self.team_combo.currentTextChanged.connect(self.search_players)
        search_layout.addWidget(self.team_combo)
        
        layout.addWidget(search_group)
        
        # Pelaajataulukko
        self.players_table = QTableWidget()
        self.players_table.setColumnCount(8)
        self.players_table.setHorizontalHeaderLabels([
            "Nimi", "Joukkue", "Kansallisuus", "Asema", "OVR", "Palkka", "AP", "Korttityyppi"
        ])
        self.players_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.players_table)
        
        return widget
    
    def create_chemistry_tab(self):
        """Luo kemiat -tabin."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Kemiat-taulukko
        self.chemistry_table = QTableWidget()
        self.chemistry_table.setColumnCount(4)
        self.chemistry_table.setHorizontalHeaderLabels([
            "Nimi", "Tyyppi", "Arvo", "Kuvaus"
        ])
        self.chemistry_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.chemistry_table)
        
        return widget
    
    def load_initial_data(self):
        """Lataa alkuperäiset tiedot."""
        # Lataa joukkueet
        teams = self.db_manager.get_all_players()
        unique_teams = list(set(player['team'] for player in teams))
        unique_teams.sort()
        self.team_combo.addItems(unique_teams)
        
        # Lataa kemiat
        self.load_chemistry_data()
        
        # Lataa pelaajat
        self.search_players()
    
    def load_chemistry_data(self):
        """Lataa kemiat-tiedot."""
        chemistries = self.chemistry_system.get_available_boosts()
        
        self.chemistry_table.setRowCount(len(chemistries))
        
        for i, chem in enumerate(chemistries):
            self.chemistry_table.setItem(i, 0, QTableWidgetItem(chem.name))
            self.chemistry_table.setItem(i, 1, QTableWidgetItem(chem.boost_type))
            self.chemistry_table.setItem(i, 2, QTableWidgetItem(str(chem.boost_value)))
            self.chemistry_table.setItem(i, 3, QTableWidgetItem(chem.description))
    
    def search_players(self):
        """Hakee pelaajia hakuehdoilla."""
        search_text = self.search_edit.text()
        position = self.position_combo.currentText()
        team = self.team_combo.currentText()
        
        # Hae pelaajat
        if search_text:
            players = self.db_manager.search_players(search_text)
        else:
            players = self.db_manager.get_all_players()
        
        # Suodata aseman mukaan
        if position != "Kaikki":
            players = [p for p in players if p['position'] == position]
        
        # Suodata joukkueen mukaan
        if team != "Kaikki":
            players = [p for p in players if p['team'] == team]
        
        # Järjestä OVR:n mukaan
        players.sort(key=lambda x: x['overall_rating'], reverse=True)
        
        # Päivitä taulukko
        self.players_table.setRowCount(len(players))
        
        for i, player in enumerate(players):
            self.players_table.setItem(i, 0, QTableWidgetItem(player['name']))
            self.players_table.setItem(i, 1, QTableWidgetItem(player['team']))
            self.players_table.setItem(i, 2, QTableWidgetItem(player['nationality']))
            self.players_table.setItem(i, 3, QTableWidgetItem(player['position']))
            self.players_table.setItem(i, 4, QTableWidgetItem(str(player['overall_rating'])))
            self.players_table.setItem(i, 5, QTableWidgetItem(f"{player['salary']:,}"))
            self.players_table.setItem(i, 6, QTableWidgetItem(str(player['ap_points'])))
            self.players_table.setItem(i, 7, QTableWidgetItem(player.get('card_type', '')))
    
    def start_optimization(self):
        """Aloittaa joukkueen optimoinnin."""
        # Hae asetukset
        max_salary = self.max_salary_spinbox.value()
        min_ovr = self.min_ovr_spinbox.value()
        
        preferred_teams = []
        if self.preferred_teams_edit.text():
            preferred_teams = [t.strip() for t in self.preferred_teams_edit.text().split(',')]
        
        preferred_nationalities = []
        if self.preferred_nationalities_edit.text():
            preferred_nationalities = [n.strip() for n in self.preferred_nationalities_edit.text().split(',')]
        
        # Aloita optimointi säikeessä
        self.optimization_thread = OptimizationThread(
            self.team_optimizer, max_salary, min_ovr, preferred_teams, preferred_nationalities
        )
        self.optimization_thread.progress.connect(self.progress_bar.setValue)
        self.optimization_thread.finished.connect(self.on_optimization_finished)
        self.optimization_thread.error.connect(self.on_optimization_error)
        
        self.optimize_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.optimization_thread.start()
    
    def on_optimization_finished(self, teams):
        """Kutsutaan kun optimointi on valmis."""
        self.current_teams = teams
        self.update_teams_table(teams)
        
        self.optimize_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        self.statusBar().showMessage(f"Löytyi {len(teams)} joukkuetta")
    
    def on_optimization_error(self, error_msg):
        """Kutsutaan kun optimoinnissa tapahtuu virhe."""
        QMessageBox.critical(self, "Virhe", f"Optimointivirhe: {error_msg}")
        
        self.optimize_button.setEnabled(True)
        self.progress_bar.setVisible(False)
    
    def update_teams_table(self, teams):
        """Päivittää joukkueet-taulukon."""
        self.teams_table.setRowCount(len(teams))
        
        for i, team in enumerate(teams):
            self.teams_table.setItem(i, 0, QTableWidgetItem(f"{team.overall_rating:.1f}"))
            self.teams_table.setItem(i, 1, QTableWidgetItem(f"{team.total_salary:,}"))
            self.teams_table.setItem(i, 2, QTableWidgetItem(str(team.total_ap)))
            self.teams_table.setItem(i, 3, QTableWidgetItem(str(team.chemistry_boosts.get('ovr', 0))))
            self.teams_table.setItem(i, 4, QTableWidgetItem(f"{team.chemistry_boosts.get('salary_cap', 0):,}"))
            self.teams_table.setItem(i, 5, QTableWidgetItem(str(team.chemistry_boosts.get('ap', 0))))
            
            # Laske tehokkuus
            efficiency = team.overall_rating / (team.total_salary / 1000000) if team.total_salary > 0 else 0
            self.teams_table.setItem(i, 6, QTableWidgetItem(f"{efficiency:.2f}"))
    
    def on_team_selected(self):
        """Kutsutaan kun joukkue valitaan."""
        current_row = self.teams_table.currentRow()
        if current_row >= 0 and current_row < len(self.current_teams):
            team = self.current_teams[current_row]
            self.show_team_details(team)
    
    def show_team_details(self, team):
        """Näyttää joukkueen yksityiskohdat."""
        # Päivitä joukkueen tiedot
        details = f"Kokonaisarvo: {team.overall_rating:.1f}\n"
        details += f"Kokonaispalkka: {team.total_salary:,} $\n"
        details += f"Kokonais-AP: {team.total_ap}\n"
        details += f"OVR Boost: +{team.chemistry_boosts.get('ovr', 0)}\n"
        details += f"Salary Cap Boost: +{team.chemistry_boosts.get('salary_cap', 0):,} $\n"
        details += f"AP Boost: +{team.chemistry_boosts.get('ap', 0)}\n"
        
        self.team_details_text.setText(details)
        
        # Päivitä pelaajataulukko
        all_players = team.forwards + team.defense + [team.goalie]
        self.team_players_table.setRowCount(len(all_players))
        
        for i, player in enumerate(all_players):
            self.team_players_table.setItem(i, 0, QTableWidgetItem(player['name']))
            self.team_players_table.setItem(i, 1, QTableWidgetItem(player['team']))
            self.team_players_table.setItem(i, 2, QTableWidgetItem(player['nationality']))
            self.team_players_table.setItem(i, 3, QTableWidgetItem(player['position']))
            self.team_players_table.setItem(i, 4, QTableWidgetItem(str(player['overall_rating'])))
            self.team_players_table.setItem(i, 5, QTableWidgetItem(f"{player['salary']:,}"))