#!/usr/bin/env python3
"""
Yksinkertainen käyttöliittymä NHL scraperille
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from advanced_nhl_scraper import AdvancedNHLScraper
import os

class NHLScraperUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NHL HUT Builder Scraper")
        self.root.geometry("800x600")
        
        self.scraper = None
        self.is_scraping = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Luo käyttöliittymän komponentit"""
        # Pääkehys
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Otsikko
        title_label = ttk.Label(main_frame, text="NHL HUT Builder Web Scraper", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Asetukset
        settings_frame = ttk.LabelFrame(main_frame, text="Asetukset", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Maksimimäärä kortteja
        ttk.Label(settings_frame, text="Maksimimäärä kortteja:").grid(row=0, column=0, sticky=tk.W)
        self.max_cards_var = tk.StringVar(value="50")
        max_cards_entry = ttk.Entry(settings_frame, textvariable=self.max_cards_var, width=10)
        max_cards_entry.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # Yksityiskohtaiset tiedot
        self.detailed_var = tk.BooleanVar()
        detailed_check = ttk.Checkbutton(settings_frame, text="Hae yksityiskohtaiset tiedot", 
                                        variable=self.detailed_var)
        detailed_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Tietokanta tiedosto
        ttk.Label(settings_frame, text="Tietokanta tiedosto:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.db_file_var = tk.StringVar(value="nhl_cards.db")
        db_file_entry = ttk.Entry(settings_frame, textvariable=self.db_file_var, width=30)
        db_file_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=(10, 0))
        
        # Painikkeet
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="Aloita keräys", 
                                      command=self.start_scraping)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="Pysäytä", 
                                     command=self.stop_scraping, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(5, 0))
        
        self.stats_button = ttk.Button(button_frame, text="Näytä tilastot", 
                                      command=self.show_stats)
        self.stats_button.pack(side=tk.LEFT, padx=(5, 0))
        
        self.export_button = ttk.Button(button_frame, text="Vie JSON:ään", 
                                       command=self.export_json)
        self.export_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Edistymispalkki
        self.progress_var = tk.StringVar(value="Valmis")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=3, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        # Logi-ikkuna
        log_frame = ttk.LabelFrame(main_frame, text="Loki", padding="5")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Konfiguroi grid-weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
    
    def log_message(self, message):
        """Lisää viesti logi-ikkunaan"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_scraping(self):
        """Aloita keräys taustalla"""
        if self.is_scraping:
            return
        
        try:
            max_cards = int(self.max_cards_var.get()) if self.max_cards_var.get() else None
        except ValueError:
            messagebox.showerror("Virhe", "Anna kelvollinen numero korttien määrälle")
            return
        
        self.is_scraping = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_bar.start()
        self.progress_var.set("Kerätään kortteja...")
        
        # Aloita keräys taustalla
        thread = threading.Thread(target=self.scrape_thread, 
                                 args=(max_cards, self.detailed_var.get()))
        thread.daemon = True
        thread.start()
    
    def scrape_thread(self, max_cards, detailed):
        """Keräys-thread"""
        try:
            self.scraper = AdvancedNHLScraper(self.db_file_var.get())
            self.log_message("Aloitetaan NHL korttien kerääminen...")
            
            cards_saved = self.scraper.scrape_cards(max_cards=max_cards, detailed_info=detailed)
            
            self.log_message(f"Keräys valmis! Tallennettu {cards_saved} korttia.")
            
            # Näytä tilastot
            stats = self.scraper.get_database_stats()
            self.log_message(f"Tietokannassa nyt {stats['total_cards']} korttia")
            
        except Exception as e:
            self.log_message(f"Virhe keräyksessä: {e}")
        finally:
            self.scraping_finished()
    
    def stop_scraping(self):
        """Pysäytä keräys"""
        self.is_scraping = False
        self.log_message("Keräys pysäytetty käyttäjän toimesta")
        self.scraping_finished()
    
    def scraping_finished(self):
        """Keräyksen lopetus"""
        self.is_scraping = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_bar.stop()
        self.progress_var.set("Valmis")
    
    def show_stats(self):
        """Näytä tietokannan tilastot"""
        if not self.scraper:
            try:
                self.scraper = AdvancedNHLScraper(self.db_file_var.get())
            except Exception as e:
                messagebox.showerror("Virhe", f"Tietokannan avaaminen epäonnistui: {e}")
                return
        
        try:
            stats = self.scraper.get_database_stats()
            
            stats_text = f"""Tietokannan tilastot:
            
Kortteja yhteensä: {stats['total_cards']}
X-Factor kyvyjä: {stats['total_abilities']}
Tilastoja: {stats['total_stats']}

Yleisimmät X-Factor kyvyt:"""
            
            for ability, count in stats['top_abilities'][:5]:
                stats_text += f"\n  {ability}: {count}"
            
            if stats['top_ratings']:
                stats_text += "\n\nKorkeimmat ratingit:"
                for name, rating in stats['top_ratings'][:5]:
                    stats_text += f"\n  {name}: {rating}"
            
            messagebox.showinfo("Tietokannan tilastot", stats_text)
            
        except Exception as e:
            messagebox.showerror("Virhe", f"Tilastojen hakeminen epäonnistui: {e}")
    
    def export_json(self):
        """Vie tiedot JSON-muotoon"""
        if not self.scraper:
            try:
                self.scraper = AdvancedNHLScraper(self.db_file_var.get())
            except Exception as e:
                messagebox.showerror("Virhe", f"Tietokannan avaaminen epäonnistui: {e}")
                return
        
        try:
            output_file = "nhl_cards_export.json"
            self.scraper.export_to_json(output_file)
            
            if os.path.exists(output_file):
                messagebox.showinfo("Vienti onnistui", f"Tiedot vietiin tiedostoon: {output_file}")
            else:
                messagebox.showerror("Virhe", "JSON-tiedoston luominen epäonnistui")
                
        except Exception as e:
            messagebox.showerror("Virhe", f"Vienti epäonnistui: {e}")

def main():
    """Pääohjelma"""
    root = tk.Tk()
    app = NHLScraperUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()