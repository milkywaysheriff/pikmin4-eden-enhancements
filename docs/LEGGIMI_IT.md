# Pikmin 4 — Eden Enhancements 1.0-beta1

Pacchetto modulare di **gallongg** per Pikmin 4 **1.1.1** su Eden,
Title ID `0100B7C00933A000`. È una beta: esiti e limiti in `VERIFICATION.md`.

## Contenuto

- FPS: 60, 120 oppure 180. Scegline una sola; 120/180 sperimentali.
- Timing A41 cumulativa: include le correzioni seguito e salita su Occin
  di A38/A40, più timer aggiuntivi. Va abilitata con ciascuna patch FPS.
- Velocità rotazione manuale camera: +12,5%, +25%, +50%, +75% o +100%.
  Scegline una sola; non cambia distanza o zoom della camera.
- Ultrawide: 5120×2160 oppure 3440×1440 con proiezione per singola visuale A45.
- Opzioni indipendenti: aberrazione cromatica OFF e DR Lock v5.

La configurazione locale più recente usa FPS60, A41, camera +50%, A45
5120×2160, CA OFF e DR Lock. Il nuovo split Dandori 5120 ha conferma
dell'utente; la variante A45 3440 resta da provare in gioco.

## Installazione

1. Ferma il gioco e chiudi Eden. Copia le vecchie mod fuori dalla cartella
   mod per avere un backup. Annota le impostazioni prima di cambiarle.
2. Per trovare il percorso corretto usa il clic destro su Pikmin 4 in
   Eden → apertura della posizione dati mod; poi chiudi di nuovo Eden.
3. Dalle cartelle numerate dello ZIP copia **solo le cartelle `P4 - ...`
   che scegli**, direttamente nella posizione mod di Pikmin 4. Non copiare
   la radice del pacchetto né i contenitori numerati.
4. Ogni cartella `P4 - ...` deve contenere direttamente `exefs/` e i suoi
   file `.pchtxt`. Le FPS richiedono **entrambi** i file main e SDK, oltre
   alla mod timing A41 separata.
5. Nelle proprietà abilita le opzioni scelte e update **1.1.1**. Non
   abilitare due FPS, due camera o due ultrawide insieme. Velocità Eden100%.

Se hai le vecchie mod del lavoro locale, sposta prima fuori quelle
equivalenti: FPS v4, camera v3, `TEST - Follow progress delta ... A38`
(può già contenere A41), `TEST - Ultrawide ... v6` (può già contenere A45),
CA e DR. Rinominare le nuove cartelle non disabilita le vecchie copie.

## Impostazioni ultrawide

GPU **High**, scala Eden **1×**, rapporto **Stretch to Window** e area
immagine con le proporzioni della risoluzione scelta. La CPU locale era
Unsafe; non è necessario cambiarla per installare questo pacchetto.
Non applicare un altro4× sopra questi viewport. Con GPU Low in passato
compariva un difetto giallo, soprattutto al secondo caricamento dopo il titolo.

I rapporti esatti sono64:27 (5120×2160) e43:18 (3440×1440), entrambi
commercialmente21:9. Non usare lo stretch su uno schermo32:9; la variante32:9
non è inclusa. I numeri sono richieste di viewport, non misure della
risoluzione3D interna. DR Lock non forza screen percentage100%. Le patchFPS
impostano un obiettivo; non garantiscono120FPS in ogni scena.

## Ripristino

Chiudi Eden e sposta fuori le cartelle `P4 - ...` installate. Ripristina le
vecchie cartelle dal backup per tornare esattamente alle tue mod precedenti.
Per tornare al timing originale30FPS disabilita tutte le FPS e la timingA41.
Nessun salvataggio, gioco, chiave, firmware o INI è modificato dal pacchetto.

Stop Talking non è inclusa: resta una mod di terzi da scaricare a parte.
Supporto, crediti e limiti dettagliati sono nei documenti inglesi allegati.
