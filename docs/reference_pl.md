# Specyfikacja APM-1 2.0.0-rc.1

Dokument określa zachowanie modeli; deklaracje `.subckt` określają składnię
wywołania. Tabela poniżej jest generowana z bibliotek poleceniem
`python tools/check_repository.py --write-api`. Rozbieżność dokumentacji
z implementacją wymaga wyjaśnienia i testu, nie automatycznego uznania
dowolnego opisu za poprawny.

## Piny i parametry

`GDN` musi być połączony z węzłem `0`. Dotyczy to również integratorów,
których lokalne dyrektywy `.ic` ustawiają potencjał węzła stanu względem zera.
Obsługa pływającej masy obliczeniowej nie jest częścią interfejsu.
Nazwy w LTspice nie rozróżniają wielkości liter; poniżej zachowano pisownię kodu.

<!-- BEGIN GENERATED API -->
| Blok | Piny w kolejności wywołania | Parametry domyślne |
|---|---|---|
| `INV` | `out, u, GDN` | `K=1` |
| `ADD2` | `out, a, b, GDN` | `WA=1, WB=1` |
| `ADD2W` | `out, a, b, GDN` | `WA=1, WB=1, SCALE=1` |
| `SUM` | `out, u, d, GDN` | `KU=1, KD=1` |
| `SUMpinv` | `out, a, b, GDN` | `KA=1, KB=1, INVA=0, INVB=0` |
| `SUMp` | `out, a, b, p, GDN` | `VL=10` |
| `MUL` | `out, a, b, GDN` | `VL=10` |
| `MULpinv` | `out, a, b, GDN` | `VL=10, INVA=0, INVB=0` |
| `INT` | `out, u, GDN` | `IC=0, SIGN=-1, LEAK=0` |
| `INTp` | `out, u, GDN` | `IC=0, SIGN=-1, K=1, LEAK=0` |
| `INTpinv` | `out, u, GDN` | `IC=0, K=1, LEAK=0` |
| `INTV` | `out, u, GDN` | `IC=0, SIGN=-1, L=-10, H=10, LEAK=0, TAW=1m` |
| `CMPad` | `out, a, d, GDN` | `TH=0` |
| `CMPda` | `out, a, b, d, GDN` | `brak` |
| `DPT` | `out, u, w, GDN` | `VL=10` |
| `GAIN` | `out, u, GDN` | `K=1` |
| `DIF` | `out, u, GDN` | `K=1, LEAK=0, TAU=0` |
| `LIM` | `out, u, GDN` | `L=0, H=1` |
| `DEADZ` | `out, u, GDN` | `DZ=0.05` |
| `ABS` | `out, u, GDN` | `brak` |
| `SGN` | `out, u, GDN` | `brak` |
| `SCHMITT` | `y, u, GDN` | `CEN=0, HYS=0.2, IC=0, TMEM=10n` |
| `DELAY` | `out, u, GDN` | `T=1m` |
| `LP1` | `out, u, GDN` | `TAU=1m, K=1` |
| `HP1` | `out, u, GDN` | `TAU=1m, K=1` |
| `S_H` | `out, u, i, GDN` | `RON=1, ROFF=1G, CH=100n, IC=0` |
| `CLK` | `out, GDN` | `F=1k, DUTY=0.5, VHI=1, VLO=0, TR=1u, TF=1u` |
| `DAC8` | `y, b7, b6, b5, b4, b3, b2, b1, b0, GDN` | `VL=10` |
| `MUX4` | `y, a, b, c, d, s1, s0, GDN` | `brak` |
| `EDGE_R` | `y, u, GDN` | `TD=1u, TH=0.5` |
| `EDGE_F` | `y, u, GDN` | `TD=1u, TH=0.5` |
| `PWM` | `y, u, GDN` | `F=1k, VL=10` |
| `MONO` | `y, trig, GDN` | `TD=1u, TW=1m, TMEM=10n` |
| `RSTINT` | `y, u, rst, GDN` | `IC=0, SIGN=-1, LEAK=0, TR=1u` |
| `WOBLIN` | `out, GDN` | `VL=10, T=1, IC=0, LEAK=0, TAW=1m` |
<!-- END GENERATED API -->

## Algebra i skala

