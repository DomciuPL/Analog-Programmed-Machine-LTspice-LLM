# APM‑1 — RULES & GUIDELINES (RAG) v12‑PL

## 0. DYREKTYWY NADRZĘDNE

### [PRIMARY_DIRECTIVE]

Ten dokument jest **JEDYNYM i OSTATECZNYM** źródłem wiedzy dotyczącej użycia biblioteki `apm1_lib.txt`. Wszelkie odpowiedzi, objaśnienia i przykłady **MUSZĄ** wynikać wyłącznie z zasad, specyfikacji i definicji zawartych w tym pliku RAG.

### [MANDATE]

1. **Paradygmat komputera analogowego:** Całość opisu i implementacji prowadzimy w kontekście komputera analogowego APM‑1.
2. **Specyfikacje z tego pliku:** Piny, parametry i funkcje bloków opisujemy **wyłącznie** według Specyfikacji w **Sekcji 2**.
3. **Zasada skali napięcia maszynowego:** Zawsze wyjaśniamy skalowanie względem napięcia maszynowego `VL=10 V` (Sekcja 1).

### [PROHIBITION]

1. **Zakaz „domyślania” pinów i funkcji bloków z ogólnej wiedzy o LTspice.** Interpretacje bloków APM‑1 wynikają wyłącznie z niniejszego RAG.
2. **Zakaz pomijania pinu masy obliczeniowej `GDN`.** Każda instancja bloku musi mieć `GDN` podłączony do węzła `0`.
3. **Zakaz proponowania zamienników spoza biblioteki**, jeśli dana funkcja istnieje w `apm1_lib.txt`.

---

## 1. KONWENCJE I SKALA MASZYNOWA

### [RULE | Skala VL=10]

Wszystkie zmienne modelujemy w jednostkach bezwymiarowych przy napięciu maszynowym `VL=10 V`.

* `MUL` zwraca (;out = (a\cdot b)/VL;). Jeżeli równanie fizyczne wymaga (a\cdot b), kompensujemy skalę przez `GAIN K={VL}` na jednym z czynników przed mnożeniem.
* Dzielniki, normalizacje i „miękkie bramkowanie” realizujemy przez `DPT` lub `GAIN`.

### [RULE | Jednostki i czytelność]

Stałe i progi definiujemy przez `.param`. Zmienne wejściowe wprowadzamy źródłami `Vx name 0 DC ...` dla deterministycznego punktu pracy.

### [RULE | Notacja]

Nazwy bloków i parametrów: UPPERCASE. Nazwy węzłów: lowercase. Komentarz `*` lub `;`. Konwencje sygnałów: `e` – błąd, `c` – stan, `bc` – produkt `B*C`.

### [RULE | Pętle sprzężenia]

Projekt pętli: sumator błędu → wzmacniacz `GAIN` (tuning (k)) → integrator (`INT`/`INTV`) → ograniczenia (`LIM`/`INTV`) → węzły wyjściowe. Skalowanie w pętli zgodnie z `VL`.

---

## 2. INWENTARZ BLOKÓW I SPECYFIKACJA PINÓW

**Źródło prawdy dla pinów i równań.** Ostatni pin to `GDN` i musi być połączony z węzłem `0`.

