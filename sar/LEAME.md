# Detector SAR del Coello

| que | donde |
|---|---|
| Script de Earth Engine (se copia entero al Code Editor) | `modelo_sar_coello.js` |
| Tablas de la v15 guardada (63, 25 controles, prueba ciega) | `datos/` |
| Metricas a partir de la salida del script | `analisis/metricas.py` |
| Pruebas del script sin Earth Engine | `pruebas/` |
| Lo que hay que pasar al vault | `NOTA_PARA_EL_VAULT.md` |

## Corridas pendientes, en orden

Cada una: poner los ajustes arriba del script, correr y copiar la consola, o con
`SALIDA = 'DRIVE'` darle Run a la tarea en la pestana Tasks (el CSV queda en la carpeta
`SAR_COELLO` de Drive).

| paso | GRUPO | FUENTE | DESDE / HASTA | VISTA | para que |
|---|---|---|---|---|---|
| 1 | `SIGNO` | `'63'` | 0 / 8 | `'SCRIPT'` | saber si alfa_r esta al reves |
| 2 | `V15C` | `'63'` y luego `'CTRL'` | 0 / 99 | `'VOLLRATH'` | solo si el paso 1 confirma el giro: la v15 corregida contra la guardada |
| 3 | `P51` | `'63'` y luego `'CTRL'` | 0 / 99 | la que quede | criterio de acierto que no premie poligonos grandes |

`P51` es la corrida mas pesada: si la consola se queda sin tiempo, usar `SALIDA = 'DRIVE'`.

## Analisis

```
python3 analisis/metricas.py resumen                      # reproduce la v15 guardada
python3 analisis/metricas.py signo  salida_signo.csv
python3 analisis/metricas.py comparar --antes datos/v15c_63.csv --despues nueva_63.csv \
        --antes-ctrl datos/v15c_ctrl.csv --despues-ctrl nueva_ctrl.csv
python3 analisis/metricas.py p51 --eventos p51_63.csv --controles p51_ctrl.csv
python3 analisis/metricas.py tamano                       # sesgo por tamano en los controles
```

## Pruebas

```
node --check modelo_sar_coello.js
eslint -c pruebas/eslint.config.mjs modelo_sar_coello.js
node pruebas/humo.js modelo_sar_coello.js     # corre todos los grupos y el panel con una API simulada
```

La prueba de humo encuentra errores de JavaScript (funciones o variables que no existen,
ramas que se caen), no errores de Earth Engine: eso solo se ve corriendo en el Code Editor.
