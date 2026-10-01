# Detector SAR del Coello

| que | donde |
|---|---|
| Script de Earth Engine (se copia entero al Code Editor) | `modelo_sar_coello.js` |
| Tablas de la v15 guardada (63, 25 controles, prueba ciega) | `datos/` |
| Metricas a partir de la salida del script | `analisis/metricas.py` |
| Pruebas del script sin Earth Engine | `pruebas/` |
| Lo que hay que pasar al vault | `NOTA_PARA_EL_VAULT.md` |

## v24 (2026-10-01): tres pruebas para subir la deteccion

Todo lo que hay que saber para correrlas, analizarlas y guardarlas esta en
`TRASPASO_v24.md` (se le pasa entero al chat que maneja Earth Engine). Copia del script
de esta version: `MODELO_SAR_v24_pruebas.txt`. Con los ajustes por defecto y en el panel
el script hace lo mismo que la v23.

| paso | GRUPO | que prueba | analisis |
|---|---|---|---|
| 1 | `ORDEN` | v24-A: escoger las 4 manchas por masa sobre el umbral (o cambio medio x area) en vez de por area | `metricas.py orden` |
| 2 | `POST90` | v24-B: ventana post de 90 dias | `metricas.py variante --tipo post` |
| 3 | `ESCALON` | v24-C: busqueda del escalon entre FECHA_PRE y FECHA_POS (carril 1) | `metricas.py variante --tipo escalon` |

Cada una con `FUENTE '63'` y `FUENTE 'CTRL'`. La prueba ciega (`'30'`) solo con permiso del autor.

## Corridas pendientes de la revision del 2026-09-27 (ya hechas segun el capitulo de resultados)

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
python3 analisis/metricas.py orden --eventos orden_63.txt --controles orden_ctrl.txt                      # v24-A
python3 analisis/metricas.py variante --eventos post90_63.txt --controles post90_ctrl.txt --tipo post     # v24-B
python3 analisis/metricas.py variante --eventos escalon_63.txt --controles escalon_ctrl.txt --tipo escalon  # v24-C
```

## Pruebas

```
node --check modelo_sar_coello.js
eslint -c pruebas/eslint.config.mjs modelo_sar_coello.js
node pruebas/humo.js modelo_sar_coello.js     # corre todos los grupos y el panel con una API simulada
```

La prueba de humo encuentra errores de JavaScript (funciones o variables que no existen,
ramas que se caen), no errores de Earth Engine: eso solo se ve corriendo en el Code Editor.