| Blok        | Piny (kolejność wiążąca)     | Równanie / Funkcja                                         | Parametry domyślne                           |   |   |
| ----------- | ---------------------------- | ---------------------------------------------------------- | -------------------------------------------- | - | - |
| **INV**     | `out, u, GDN`                | `out = −K*u`                                               | `K=1`                                        |   |   |
| **GAIN**    | `out, u, GDN`                | `out = K*u`                                                | `K=1`                                        |   |   |
| **ADD2**    | `out, a, b, GDN`             | `out = wa*a + wb*b`                                        | `wa=1, wb=1`                                 |   |   |
| **ADD2W**   | `out, a, b, GDN`             | `out = (wa*a + wb*b)*scale`                                | `wa=1, wb=1, scale=1`                        |   |   |
| **SUM**     | `out, u, d, GDN`             | `out = Ku*u + Kd*d`                                        | `Ku=1, Kd=1`                                 |   |   |
| **SUMpinv** | `out, a, b, GDN`             | `out = s_a*Ka*a + s_b*Kb*b`, `s∈{±1}`                      | `Ka=1, Kb=1, inva=0, invb=0`                 |   |   |
| **SUMp**    | `out, a, b, p, GDN`          | `out = a + (p/VL)*b`                                       | `VL=10`                                      |   |   |
| **MUL**     | `out, a, b, GDN`             | `out = (a*b)/VL`                                           | `VL=10`                                      |   |   |
| **MULpinv** | `out, a, b, GDN`             | `out = (s_a*a*s_b*b)/VL`                                   | `VL=10, inva=0, invb=0`                      |   |   |
| **INT**     | `out, u, GDN`                | `out=IC+∫ SIGN*u dt`                                       | `IC=0, SIGN=−1, leak=0`                      |   |   |
| **INTp**    | `out, u, GDN`                | `out=IC+∫ SIGN*K*u dt`                                     | `IC=0, SIGN=−1, K=1, leak=0`                 |   |   |
| **INTpinv** | `out, u, GDN`                | `out=IC+∫ K*u dt`                                          | `IC=0, K=1, leak=0`                          |   |   |
| **INTV**    | `out, u, GDN`                | `out = limit(IC+∫ SIGN*u dt, L, H)`                        | `IC=0, SIGN=−1, L=−10, H=10, leak=0`         |   |   |
| **DIF**     | `out, u, GDN`                | `out = K*du/dt`                                            | `K=1, leak=0`                                |   |   |
| **LIM**     | `out, u, GDN`                | `out = limit(u,L,H)`                                       | `L=0, H=1`                                   |   |   |
| **DEADZ**   | `out, u, GDN`                | martwa strefa `DZ`                                         | `DZ=0.05`                                    |   |   |
| **ABS**     | `out, u, GDN`                | `out =                                                     | u                                            | ` | — |
| **SGN**     | `out, u, GDN`                | `out ∈ {−1,0,1}`                                           | —                                            |   |   |
| **SCHMITT** | `y, u, GDN`                  | histereza (środek `CEN`, szer. `HYS`)                      | `CEN=0, HYS=0.2`                             |   |   |
| **DELAY**   | `out, u, GDN`                | `out(t)=u(t−T)`                                            | `T=1m`                                       |   |   |
| **LP1**     | `out, u, GDN`                | `K/(τs+1)`                                                 | `tau=1m, K=1`                                |   |   |
| **HP1**     | `out, u, GDN`                | `K·τs/(τs+1)`                                              | `tau=1m, K=1`                                |   |   |
| **S_H**     | `out, u, i, GDN`             | sample‑and‑hold ster. `i`                                  | `Ron=1, Roff=1G, Ch=100n`                    |   |   |
| **CLK**     | `out, GDN`                   | `PULSE(vlo,vhi,0,tr,tf,Ton,T)` z **Ton=`duty/f`, T=`1/f`** | `f=1k, duty=0.5, vhi=1, vlo=0, tr=1u, tf=1u` |   |   |
| **DAC8**    | `y, b7…b0, GDN`              | `y=VL*(128*b7+…+b0)/255`                                   | `VL=10`                                      |   |   |
| **MUX4**    | `y, a, b, c, d, s1, s0, GDN` | wybór wejścia wg `s1 s0`                                   | —                                            |   |   |
| **EDGE_R**  | `y, u, GDN`                  | impuls na zboczu narastającym                              | `Td=1u`                                      |   |   |
| **EDGE_F**  | `y, u, GDN`                  | impuls na zboczu opadającym                                | `Td=1u`                                      |   |   |
| **PWM**     | `y, u, GDN`                  | PWM na trójkącie, próg `u/VL`                              | `f=1k, VL=10`                                |   |   |
| **MONO**    | `y, trig, GDN`               | monostabilny impuls `Tw`                                   | `Td=1u, Tw=1m`                               |   |   |
| **DPT**     | `out, u, w, GDN`             | `out=(w/VL)*u`                                             | `VL=10`                                      |   |   |
| **RSTINT**  | `y, u, rst, GDN`             | reset: `rst>0.5 → y=IC`                                    | `IC=0, SIGN=−1, leak=0`                      |   |   |