Napięcia w równaniach są odniesione do `GDN`.
`INV=-K*u`, `GAIN=K*u`, `ADD2=wa*a+wb*b`,
`ADD2W=(wa*a+wb*b)*scale`, `SUM=Ku*u+Kd*d`.
`SUMpinv` nadaje znak każdemu wejściu zgodnie z flagami `inva/invb`
równymi 0 lub 1. `SUMp=a+(p/VL)*b`.

`MUL=a*b/VL`; `MULpinv` dodatkowo odwraca wskazane wejścia.
`DPT=(w/VL)*u`. Parametr `VL>0` jest lokalny: globalne
`.param VL=20` nie zastępuje domyślnego `VL=10` w instancji.
Przekazuj `VL={VL}`, chyba że świadomie stosujesz inną skalę lokalną,
np. `VL=1` dla iloczynu liczb bezwymiarowych.

Przy danych liczbowych zakodowanych jako 1 V na jednostkę iloczyn liczbowy
można uzyskać przez wzmocnienie wyniku `MUL` o `VL`.
Przy reprezentacji pełnoskalowej `v=VL*x_normalized` wynik
`MUL` ma już tę samą skalę; dodatkowe mnożenie przez `VL` byłoby błędem.
Mapowanie jednostek fizycznych należy zatem podać dla każdego modelu.
Pośrednie węzły wzmocnienia mogą przekraczać `VL`; bloki algebraiczne
nie mają ukrytych szyn zasilania ani nasycenia.

## Integratory i rzeczywisty upływ

`INT`: dx/dt = SIGN*u - leak*x, x(0)=IC, out=x.
`INTp`: dx/dt = SIGN*K*u - leak*x.
`INTpinv` odpowiada `INTp` z `SIGN=+1`.
Wartość domyślna `SIGN=-1` dotyczy `INT`, `INTp`, `INTV`, `RSTINT`.
`K` przelicza napięcie wejściowe na szybkość zmiany stanu;
dla reprezentacji napięciowej ma wymiar odwrotności czasu.

`leak>=0` ma jednostkę 1/s. Bez pobudzenia x(t)=IC*exp(-leak*t).
Przy `leak=0` i zerowym wejściu stan jest stały.
Stan jest oddzielony od wyjścia buforem; rezystor przy idealnym wyjściu
nie pełni funkcji upływu pamięci. Inicjalizacja odbywa się przez
`C... IC=...` i lokalne `.ic`, również przy zwykłym `.tran`.

`INTV` realizuje:
```text
y = limit(x,L,H)
dx/dt = SIGN*u - leak*x + (y-x)/Taw
x(0) = limit(IC,L,H)
```
Wymagane są `L<H`, `Taw>0`.
Jest to sprzężenie zwrotne ograniczające narastanie stanu (back-calculation).
Wyjście pozostaje w [L,H], ale wewnętrzny stan może wychodzić poza granice.
Dla stałego dodatniego pobudzenia f i `leak=0` stan po nasyceniu
dąży do H+Taw*f. Opóźnienie powrotu zależy od `Taw`, a nie rośnie
bez ograniczenia wraz z czasem przeciążenia. To nie jest idealny zacisk stanu.

`RSTINT`: przy `rst>0.5` dx/dt=(IC-x)/Tr; przy pozostałych wartościach
dx/dt=SIGN*u-leak*x. Wyjście zawsze odtwarza rzeczywisty stan x.
`Tr>0`; reset trwający co najmniej 20*Tr redukuje wcześniejsze
odchylenie do około 2.1e-9 jego początkowej wartości. Krótszy impuls daje
reset częściowy. Nie ma idealnego, natychmiastowego skoku stanu.

## Filtry, ograniczniki i pamięć analogowa

`LP1`: tau*dx/dt=K*u-x, out=x, x(0)=0.
`HP1`: out=K*u-x, gdzie x jest wyjściem takiego `LP1`.
Dla obu `tau>0`; realizację oparto na obwodzie RC i buforze.

`DIF`: dla `tau=0` out=K*du/dt. Dla `tau>0` transmitancja wynosi
K*s/(tau*s+1), co ogranicza wzmocnienie wysokich częstotliwości.
Parametr `leak` zachowano wyłącznie dla zgodności starych wywołań;
nie wpływa na różniczkowanie i powinien mieć wartość 0.
Do tłumienia należy użyć `tau`, nie `leak`.
Idealne różniczkowanie skoków nie ma skończonej amplitudy.

