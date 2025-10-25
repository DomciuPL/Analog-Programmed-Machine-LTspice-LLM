# APM-1 — RULES & GUIDELINES (RAG) v12-PL

## 0. DYREKTYWY NADRZĘDNE

### [PRIMARY_DIRECTIVE]
Niniejszy plik jest jedynym i ostatecznym źródłem prawdy dla użytkowania biblioteki `apm1_lib.txt`. Wszystkie odpowiedzi, przykłady i interpretacje muszą wynikać wyłącznie z zasad i specyfikacji zawartych w tym dokumencie.

### [MANDATE]
1. Kontekst obliczeń: komputer analogowy APM-1, skala napięcia maszynowego `VL`.
2. Źródło prawdy dla pinów i równań: **Sekcja 2**.
3. Spójność biblioteki: brak zduplikowanych sekcji `.subckt … .ends` oraz unikalne nazwy elementów wewnętrznych w każdym subukładzie.

### [PROHIBITION]
1. Zakaz „domyślania” pinów z ogólnej wiedzy o LTspice. Obowiązuje inwentarz z Sekcji 2.
2. Zakaz pomijania pinu `GDN` i niedołączania go do węzła `0`.
3. Zakaz proponowania zamienników spoza biblioteki, jeśli funkcja istnieje w `apm1_lib.txt`.

---

## 1. KONWENCJE I SKALA MASZYNOWA

### [RULE | VL=10]
Zmienne reprezentujemy w skali bezwymiarowej przy `VL=10 V`. Mnożnik `MUL` zwraca `out=(a*b)/VL`; dla produktu „fizycznego” kompensujemy skalę przez `GAIN K={VL}` na jednym z czynników przed mnożeniem. `DPT` realizuje `out=(w/VL)*u`.

### [RULE | Notacja i sygnały]
Nazwy bloków i parametrów piszemy wielkimi literami. Nazwy węzłów małymi. Komentarz `*` lub `;`. W pętlach: sumator błędu → `GAIN` (strojenie k) → integrator (`INT`/`INTV`) → ograniczenie (`LIM`/`INTV`) → wyjście, wszystko w skali `VL`.

### [RULE | Opcje symulacji]
Dla pętli zalecamy Gear, rząd 2, `reltol≤1e−6`, `abstol=vntol≤1e−9`. Ustaw `maxstep` ≤ `τ_min/10`.

---

## 2. INWENTARZ BLOKÓW I SPECYFIKACJA PINÓW
**Źródło prawdy dla pinów i równań.** Ostatni pin to `GDN` i musi być połączony z `0`.