---

## 3. NUMERYKA I STABILNOŚĆ

### [RULE | Integracja]

Dla pętli stosujemy `method=gear`, `maxord=2`, `trtol≤5`. Okno kroku `maxstep` dostosowujemy do najszybszej stałej czasowej (`≤ τ_min/10`). Precyzja: `reltol≤1e−6`, `abstol=vntol≤1e−9`.

### [RULE | Pakiet opcji minimalny]

```spice
.options method=gear maxord=2 trtol=5 reltol=1e-6 abstol=1e-9 vntol=1e-9
```

### [RULE | Ograniczenia i upływ]

Stany integratorów zabezpieczamy przez `INTV` lub `LIM` oraz mały `leak` w gałęzi stanu. Unikamy „wind‑up”.

### [RULE | Sygnały bliskie zera]

Przy dzieleniu i odwrotności dla `|B|≈0` wprowadzamy blokadę (`SCHMITT`→`MUX4`/`DPT`) i zamrażanie stanu.

### [RULE | Dobór wzmocnienia k]

W pętli `\dot C = k e` dobieramy (k) tak, aby (3τ) mieściły się w pierwszej 1/3 okna pomiarowego `.meas`.

---

## 4. REGUŁY ELEMENTARNE

### 4.1 Sumatory i wzmocnienia

* `SUM` do formowania błędu z dowolnymi znakami składowych; `SUMpinv` preferowane zamiast osobnych `INV`.
* `GAIN` pełni rolę kompensacji skali oraz strojenia pętli; w pętli bezpośrednio przed integratorem.

**Szablon błędu:**

```spice
* e = a − b
XERR e a b 0 SUM Ku=1 Kd=-1
```

### 4.2 Mnożenie i potencjometr sterowany

* `MUL` zwraca `(a*b)/VL`. Dla produktu „fizycznego” dodaj `GAIN K={VL}` przed jednym z czynników.
* `DPT`: `out=(w/VL)*u` — dzielenie przez `VL`, bramkowanie, miękkie ograniczenia.

### 4.3 Całkowanie, różniczkowanie, ograniczniki

* `INT/INTV`: preferuj `INTV` z dopasowanym `L/H` i małym `leak`.
* `DIF`: tylko z tłumieniem wysokich częstotliwości (`leak`/filtr), aby nie wzmacniać szumu numerycznego.
* `LIM/DEADZ/SCHMITT`: w pętlach na gałęzi **stanu**, nie na błędzie.

### 4.4 Czasowanie i logika

`DELAY` do detekcji zboczy, `S_H` z `CLK` dla próbkowania, `PWM` dla modulacji.

---

## 5. OPERACJE ZAAWANSOWANE

### 5.1 Dzielenie (C=A/B) — Reguła kanoniczna

**Wariant bezpośredni:** (e=A−B C), (\dot C=k e). Produkt `B*C` formujemy jako produkt „fizyczny” w pętli: `GAIN K={VL}` na gałęzi `B` + `MUL`. Stan `C` ograniczamy `INTV` i małym `leak`.

**Szablon (bezpośredni):**

```spice
.param VL=10  k=150  leak=1e-3  L=-100  H=100
Va A 0 DC <...>
Vb B 0 DC <...>
XbVL BVL B 0 GAIN K={VL}
XMUL BC  BVL C 0 MUL     ; BC = B*C
XER  E   A   BC 0 SUM Ku=1 Kd=-1
XK   Es  E   0  GAIN K={k}
XC   C   Es  0  INTV SIGN=+1 IC=0 L={L} H={H} leak={leak}
.tran 0 0.3 0 10u
```

**Wariant przez odwrotność:** najpierw (D=1/B) z pętlą (e=1−B D), potem (C=A D). W obu mnożeniach kompensujemy `VL`.

**Szablon (odwrotność):**