`LIM=limit(u,L,H)`, `ABS=abs(u)`, `SGN` zwraca -1, 0 lub 1.
`DEADZ` zwraca 0 dla abs(u)<DZ, a poza tym u-DZ*sgn(u);
wymagane `DZ>=0`.
`DELAY` jest opóźnieniem transportowym `T>0`.

`S_H` jest układem śledząco-pamiętającym, nie idealnym próbnikiem
na pojedynczym zboczu. Przy sterowaniu >0.5 klucz śledzi wejście ze
stałą czasową Ron*Ch; po rozwarciu klucza występuje powolne oddziaływanie wejścia
przez Roff, ze stałą czasową Roff*Ch. Wymagane Ron>0, Roff>Ron, Ch>0.
Początkowy stan kondensatora określa `IC`.

## Logika i czasowanie

`CMPad`: 1, gdy a+d>th, w przeciwnym razie 0.
`CMPda`: wybór a dla d>0.5, w pozostałych przypadkach b.
`MUX4`: s1s0=00 wybiera a, 01 wybiera b, 10 wybiera c, 11 wybiera d;
wejścia wyboru są porównywane z 0.5. Nie istnieje blok o nazwie `MUX`.

`DAC8` oczekuje bitów 0/1 i zwraca VL*(128*b7+...+b0)/255.
Nie progowuje wejść: podanie bitów 0/VL wymaga wcześniejszego przeskalowania.
`PWM` porównuje u/VL z trójkątną nośną 0..1; u<=0 daje 0,
u>=VL daje wypełnienie 1 z pominięciem pojedynczych punktów równości.
Wymagane f>0, VL>0.

`CLK`: okres 1/f. Wypełnienie `duty` dotyczy przejść przez połowę
amplitudy; długość płaskiego odcinka wysokiego wynosi duty/f-(tr+tf)/2.
Dla 0<duty<1 wymagane tr>0, tf>0 oraz
(tr+tf)/2 < min(duty,1-duty)/f. Dla duty=0 lub 1 generowana jest stała.
Wymagane f>0 i 0<=duty<=1; wartości spoza zakresu nie są poprawnymi danymi,
nawet jeżeli gałąź implementacji sprowadza je do stałej.

`EDGE_R/F` wykrywają przekroczenie progu `th`, a nie dowolny dodatni
lub ujemny przyrost napięcia. Dla odizolowanych zboczy impuls ma długość Td.
Przejście powrotne przed upływem Td może go skrócić; wymagane Td>0.

`SCHMITT` ma kondensator pamięci oraz progi CEN±HYS/2, HYS>0.
Po przekroczeniu górnego progu stan zbliża się do 1, poniżej dolnego do 0,
a w paśmie histerezy jest podtrzymywany. Wyjście progowane na 0.5 daje 0/1.
IC należy do {0,1}; Tmem>0 określa czas odpowiedzi pamięci.

`MONO` ma jawny stan początkowy 0, detektor zbocza i opóźnione kasowanie.
Dla odizolowanych wyzwoleń długość impulsu wynosi w przybliżeniu Tw.
Wymagane Tw>Td>=20*Tmem>0 oraz odstęp zboczy większy od Tw+Td.
Kasowanie ma pierwszeństwo; zachowanie przy nakładających się wyzwoleniach
nie jest retriggerowalnym monostabilnym wydłużaniem impulsu.

## WOBLIN

Dołącz obie biblioteki. Wymagane VL>0, T>0, leak>=0, Taw>0.
Wartość początkowa jest ograniczana do [0,VL].
Przy leak=0 i IC w tym zakresie:

```text
out(t) = limit(IC + (VL/T)*t,0,VL)
t_sat = T*(1-IC/VL)
```

`T` oznacza czas rampy od 0 do pełnej skali, nie czas od dowolnego IC.
To pojedynczy przebieg z podtrzymaniem ograniczonego wyjścia, bez
automatycznego powrotu i bez okresowego przemiatania częstotliwości.
Przy leak>0 rampa przestaje być liniowa; przed ograniczeniem:
x(t)=IC*exp(-leak*t)+(VL/(T*leak))*(1-exp(-leak*t)).
Może nie osiągnąć górnej granicy.
Pełny przykład: [04_woblin.cir](../examples/04_woblin.cir).