| Blok        | Piny (kolejność wiążąca)     | Równanie / Funkcja                      | Parametry domyślne                    |
|-------------|-------------------------------|-----------------------------------------|---------------------------------------|
| **INV**     | `out, u, GDN`                | `out = −K*u`                            | `K=1`                                 |
| **GAIN**    | `out, u, GDN`                | `out = K*u`                             | `K=1`                                 |
| **ADD2**    | `out, a, b, GDN`             | `out = wa*a + wb*b`                     | `wa=1, wb=1`                          |
| **ADD2W**   | `out, a, b, GDN`             | `out = (wa*a + wb*b)*scale`             | `wa=1, wb=1, scale=1`                 |
| **SUM**     | `out, u, d, GDN`             | `out = Ku*u + Kd*d`                     | `Ku=1, Kd=1`                          |
| **SUMpinv** | `out, a, b, GDN`             | `s∈{±1}`: `out = s_a*Ka*a + s_b*Kb*b`   | `Ka=1, Kb=1, inva=0, invb=0`          |
| **SUMp**    | `out, a, b, p, GDN`          | `out = a + (p/VL)*b`                    | `VL=10`                               |
| **MUL**     | `out, a, b, GDN`             | `out = (a*b)/VL`                        | `VL=10`                               |
| **MULpinv** | `out, a, b, GDN`             | `s∈{±1}`: `out = (s_a*a*s_b*b)/VL`      | `VL=10, inva=0, invb=0`               |
| **INT**     | `out, u, GDN`                | `out = IC + ∫ SIGN*u dt`                | `IC=0, SIGN=−1, leak=0`               |
| **INTp**    | `out, u, GDN`                | `out = IC + ∫ SIGN*K*u dt`              | `IC=0, SIGN=−1, K=1, leak=0`          |
| **INTpinv** | `out, u, GDN`                | `out = IC + ∫ K*u dt`                   | `IC=0, K=1, leak=0`                   |
| **INTV**    | `out, u, GDN`                | `out = limit(IC+∫ SIGN*u,L,H)`          | `IC=0, SIGN=−1, L=−10, H=10, leak=0`  |
| **DIF**     | `out, u, GDN`                | `out = K*du/dt`                         | `K=1, leak=0`                         |
| **LIM**     | `out, u, GDN`                | `out = limit(u,L,H)`                    | `L=0, H=1`                            |
| **DEADZ**   | `out, u, GDN`                | martwa strefa `DZ`                      | `DZ=0.05`                             |
| **ABS**     | `out, u, GDN`                | `out = |u|`                             | —                                     |
| **SGN**     | `out, u, GDN`                | `out ∈ {−1,0,1}`                        | —                                     |
| **SCHMITT** | `y, u, GDN`                  | histereza (`CEN`, `HYS`)                | `CEN=0, HYS=0.2`                      |
| **DELAY**   | `out, u, GDN`                | `out(t)=u(t−T)`                         | `T=1m`                                |
| **LP1**     | `out, u, GDN`                | `K/(τs+1)`                              | `tau=1m, K=1`                         |
| **HP1**     | `out, u, GDN`                | `K·τs/(τs+1)`                           | `tau=1m, K=1`                         |
| **S_H**     | `out, u, i, GDN`             | sample-and-hold sterowany `i`           | `Ron=1, Roff=1G, Ch=100n`             |
| **CLK**     | `out, GDN`                   | `PULSE(..., Ton, T)`                    | `f=1k, duty=0.5, vhi=1, vlo=0, tr=tf=1u` |
| **DAC8**    | `y, b7…b0, GDN`              | `y=VL*(128*b7+…+b0)/255`                | `VL=10`                                |
| **MUX4**    | `y, a, b, c, d, s1, s0, GDN` | multiplekser 4:1                        | —                                     |
| **EDGE_R**  | `y, u, GDN`                  | impuls na zboczu narastającym           | `Td=1u`                               |
| **EDGE_F**  | `y, u, GDN`                  | impuls na zboczu opadającym             | `Td=1u`                               |
| **PWM**     | `y, u, GDN`                  | PWM na trójkącie, próg `u/VL`           | `f=1k, VL=10`                         |
| **MONO**    | `y, trig, GDN`               | monostabilny impuls `Tw`                 | `Td=1u, Tw=1m`                        |
| **RSTINT**  | `y, u, rst, GDN`             | reset: `rst>0.5 → y=IC`                 | `IC=0, SIGN=−1, leak=0`               |

---

## 3. NUMERYKA I STABILNOŚĆ

### [RULE | Integracja]
Pętle sprzężenia rozwiązujemy metodą Gear, rząd 2. Tolerancje jak w Sekcji 1. `maxstep` dopasowany do najszybszej stałej czasowej układu.

### [RULE | Pakiet opcji minimalny]
```spice
.options method=gear maxord=2 trtol=5 reltol=1e-6 abstol=1e-9 vntol=1e-9
```
Zestaw zgodny z testami kontrolnymi i przykładami.

### [RULE | Ograniczenia i upływ]
Stany integratorów zabezpieczamy przez `INTV` lub `LIM` oraz mały `leak` w gałęzi stanu przeciw „wind-up”.

### [RULE | Sygnały bliskie zera]
Dla dzielenia i odwrotności przy `|B|≈0` stosujemy blokadę pętli (`SCHMITT`→`MUX4`/`DPT`) i zamrażanie stanu.

---

## 4. REGUŁY ELEMENTARNE

### 4.1 Sumatory i wzmocnienia
`SUM` do formowania błędu; `SUMpinv` preferowany nad łańcuchem `INV`. `GAIN` służy do kompensacji skali oraz strojenia pętli bezpośrednio przed integratorem.

**Szablon błędu:**
```spice
* e = a − b
XERR e a b 0 SUM Ku=1 Kd=-1
```

### 4.2 Mnożenie i potencjometr sterowany
`MUL` zwraca `(a*b)/VL`; dla produktu „fizycznego” poprzedź jeden czynnik `GAIN K={VL}`. `DPT`: `out=(w/VL)*u`.

### 4.3 Całkowanie, różniczkowanie, ograniczniki
Preferuj `INTV` z dopasowanym `L/H` i małym `leak`. `DIF` używaj z tłumieniem HF (`leak` lub filtr), aby nie wzmacniać szumu numerycznego. `LIM/DEADZ/SCHMITT` umieszczaj na gałęzi **stanu**, nie błędu.

