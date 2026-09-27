# Nota para el vault (2026-09-27, sesion en la nube sobre el script SAR)

Para la sesion que tiene acceso al `SEGUNDO CEREBRO CLAUDE`. Esta sesion no puede
escribir en el vault; todo lo de abajo esta en la rama `claude/pensive-lamport-1l9reo`
del repositorio `Nievepro/CODIGO-TESIS`, carpeta `sar/`. Sin tildes, como las notas del
wiki. Nada de esto cambia las cifras vigentes: la deteccion con los ajustes por defecto
es la misma.

## 1. Contradiccion abierta: direccion de vista en la correccion por pendiente

Proponer `wiki/questions/Direccion de vista en la correccion por pendiente.md` y un
pendiente nuevo (siguiente ID libre, P60): "Verificar la direccion de vista de la
correccion por pendiente con el GRUPO 'SIGNO'", dueno autor (correr) y agente (leer).

Las dos versiones, las dos del propio trabajo:

| fuente | que usa en cos(direccion - aspecto) | descendente |
|---|---|---|
| [[Geometria del radar en el Coello - resultado negativo]] (P29) | azimut al satelite = rumbo - 90 | 102 grados |
| `DETECTOR SAR/MODELO_SAR.js`, `vista` en `alfaR` (v8 en adelante) | direccion de mirada = rumbo + 90 | 281,97 grados |
| modulo publicado de Vollrath et al. (2020), `slope_correction_lib.js` | aspecto de la banda `angle` | ~102 grados si el aspecto de Earth Engine es la direccion a la que mira la ladera |

Son vectores opuestos, como dice el paquete de contexto, pero justamente por eso no
pueden estar bien los dos en la misma formula: cambiar uno por el otro le cambia el
signo a alfa_r. Si el que falla es el del script, desde la v8 quedan en espejo la
correccion por pendiente, la mascara de layover y sombra, el margen de la v18 y el
angulo local del censo de manchas. Las cifras de la v8 a la v18 siguen siendo
mediciones reales, pero de ese procedimiento, no del de Vollrath.

Segun `wiki/log.md`, la v8 se integro en el script con la direccion medida en la
cuenca, sin `p31_lote.js`; la v11 y la v15 usan la misma reimplementacion. No hay en el
vault ninguna comparacion entre esa reimplementacion y el modulo publicado.

Como se resuelve: el `GRUPO 'SIGNO'` hace dos pruebas independientes (brillo de las
laderas que miran al sensor y comparacion pixel a pixel con el modulo publicado, en
las dos convenciones). Hasta verla, la contradiccion queda abierta; no elegir ganador.

## 2. Correcciones al paquete de contexto

- Prueba ciega, fila 26 (0,135 ha, el mismo poligono que el ID 14): el paquete traia
  `rk fusion = 0.1072`; con ese valor el AUC de la prueba ciega da 0,611 y no 0,625. Con
  0,0376, el valor del ID 14, da exactamente 0,625. Confirmar contra
  `INFORME V15/consola_v15C_30.csv`.
- "v15 con puesto 1-8 = 49 de 63 y 15 de 25" son en realidad los sitios con alguna
  mancha que toca (puesto distinto de -1). Con puesto 1 a 8 son 38 y 5.
- `sar/analisis/metricas.py resumen` reproduce las cifras de la v15 de
  [[Cifras vigentes]] a partir de las tablas: 35 de 63 y 0 de 25, 7 de 18 y 4 de 12,
  kappa 0,415 / 0,051 / 0,395 y AUC 0,728 / 0,625 / 0,724.

## 3. Hallazgo para P51, solo con los 25 controles de ajuste (los 30 no se usan)

Configuracion: v15 de dos carriles. Conjunto: los 25 controles negativos del archivo de
70. Fuente: `sar/analisis/metricas.py tamano` sobre `sar/datos/v15c_ctrl.csv`.

| medida | valor |
|---|---|
| Spearman entre area del control y cercania al top (puesto v15) | 0,49, p = 0,012 (permutacion) |
| controles de 5 ha o mas en los puestos 1 a 8 | 4 de 7 |
| controles de menos de 5 ha en los puestos 1 a 8 | 1 de 18; Fisher p = 0,012 |
| area mediana: controles / eventos | 1,42 / 0,40 ha (maximo 20,28 / 4,07 ha) |

Lectura: el sesgo por tamano ya se ve en el conjunto de ajuste, sin mirar la prueba
ciega. La especificidad esta medida sobre controles mas grandes que los deslizamientos.

## 4. Lo que cambio en el script (rama del repositorio)

- Correcciones sin efecto en la deteccion: todos los grupos leen bien las fuentes `30`
  y `70R`; `DESDE`/`HASTA` valen para todas las fuentes y cada lote imprime sus sitios;
  los atajos de `polz` ya no botan opciones; `MANCHAS` no se cae sin imagenes; un
  `GRUPO` mal escrito avisa; el panel pinta la pendiente minima del modelo (20) y el
  cambio del carril 2; la cobertura disuelve las manchas antes de medir.
- `SALIDA = 'DRIVE'`: el lote queda en un CSV en Drive (carpeta `SAR_COELLO`).
- `VISTA = 'SCRIPT'` (por defecto, la de siempre) o `'VOLLRATH'` (girada 180 grados).
- `GRUPO 'SIGNO'` y `GRUPO 'P51'` (probabilidad de tocar por azar, p0; criterio
  propuesto antes de ver datos: toca y p0 <= 0,05).

## 5. Corridas pendientes, en orden (dueno: autor)

1. `SIGNO`, `FUENTE '63'`, 8 sitios, `VISTA 'SCRIPT'`.
2. Si confirma el giro: `V15C` con `VISTA 'VOLLRATH'` sobre `63` y `CTRL` (un solo
   cambio contra la v15 guardada). La prueba ciega solo si el autor y el director lo
   aprueban: seria su cuarto uso.
3. `P51` sobre `63` y `CTRL` con la `VISTA` que quede.
