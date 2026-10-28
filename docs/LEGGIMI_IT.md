# Installazione e opzioni

Mod opzionali per **Pikmin 4 1.1.1 su Eden**.
Scegli le funzioni che ti servono: non attivare tutte le varianti insieme.

| Funzione | Opzioni |
|---|---|
| FPS più alti | Obiettivo 60, 120 o 180 FPS; una sola opzione |
| Movimento Pikmin | Correzioni al seguito e alla salita su Occin ai frame rate più alti; richiesta con le mod FPS |
| Camera più veloce | Rotazione manuale +12,5%, +25%, +50%, +75% o +100%; una sola opzione |
| Ultrawide | 3440×1440 o 5120×2160; una sola opzione |
| Grafica opzionale | Aberrazione cromatica OFF e blocco della risoluzione dinamica |

## Installazione

1. Scarica lo ZIP delle mod allegato alla release GitHub ed estrailo fuori
   dalla cartella mod di Eden. Sources serve per lo sviluppo.
2. Ferma il gioco e chiudi Eden. Salva un backup delle vecchie mod che
   modificano le stesse funzioni, fuori dalla cartella mod.
3. Trova la posizione dati mod dal menu clic destro di Pikmin 4 in Eden;
   poi chiudi di nuovo Eden prima di copiare i file.
4. Copia **solo le cartelle `P4 - ...` scelte** dai contenitori numerati
   direttamente nella cartella mod del gioco. Non copiare lì la radice
   dello ZIP o i contenitori numerati.
5. Nelle proprietà abilita le mod scelte e l'update **1.1.1**. Mantieni
   la velocità di emulazione al **100%**.

Con una mod FPS servono entrambi i file main e SDK nella sua cartella
`exefs`, più la mod separata **Pikmin Movement and Timers**. Non attivare
due mod FPS, due velocità camera o due ultrawide insieme. Rimuovi le
vecchie copie equivalenti quando aggiorni: il nuovo nome non le disattiva.

## Ultrawide e limiti

Usa GPU **High**, scala Eden **1×**, **Stretch to Window** e un'area
immagine con le proporzioni della risoluzione scelta. Non applicare un
altro 4× né una seconda mod che modifica output/proiezione. Con GPU Low
si era verificato un difetto giallo dopo il ritorno al titolo e un nuovo
caricamento. La CPU locale è Unsafe; le mod non la cambiano.

Entrambe le opzioni sono commercialmente 21:9: i rapporti esatti sono
43:18 per 3440×1440 e 64:27 per 5120×2160. Non sono pensate per 32:9. Le
misure indicate sono richieste di viewport, non misure del rendering 3D.

La configurazione locale usa 60 FPS e 5120×2160. Le correzioni al seguito e
alla salita su Occin hanno riscontro positivo. 120 FPS è sperimentale;
180FPS e l'attuale 3440×1440 non sono ancora state provate in gioco.
L'obiettivo FPS non garantisce quelle prestazioni in ogni scena; il blocco
della risoluzione dinamica non forza lo screen percentage al 100%.
Dettagli delle verifiche in `VERIFICATION.md`.

## Ripristino

Chiudi Eden e sposta fuori le cartelle installate. Ripristina il backup
per recuperare le mod precedenti. Per tornare al timing originale a 30 FPS
disabilita tutte le mod FPS e la mod movimento. Il download non sostituisce
giochi, salvataggi o file INI.
