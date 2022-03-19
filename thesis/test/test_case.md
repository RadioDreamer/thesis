# Tesztesetek

## Alapmodell

### Feloldódás tesztelése

- A bomló régió objektumait és belső régióit megörökli-e a szülő
- A legkülső régió nem oldódhat fel (konstruktorban lehetne szűrni)
- Egy belső régió oldódik fel (ilyenkor a benne lévő régiók a feloldó régió szülőjébe kerülnek)
- Egyszerre bomlik két szomszédos régió
- 