# Datos de la v15 (GRUPO 'V15C')

Salida de consola de la corrida `V15C` del 2026-09-27, copiada del paquete de contexto
que armo la sesion que tiene acceso al vault. Los CSV originales estan en
`CODIGO TESIS/INFORME V15/consola_v15C_63.csv`, `consola_v15C_controles.csv` y
`consola_v15C_30.csv`.

| archivo | sitios | que son |
|---|---|---|
| `v15c_63.csv` | 63 | inventario (ID 1 a 63) |
| `v15c_ctrl.csv` | 25 | controles negativos del archivo de 70 (C2 a C26) |
| `v15c_30.csv` | 30 | prueba ciega: indices 0 a 11 controles, 12 a 29 deslizamientos |

Columnas: `indice, ha, puesto_v11, puesto_fusion, puesto_v15, rk_v11, rk_fusion`.
`-1` en un puesto = ninguna mancha de ese carril toca el poligono; `-1` en rk = el
poligono no tiene pixel valido. Detecta = puesto entre 1 y 4.

## Comprobacion contra las cifras del vault

`python3 ../analisis/metricas.py resumen` reproduce las cifras publicadas en
`wiki/Cifras vigentes.md`: 35 de 63 y 0 de 25; 7 de 18 y 4 de 12 en la prueba ciega;
kappa 0,415 y 0,051; AUC por evento 0,728 (63 + 25), 0,625 (30) y 0,724 (63 + 37),
con el puntaje `-min(rk v11, rk fusion)`.

## Una correccion de copia

En el paquete, la fila 26 de la prueba ciega venia con `rk_fusion = 0.1072` (el mismo
valor de `rk_v11`). Es el mismo poligono que el ID 14 de los 63 (0,135 ha, iguales
puestos y rk v11), donde `rk_fusion = 0.0376`. Con 0,1072 el AUC de la prueba ciega
da 0,611; con 0,0376 da 0,625, que es la cifra del informe. Se dejo 0,0376.
Confirmarlo contra `consola_v15C_30.csv`.

El paquete tambien decia "v15 con puesto 1-8 = 49" en los 63 y 15 en los controles:
esos numeros son en realidad los sitios con alguna mancha que toca (puesto distinto
de -1). Con puesto 1 a 8 son 38 y 5.
