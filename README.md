# APM-1 — Analog Programmed Machine for LTspice

Biblioteka bloków obliczeń analogowych i hybrydowych: sumatory, mnożniki,
integratory, filtry, ograniczniki, układy czasowe i generator rampy.

**Wersja: 2.0.0-rc.1.** Poprawki zmieniają działanie upływu i pamięci stanu.
Przed użyciem dawnych obwodów należy przeczytać [instrukcję migracji](docs/migration_pl.md).
Sprawdzono strukturę i równania za pomocą testów Python; wyniki LTspice wymagają
osobnego uruchomienia. Aktualny zakres potwierdzenia podano w [raporcie](docs/validation_pl.md).

## Pierwsze uruchomienie

Pobierz całe repozytorium przez **Code → Download ZIP** i rozpakuj je,
zachowując strukturę katalogów. Otwórz w LTspice plik
[examples/01_algebra.cir](examples/01_algebra.cir) i wybierz **Run**.
Nie trzeba kopiować bibliotek do katalogów instalacyjnych LTspice.

W oknie przebiegów dodaj `V(sum)`, `V(normalized)` i `V(product)`.
W **SPICE Error Log** odczytaj pomiary: suma wynosi 5, iloczyn po
kompensacji 6, a miary błędu powinny mieścić się w tolerancjach z
[tests/acceptance.json](tests/acceptance.json).
Przykład wykonuje trzy przebiegi dla `VL=5,10,20`.

[Pełna instrukcja](docs/usage_pl.md) opisuje ścieżki, parametry, wykresy XY,
maksymalny krok, warunki początkowe i uruchomienie z wiersza poleceń.
Docelowe środowisko to LTspice 24.x/26.x; nie deklarujemy potwierdzenia
każdej wersji ani zgodności z innymi odmianami SPICE.

## Rozdzielenie odpowiedzialności

| Materiał | Zawartość |
|---|---|
| [apm1_lib.txt](apm1_lib.txt) | Kod 34 subukładów APM-1. |
| [apm1_wob_lib.txt](apm1_wob_lib.txt) | Kod rozszerzenia `WOBLIN`; wymaga głównej biblioteki. |
| [Specyfikacja](docs/reference_pl.md) | Pełny inwentarz pinów, parametrów, równań i ograniczeń. |
| [Instrukcja](docs/usage_pl.md) | Sposób przygotowania i uruchomienia obwodu. |
| [Zasady dla LLM](docs/llm_rules_pl.md) | Generowanie obwodów zgodnych ze specyfikacją. |
| [Przykłady](examples/README.md) | Pięć podstawowych przykładów i obwody zaawansowane. |
| [Migracja](docs/migration_pl.md) | Zmiany działania względem commitu `b7a5d54`. |

Biblioteki mają rozszerzenie `.txt`, lecz zawierają kod SPICE. Dokumentacji
Markdown i archiwalnych komentarzy nie wolno dołączać dyrektywą `.include`.

## Konwencje

Ostatni pin każdego bloku to `GDN`; instancje na głównym poziomie obwodu
łączą go bezpośrednio z węzłem `0`.
`VL` jest współczynnikiem normalizacji, a nie zasilaniem ani wspólnym
ogranicznikiem wszystkich węzłów. Bloki mające parametr `VL` otrzymują go
jawnie, np. `XM out a b 0 MUL VL={VL}`.

Integratory mają rzeczywisty stan na kondensatorze; `leak` ma jednostkę
`1/s`. `INTV` stosuje ograniczenie wyjścia i sprzężenie przeciw nadmiernemu
narastaniu stanu. Reset `RSTINT` ma skończoną stałą czasową `Tr`.
Zmiany te opisano w specyfikacji, bez utożsamiania ograniczenia wyjścia
z idealnym ograniczeniem wewnętrznego stanu.

## Kontrola

Z katalogu głównego uruchom:

```console
python tools/check_repository.py
python -m unittest discover -s tests -p "test_*.py" -v
python tools/run_ltspice.py --exe "C:\ścieżka\do\LTspice.exe"
```

Pierwsze dwa polecenia nie wykonują symulacji SPICE. Trzecie uruchamia
LTspice i sprawdza wyniki pomiarów względem jawnych tolerancji.

## Licencja

Kod biblioteki i netlisty objęto [licencją MIT](LICENSE).
Autor oryginalnej biblioteki i przykładów: Dariusz Domal.
Broszura D-12 jest materiałem źródłowym; jej obecność nie oznacza
przelicencjonowania praw do dokumentu.
