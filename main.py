import os
import json
import sys

# 1. Alapvető adatok és struktúra
wheel_order = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]

sectors = {
    "1. Sektor (0-tól)": wheel_order[0:9],
    "2. Sektor (Jobb)": wheel_order[9:18],
    "3. Sektor (Alsó)": wheel_order[18:28],
    "4. Sektor (Bal)": wheel_order[28:37]
}

# 20 pörgetéses kimaradási valószínűségi táblázat (százalékos formában)
consecutive_probabilities = {
    1: 75.68,
    2: 57.27,
    3: 43.34,
    4: 32.80,
    5: 24.82,
    6: 18.78,
    7: 14.21,
    8: 10.75,
    9: 8.14,
    10: 6.16,
    11: 4.66,
    12: 3.53,
    13: 2.67,
    14: 2.02,
    15: 1.53,
    16: 1.16,
    17: 0.88,
    18: 0.66,
    19: 0.50,
    20: 0.39
}

# 2. Mentési és betöltési funkciók
def save_session_data(filename, history, bankroll, initial_bankroll, unit_bet, sector_streaks):
    data = {
        "history": history,
        "bankroll": bankroll,
        "initial_bankroll": initial_bankroll,
        "unit_bet": unit_bet,
        "sector_streaks": sector_streaks
    }
    filepath = os.path.abspath(filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_session_data(filename):
    filepath = os.path.abspath(filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

# Részletes statisztika kiíró függvény
def print_detailed_statistics(history, initial_bankroll, current_bankroll, unit_bet, sector_streaks):
    total = len(history)
    total_bet = unit_bet * 9
    print("\n" + "=" * 50)
    print("             RÉSZLETES STATISZTIKA")
    print("=" * 50)
    print(f" Összes eddigi pörgetés száma: {total}")
    print(f" Kezdő tőke: {initial_bankroll} | Jelenlegi tőke: {current_bankroll}")
    print(f" Egy számra eső tét: {unit_bet} Ft | Teljes szektor tét (9 szám): {total_bet} Ft")
    
    if total > 0:
        print("\n Sektorok részletes megoszlása, feszültségei és aktuális kimaradási sorozatai:")
        expected_per_sector = total / 4.0
        for s_name, s_nums in sectors.items():
            c = sum(1 for n in history if n in s_nums)
            tension = c - expected_per_sector
            streak = sector_streaks.get(s_name, 0)
            
            # Valószínűség lekérdezése a kimaradási táblázatból
            if streak == 0:
                prob_text = "Nem áll ki (Legutóbb benne volt)"
            elif streak <= 20:
                p_val = consecutive_probabilities.get(streak, 0.39)
                prob_text = f"{streak}. egymás utáni kimaradás esélye: {p_val}%"
            else:
                prob_text = f"{streak}. egymás utáni kimaradás esélye: < 0.39% (Extrém ritka)"
                
            if tension >= 7.0:
                status = "KIRÍVÓAN FESZÜLT (>= 7)"
            elif tension >= 1.5:
                status = "TÚLTERHELT / FESZÜLT"
            elif tension <= -1.5:
                status = "LEMERÜLT (Hiány / Éhes zóna)"
            else:
                status = "NORMÁL / EGYENSÚLYOS"
                
            pct = (c / total) * 100
            print(f"   - {s_name}: {c} találat ({pct:.1f}%) | Feszültség: {tension:+.1f}")
            print(f"     -> Státusz: {status} | Kimaradás: {streak} kör ({prob_text})")
            
        print(f"\n Utolsó 10 pörgetett szám sorrendben: {history[-10:]}")
    else:
        print(" Még nincsenek rögzített pörgetések a statisztikához.")
    print("=" * 50 + "\n")
    sys.stdout.flush()

# 3. Fő interaktív hurok
def start_interactive_session():
    print("==================================================")
    print("    INTERAKTÍV RULETT FESZÜLTSÉG & KIMARADÁS FIGYELŐ")
    print("==================================================\n")
    sys.stdout.flush()
    
    filename = input("Add meg a mentési fájl nevét (pl. jatek.json): ").strip()
    if not filename:
        filename = "rulett_mentes.json"
        
    try:
        initial_bankroll = float(input("Add meg a kezdő bankrollt / tőkét: "))
    except ValueError:
        initial_bankroll = 10000.0
        
    # Egy számra eső tét bekérése (minimum 50 Ft)
    while True:
        try:
            unit_bet = float(input("Add meg az 1 számra eső tétet (minimum 50 Ft): "))
            if unit_bet < 50:
                print(">>> Az 1 számra eső tét legalább 50 Ft kell legyen! Próbáld újra. <<<")
                sys.stdout.flush()
                continue
            break
        except ValueError:
            print(">>> Érvénytelen szám! <<<")
            sys.stdout.flush()

    total_bet = unit_bet * 9
    print(f" [Információ]: Mivel egy szektor 9 számból áll, a teljes körös téted: {total_bet} Ft ({unit_bet} Ft x 9).\n")
    sys.stdout.flush()

    current_bankroll = initial_bankroll
    history = []
    sector_streaks = {s_name: 0 for s_name in sectors.keys()}
    
    existing = load_session_data(filename)
    if existing:
        choice = input(f"Találtam mentést '{filename}' néven. Betöltsem? (igen/nem): ").strip().lower()
        if choice == "igen":
            history = existing.get("history", [])
            current_bankroll = existing.get("bankroll", initial_bankroll)
            initial_bankroll = existing.get("initial_bankroll", initial_bankroll)
            unit_bet = existing.get("unit_bet", unit_bet)
            sector_streaks = existing.get("sector_streaks", {s_name: 0 for s_name in sectors.keys()})
            total_bet = unit_bet * 9
            print(f" -> Siker! Mentés betöltve. Eddigi pörgetések száma: {len(history)}, 1 szám tétje: {unit_bet} Ft")
            sys.stdout.flush()

    print("\n[INFO]: Írj be egy számot (0-36) a pörgetéshez.")
    print("[INFO]: Írd be, hogy **stat**, ha ki akarod kérni a részletes statisztikát.")
    print("[INFO]: Ha ki akarsz lépni és menteni, írd be: q\n")
    print("-" * 50)
    sys.stdout.flush()
    
    if len(history) > 0:
        print_detailed_statistics(history, initial_bankroll, current_bankroll, unit_bet, sector_streaks)
    
    while True:
        user_input = input("Add meg a következőt (szám / stat / q): ").strip().lower()
        
        if user_input == 'q':
            save_session_data(filename, history, current_bankroll, initial_bankroll, unit_bet, sector_streaks)
            print(f"\n[INFO]: Munkamenet elmentve. Kilépés...")
            sys.stdout.flush()
            break
            
        if user_input == 'stat':
            print_detailed_statistics(history, initial_bankroll, current_bankroll, unit_bet, sector_streaks)
            continue
            
        try:
            number = int(user_input)
            if number < 0 or number > 36:
                print(">>> Hiba: 0 és 36 közötti számot adj meg! <<<\n")
                sys.stdout.flush()
                continue
        except ValueError:
            print(">>> Hiba: Érvénytelen parancs! Számot, 'stat'-ot vagy 'q'-t adj meg. <<<\n")
            sys.stdout.flush()
            continue
            
        history.append(number)
        total = len(history)
        
        # --- Szektor kimaradások (streak) frissítése ---
        current_sector_name = ""
        for s_name, s_nums in sectors.items():
            if number in s_nums:
                current_sector_name = s_name
                sector_streaks[s_name] = 0
            else:
                sector_streaks[s_name] += 1

        # --- 20% Védelmi limit vizsgálat ---
        bankroll_diff_pct = abs(current_bankroll - initial_bankroll) / initial_bankroll * 100
        if current_bankroll <= initial_bankroll * 0.8 or current_bankroll >= initial_bankroll * 1.2 or bankroll_diff_pct >= 20.0:
            reason = "veszteség" if current_bankroll < initial_bankroll else "nyereség"
            print(f"\n[VÉDELMI VÁSZJELZÉS] STOP! A 20%-os limit ({reason}) elérve a(z) {total}. pörgetésnél!")
            print(">>> A JÁTÉKOT AZONNAL ABBA KELL HAGYNI! <<<")
            sys.stdout.flush()
            save_session_data(filename, history, current_bankroll, initial_bankroll, unit_bet, sector_streaks)
            break
                
        print(f"\n[{total}. dobás] Beérkezett szám: {number} (Helye: {current_sector_name})")
        
        if total <= 50:
            print(f"   [Megfigyelési fázis: {total}/50 pörgetés] – Adatgyűjtés folyamatban...")
        
        # Feszültségszámítás és kimaradási esélyek kiírása minden szektorra
        counts = {}
        expected_per_sector = total / 4.0
        tension_detected_7 = False
        tension_sector = ""
        
        for s_name, s_nums in sectors.items():
            c = sum(1 for n in history if n in s_nums)
            counts[s_name] = c
            tension = c - expected_per_sector
            
            if tension >= 7.0:
                tension_detected_7 = True
                tension_sector = s_name
            
        print("   [Státusz, Feszültség és Kimaradási Esélyek]:")
        for s_name, c in counts.items():
            tension = c - expected_per_sector
            streak = sector_streaks[s_name]
            
            if streak == 0:
                prob_str = "Találat érkezett (Újraindul)"
            elif streak <= 20:
                p_val = consecutive_probabilities.get(streak, 0.39)
                prob_str = f"{streak}. egymás utáni kimaradás esélye: {p_val}%"
            else:
                prob_str = f"{streak}. egymás utáni kimaradás esélye: < 0.39%"

            if tension >= 7.0:
                status = "KIRÍVÓAN FESZÜLT (>= 7)"
            elif tension >= 1.5:
                status = "TÚLTERHELT / FESZÜLT"
            elif tension <= -1.5:
                status = "LEMERÜLT (Hiány / Éhes zóna)"
            else:
                status = "NORMÁL / EGYENSÚLYOS"
                
            pct = (c / total) * 100
            print(f"     - {s_name}: {c} találat ({pct:.1f}%) | Feszültség: {tension:+.1f}")
            print(f"       -> Státusz: {status} | Kimaradás: {streak} kör ({prob_str})")

        # --- 7-es feszültség elérése esetén interaktív kérdés a játékról és bankrollról ---
        if tension_detected_7:
            print(f"\n   >>> FIGYELEM: A(z) {tension_sector} zóna feszültsége elérte vagy meghaladta a 7-es értéket!")
            sys.stdout.flush()
            play_choice = input("   Játszottál ezzel a jelzéssel? (i / n): ").strip().lower()
            
            if play_choice == 'i':
                result_choice = input("   Nyertél vagy vesztettél a fogadással? (nyert / vesztett): ").strip().lower()
                if result_choice == 'nyert':
                    current_bankroll += total_bet
                    print(f"   [Bankroll frissítve]: Nyereség (+{total_bet} Ft). Jelenlegi tőke: {current_bankroll} Ft")
                elif result_choice == 'vesztett':
                    current_bankroll -= total_bet
                    print(f"   [Bankroll frissítve]: Veszteség (-{total_bet} Ft). Jelenlegi tőke: {current_bankroll} Ft")
                else:
                    print("   [Figyelem]: Ismeretlen válasz, a bankroll nem változott.")
            else:
                print("   [Rögzítve]: Nem játszottál ebben a körben, a tőke változatlan.")

        save_session_data(filename, history, current_bankroll, initial_bankroll, unit_bet, sector_streaks)
        print("-" * 50)
        sys.stdout.flush()

if __name__ == "__main__":
    try:
        start_interactive_session()
    except Exception as e:
        print(f"\nHiba történt: {e}")
        sys.stdout.flush()
