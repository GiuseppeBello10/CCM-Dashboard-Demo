import pandas as pd

def caricamento_dati_rischio(nome_file):
    # Carica il file Excel
    df = pd.read_excel(nome_file,sheet_name="risk")
    # Crea il dizionario: chiave = Paese, valore = dizionario dei rischi
    rischi = df.set_index('Paese').T.to_dict()
    # Visualizza il risultato
    #print(rischi_paese)
    return rischi

def caricamento_dati_pesi(nome_file):
    df = pd.read_excel(nome_file,sheet_name="pesi_settore")
    pesi = df.set_index('Settore').T.to_dict()
    #print(pesi_settore)
    return pesi
    
def caricamento_dati_fattori(nome_file):
    df = pd.read_excel(nome_file,sheet_name="fattori")
    fattori = df.set_index('Strategia').T.to_dict()
    #print(fattori_strategia)
    return fattori