```spice
.param VL=10  k=150  leak=1e-3  L=-10  H=10
Va A 0 DC <...>
Vb B 0 DC <...>
V1 ONE 0 DC 1
XbVL BVL B 0 GAIN K={VL}
XBD  BD  BVL D 0 MUL
XER  E   ONE BD 0 SUM Ku=1 Kd=-1
XK   Es  E   0   GAIN K={k}
XD   D   Es  0   INTV SIGN=+1 IC=0 L={L} H={H} leak={leak}
XaVL AVL A   0   GAIN K={VL}
XCD  C   AVL D   0   MUL
.tran 0 0.3 0 10u
```

**Warunki brzegowe:** dla `|B|<B_min` wymagane blokowanie pętli (histereza `SCHMITT` → `MUX4`/`DPT`) lub przełączanie znaku wejścia.

---

## 6. SZABLONY ZŁOŻONE

**Detekcja zbocza i monostabilny:**

```spice
.param Td=1u Tw=1m
XEDG pe  u   0 EDGE_R  Td={Td}
XMON y   pe  0 MONO    Td=1u Tw={Tw}
```

**Filtry I rzędu:**

```spice
.param tau=1m K=1
XLP yLP u 0 LP1 tau={tau} K={K}
XHP yHP u 0 HP1 tau={tau} K={K}
```

**Sample‑and‑Hold z zegarem:**

```spice
.param f=1k duty=0.5
XCLK clk 0 CLK f={f} duty={duty}
XSH  y   u clk 0 S_H
```

---

## 7. PROCEDURY WALIDACYJNE

### [RULE | Blok „RESULTS” — obowiązkowy]

Każdy plik `.cir` kończymy blokiem wyników. Zawiera komendy `.meas` oraz ewentualne uwagi do wykresów XY.

**Szablon:**

```spice
*=== RESULTS_BEGIN ===
.meas tran C_final AVG V(C) FROM=0.2 TO=0.3
; dodatkowe: .meas AT/WHEN, komentarze XY
*=== RESULTS_END ===
```

### [RULE | Test DC]

Poprzedzaj szablony `.op` lub krótkim `.tran` z wejściami stałymi.

### [RULE | Okna pomiarowe]

Średnie `AVG` wykonujemy po co najmniej trzech stałych czasowych układu, zwykle w ostatniej 1/3 przedziału.

### [CHECKLIST | Pre‑run]

1. `[ ]` `.include apm1_lib.txt` na początku pliku.
2. `[ ]` Kompletne listy pinów w każdym `X...`.
3. `[ ]` `GDN` do `0` w każdej instancji.
4. `[ ]` Zdefiniowane `VL` (`.param VL=10`).
5. `[ ]` `.tran` i `.options` obecne, `maxstep` ustawiony.
6. `[ ]` Pomiary `AT/WHEN` tylko dla `time>0`.

---

## 8. PRZYKŁADY KONTROLNE

**Dzielenie A=6, B=3 — wariant bezpośredni:** zawiera `.meas AVG` dla `C` w oknie `FROM/TO`.

**Dzielenie — wariant przez odwrotność:** pomiary `AVG` dla `D` i `C`.

---

## 9. BŁĘDY TYPOWE I KOREKTY

### [RULE | MUL Scale]

Saturacja `±VL` zwykle oznacza brak kompensacji skali przed `MUL`.

### [RULE | Pin Count]

Błąd „number of nodes…” wynika z pominięcia pinu sterującego (`DPT`) lub `GDN`.

### [RULE | Measurement Windows]

Pomiary `AVG` ustawiamy po ustaleniu stanu; krótkie okna dają bias.

### **[RULE | CLK Param Scope] — NOWE**

Nie używaj wewnętrznych `.param T`/`Ton` zależnych od `f` i `duty` w sub‑układzie `CLK`. Obliczaj `T` i `Ton` bezpośrednio w `PULSE(...)` jako `{1/f}` i `{duty/f}`. Zapewnia to przenośność i brak błędów zegara.

## 10. META (dla generowania materiałów)

* Odpowiedzi mają wskazywać nazwy bloków, kolejność pinów i równania z Sekcji 2.
* Każdy fragment netlisty ma zawierać `.param`, `.options`, `.tran` i blok `RESULTS`.
* W interpretacji wyników należy wskazywać `AVG`, `AT`, `FROM/TO` oraz skalowanie względem `VL`.

**Koniec dokumentu RAG v12‑PL**
