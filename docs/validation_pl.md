# Zakres sprawdzenia 2.0.0-rc.1

Bazą zmian był commit `b7a5d549d62d9f9830319f8fee226543f12b7d58`.
Kontrole przygotowano 3 października 2026 r.

## Wykonane kontrole

Sprawdzono niezależnym całkowaniem RK4 równania odczytane z kodu źródeł
prądowych INT, INTV, RSTINT i SCHMITT oraz priorytet resetu MONO.
Testy potwierdziły wykładniczy upływ, znak i podtrzymanie całki,
powrót z przeciążenia, trwałe skasowanie pamięci oraz podtrzymanie
stanu w paśmie histerezy. Sprawdzono też dyrektywy warunków początkowych.

Dla D-12 porównano pochodną funkcji pierwotnej z równaniem rozdzielonym
i numerycznie potwierdzono punkt końcowy y=0.99 dla czterech wartości A.
Jest to kontrola matematyczna równania, nie wykonanie jego netlisty
ani porównanie z oryginalną broszurą.

Testy narzędzia kontroli wyników używają syntetycznych logów.
Sprawdzają pomiary skalarne, tabele kroków, kodowania tekstu,
brakujące i nadmiarowe wyniki, wartości niefinitywne, przekroczenie tolerancji
oraz zgłoszenie braku symulatora. Sprawdzono również normalizację wektora
prędkości i zgodność jednostek GEE. Łącznie wykonano 16 testów Python.

Kontrola struktury obejmuje deklaracje 35 bloków, wywołania subukładów,
nazwy parametrów, liczbę pinów, masę, jawne VL, ścieżki include,
pomiary, tabelę API i lokalne odsyłacze Markdown. Zestaw zawiera
23 wejścia netlist, z czego 3 są plikami zgodności dołączającymi
inne przykłady. Kontrola nie jest pełnym parserem SPICE.

## Status LTspice

**Nie wykonano symulacji LTspice w środowisku przygotowania zmian:
program nie był dostępny.** Nie potwierdzono więc akceptacji składni
przez docelową wersję, zbieżności, przebiegów, eksportu WAV ani tolerancji
pomiarów w rzeczywistym symulatorze. Wersja pozostaje kandydatem do wydania.

[acceptance.json](../tests/acceptance.json) określa wymagane wyniki,
nie wynik zaliczenia. Zestaw core zawiera 8 obwodów i 16 przebiegów,
a all 20 obwodów i 31 przebiegów z uwzględnieniem .step.
Trzy pliki zgodności są sprawdzane strukturalnie i nie powielają symulacji.

## Powtórzenie kontroli

Wymagany jest Python 3.10 lub nowszy, bez dodatkowych pakietów.
Z katalogu głównego uruchom:

```console
python tools/check_repository.py
python -m unittest discover -s tests -p "test_*.py" -v
python tools/run_ltspice.py --suite all --exe "C:\\ścieżka\\LTspice.exe" --version-note "wersja z Help/About"
```

Narzędzie wsadowe jest przygotowane dla wykonywalnego programu LTspice
obsługującego opcję `-b`, przede wszystkim instalacji Windows.
Ścieżkę i numer wersji trzeba zastąpić wartościami rzeczywistej instalacji.
Domyślny limit wynosi 300 s na obwód; można go zmienić przez `--timeout`.
Lista obwodów bez uruchamiania: `--suite all --list`.

Symulator pracuje na osobnych kopiach w katalogu tymczasowym `build`.
Narzędzie zachowuje logi i raport `build/ltspice/report.json`;
nie zachowuje dużych plików RAW ani WAV z przebiegu wsadowego.
Każdy wymagany pomiar musi istnieć dla wszystkich kroków i mieścić się
w zadanym przedziale. Brak programu lub logu nie jest wynikiem pozytywnym.

Przed wydaniem należy uzyskać pozytywny raport all w konkretnej wersji
LTspice i sprawdzić stabilność istotnych pomiarów po zmniejszeniu
maksymalnego kroku. Nie należy poszerzać tolerancji wyłącznie po to,
aby ukryć rozbieżność: wymaga ona wyjaśnienia modelu lub błędu numerycznego.