### 4.4 Czasowanie i logika
`DELAY` do detekcji zboczy, `S_H` z `CLK` dla próbkowania, `PWM` dla modulacji. Zegar `CLK` definiujemy jako `PULSE({vlo} {vhi} 0 {tr} {tf} {duty/f} {1/f})`.

---

## 5. OPERACJE ZAAWANSOWANE

### 5.1 Dzielenie (C=A/B) — reguła kanoniczna
**Wariant bezpośredni:** `e=A−B*C`, `\dot C=k e`. Produkt `B*C` traktujemy jako produkt „fizyczny”: `GAIN K={VL}` na gałęzi `B` + `MUL`. Stan `C` ograniczamy `INTV` z małym `leak`.

**Szablon:**
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

**Wariant przez odwrotność:** najpierw `D=1/B` z pętlą `e=1−B*D`, potem `C=A*D`. Oba mnożenia z kompensacją `VL`.

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

**Sample-and-Hold z zegarem:**
```spice
.param f=1k duty=0.5
XCLK clk 0 CLK f={f} duty={duty}
XSH  y   u clk 0 S_H
```
Szablony zgodne z definicjami bloków w bibliotece.

---

## 7. PROCEDURY WALIDACYJNE

### [RULE | Blok „RESULTS” — obowiązkowy]
Każdy plik `.cir` kończymy blokiem z `*.meas*` oraz uwagami do wykresów XY.

**Szablon:**
```spice
*=== RESULTS_BEGIN ===
.meas tran C_final AVG V(C) FROM=0.2 TO=0.3
; dodatkowe: .meas AT/WHEN, komentarze XY
*=== RESULTS_END ===
```

### [RULE | Test DC]
Dla układów statycznych poprzedź `.op` krótkim `.tran` z wejściami stałymi.

### [RULE | Okna pomiarowe]
Średnie `AVG` licz po ≥3 stałych czasowych, zwykle w ostatniej 1/3 przedziału czasowego.

### [CHECKLIST | Pre-run]
1. `[ ]` `.include apm1_lib.txt` na początku.  
2. `[ ]` Kompletne listy pinów w każdym `X...`.  
3. `[ ]` `GDN` do `0` w każdej instancji.  
4. `[ ]` Zdefiniowane `VL` (`.param VL=10`).  
5. `[ ]` `.tran` i `.options` obecne; `maxstep` ustawiony.  
6. `[ ]` Pomiary `AT/WHEN` tylko dla `time>0`.

---

## 8. BŁĘDY TYPOWE I KOREKTY

### [RULE | Duplicate Instances]
Jeśli LTspice zgłasza „Instance with that name already defined”, usuń nazwy typu `B1`, `Rle` i zastąp je formą `B_<BLOK>*`, `R_<BLOK>*`. Sprawdź brak wielokrotnych definicji tego samego `.subckt`.

### [RULE | Pin Count]
„Number of nodes does not match pins” wynika zwykle z pominięcia pinu sterującego (`DPT`) lub `GDN`. Zweryfikuj listy pinów według Sekcji 2.

### [RULE | MUL Scale]
Saturacja `±VL` po mnożeniu oznacza brak kompensacji skali przed `MUL`. Zastosuj `GAIN K={VL}`.

### **[RULE | CLK Param Scope]**
W `CLK` nie definiuj wewnętrznych `.param` zależnych od `f` i `duty`. Użyj `PULSE({vlo} {vhi} 0 {tr} {tf} {duty/f} {1/f})` bezpośrednio. Zapewnia to przenośność i brak błędów czasowania.

---

## 9. REGUŁY DOT. NAZEWNICTWA WEWNĘTRZNEGO

### [RULE | Prefiksy instancji]
Wewnątrz subukładów stosuj prefiksy: `B_<BLOK>` dla źródeł behawioralnych, `R_<BLOK>` dla rezystorów upływu, `G_<BLOK>` dla przewodności upływu, `V_<BLOK>` dla źródeł napięcia. Nazwy muszą być unikalne w skali **całej** biblioteki.

### [RULE | Rezystor upływu]
Każdy subukład powinien zawierać jeden rezystor upływu `R_<BLOK> out GDN 1G` lub równoważny mechanizm.

---

## 10. META (dla generowania materiałów)
Odpowiedzi muszą wskazywać nazwy bloków, kolejność pinów i równania z Sekcji 2; każdy przykład `.cir` zawiera `.param`, `.options`, `.tran` i blok `RESULTS`. W interpretacji wyników należy używać `AVG`, `AT`, `FROM/TO` oraz odnosić się do skalowania względem `VL`.

**Koniec dokumentu RAG v12-PL**
