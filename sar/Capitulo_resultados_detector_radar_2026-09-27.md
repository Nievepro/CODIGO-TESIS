# Resultados del detector de deslizamientos con radar (Sentinel-1)

Cuenca del río Coello, 2020–2025. Borrador del capítulo de resultados, 27 de septiembre de 2026.
Todas las cifras salen de corridas guardadas del script `MODELO_SAR_v1` (versiones v1 a v23) y
de sus consolas en `DETECTOR SAR/`. Las citas marcadas "(DOI por verificar)" deben revisarse
contra la revista antes de la entrega.

---

## 1. El detector final: v15 de dos carriles

### 1.1 Cómo funciona

| Parte | Descripción |
|---|---|
| Método base | Cambio de retrodispersión Sentinel-1 GRD entre una ventana antes y una después del evento, con umbral en el percentil 99 (Handwerger et al., 2022), corrido por evento en una caja de 1 km |
| Ventanas | 180 días antes de la fecha pre y 180 días desde la fecha post |
| Carril 1 (v11) | Cambio = mediana pre − mediana post (dB), promedio de VH y VV, con corrección por pendiente y máscara de layover y sombra, pendiente mínima de 20° |
| Carril 2 (fusión) | En cada píxel, el mayor de tres indicadores llevados a la misma escala: el cambio del carril 1, el cambio de VH − VV y la subida de la señal |
| Decisión | En cada carril se marca lo que supera el p99 de la caja y se entregan las 4 manchas más grandes: 8 manchas en total |
| Acierto | Detecta si alguna de las 8 manchas toca el polígono del inventario |
| Datos | Solo radar y DEM (FABDEM). El óptico se usó únicamente para diagnóstico, nunca para decidir |

### 1.2 Desempeño en las tres bases

| Base | Detecta | Falsas alarmas | Sensibilidad | Especificidad | Kappa (IC 95 %) | AUC por evento (IC 95 %) |
|---|---|---|---|---|---|---|
| Inventario 63 + 25 controles | 35 de 63 | 0 de 25 | 55,6 % | 100 % | 0,415 (0,299 a 0,532) | 0,728 (0,618 a 0,826) |
| 45 confirmados del archivo de 70 + 25 controles | 28 de 45 | 0 de 25 | 62,2 % | 100 % | 0,541 (0,406 a 0,688) | 0,777 (0,659 a 0,875) |
| Prueba ciega: 18 deslizamientos + 12 controles | 7 de 18 | 4 de 12 | 38,9 % | 66,7 % | 0,051 (−0,250 a 0,359) | 0,625 (0,398 a 0,819) |
| 63 eventos + 37 controles (25 + 12) | 35 de 63 | 4 de 37 | 55,6 % | 89,2 % | 0,395 (0,236 a 0,537) | 0,724 (0,619 a 0,812) |

**Cómo leer la prueba ciega.** Los 18 deslizamientos de la prueba ciega son eventos del
inventario de 63 (con sus mismos resultados), así que para el radar no son independientes; la
diferencia entre 35 de 63 y 7 de 18 se debe a qué eventos cayeron en ese subconjunto, no a
sobreajuste. Lo único independiente son los **12 controles**, y ahí sí aparece la diferencia:
**4 falsas alarmas de 12**, contra 0 de 25 en los controles de ajuste. Las 4 caen en los 4
controles más grandes (5,7 a 58,3 ha).

### 1.3 Detección por tamaño del deslizamiento (63 eventos)

| Área | Eventos | Detecta la v15 |
|---|---|---|
| < 0,1 ha | 8 | 1 |
| 0,1 a 0,25 ha | 14 | 6 |
| 0,25 a 0,5 ha | 15 | 9 |
| 0,5 a 1 ha | 12 | 8 |
| ≥ 1 ha | 14 | 11 |
| **Total** | **63** | **35** |

El deslizamiento típico de la zona mide 0,197 ha (Santa-Ramírez et al., 2020). Por debajo de
0,25 ha el detector encuentra 7 de 22; por encima, 28 de 41.

## 2. Criterio de acierto: "toca" y "centroide dentro"

"Toca" podría premiar los roces de borde. Se midieron dos criterios más, al lado de "toca" y sin
reemplazarlo, sobre las 8 manchas entregadas:

| Área | Eventos | Toca (puesto 1 a 4) | Intersección / área menor ≥ 0,25 | Centroide dentro (margen 10 m) |
|---|---|---|---|---|
| < 0,1 ha | 8 | 1 | 0 | 1 |
| 0,1 a 0,25 ha | 14 | 6 | 4 | 6 |
| 0,25 a 0,5 ha | 15 | 9 | 7 | 8 |
| 0,5 a 1 ha | 12 | 8 | 8 | 8 |
| ≥ 1 ha | 14 | 11 | 10 | 11 |
| **Total, 63 eventos** | **63** | **35** | **29** | **34** |
| **25 controles** | **25** | **0** | **0** | **0** |

- **34 de los 35 aciertos tienen una mancha centrada dentro del polígono.** El único roce de
  borde es el ID 32. Ningún evento cumple los criterios nuevos sin tocar.
- La mediana de la intersección sobre el área menor en los 35 aciertos es 0,78.
- Ese criterio castiga a los deslizamientos pequeños (pierde 6 aciertos, entre ellos el único
  menor de 0,1 ha); por eso se reporta "centroide dentro" junto a "toca".
- Ninguno de los dos corrige el sesgo de los controles grandes: una mancha pequeña que cae
  entera dentro de un control de 20 ha cuenta igual.

## 3. Línea base de azar (p0)

Para saber cuánto se acertaría por suerte, cada polígono se desplazó a 100 posiciones dentro de
su caja (rejilla de 100 m) y se contó en cuántas tocaba alguna de las 8 manchas entregadas (p0).

| Medida | 63 eventos | 25 controles |
|---|---|---|
| Aciertos esperados por azar (suma de p0) | 6,2 | 5,2 |
| Aciertos observados de la v15 | 35 | 0 |

- El detector toca 35 donde el azar tocaría unos 6. La probabilidad de lograrlo por azar es
  menor de 1 en 10²⁰: **la señal es real**.
- p0 crece con el área del polígono (correlación de 0,88 con el logaritmo del área). Un criterio
  "toca y p0 ≤ 0,05" corrige ese sesgo, pero deja solo 6 de los 35 aciertos, así que no se
  adoptó; p0 queda como línea base de azar para la discusión.
- Los controles de ajuste son más grandes que los deslizamientos (mediana 1,42 contra 0,40 ha).
  Aun en esos 25, los de 5 ha o más quedan a un paso del top: 4 de 7 entre los puestos 1 y 8,
  contra 1 de 18 de los pequeños (Fisher p = 0,012).

## 4. Variantes probadas y descartadas

Regla de parada, fijada antes de las pruebas: un cambio se conserva solo si sube la detección en
los 63 sin que la especificidad baje de 83,8 %. Todas las cifras son sobre los 63 eventos y los
25 controles de ajuste.

| Versión | Idea | Fuente | Detecta (63) | Falsas alarmas (25) | Por qué se descartó |
|---|---|---|---|---|---|
| v1 | Método base: VH, p99, 4 manchas más grandes | Handwerger et al. (2022) | 21 | 2 | Línea base; superada |
| v2, v3 | Contraste contra un anillo de 30 a 150 m | — | 23 | 3 | Gana 4 y pierde 2; McNemar p = 0,69 |
| v4 | Ventana pre de la misma temporada | — | 26 | 3 | La separación sin umbral no mejora (AUC 0,648 → 0,625) |
| v5 | VV en vez de VH | Santangelo et al. (2022) | 23 | 2 | Sola no mejora |
| v6 | Promedio del cambio en VH y VV | Lindsay et al. (2025) | 26 | 2 | Superada por la v8 |
| v7 | Banda L (ALOS-2 PALSAR-2 ScanSAR, 25 m) | — | 10 | 4 | Resolución muy gruesa para deslizamientos de menos de 1 ha |
| v8 | Corrección por pendiente (modelo de volumen) y máscara de layover y sombra | Vollrath et al. (2020) | 29 | 1 | Superada por la v11 |
| v9 | Suavizado, máximo VH/VV, valor absoluto, área × pendiente, p98 | — | 25 a 29 | 1 a 2 | Ninguna supera a la v8 |
| v10 | Ventanas de 365 días | Handwerger et al. (2022) | 31 | 3 | Suben las falsas alarmas |
| v10 | Filtro óptico de NDVI sobre las manchas | — | 32 | 1 | Descartada por decisión del autor: la tesis evalúa solo el radar |
| v11 | v8 con pendiente mínima de 20° | — | 30 | 0 | Carril 1 de la v15 |
| v11 | Caja de 500 m y de 2 km; filtro de Lee por imagen; persistencia del cambio | — | 21 a 32 | 0 a 5 | Bajan la detección o suben las falsas alarmas |
| v12 | Índices de vegetación de radar (VH/VV, RVI, mezcla) | — | 11 a 22 | 1 a 4 | No superan a la v11 |
| v13 | Prueba ómnibus con todas las imágenes | Canty et al. (2020) | 29 | 3 | Rota eventos, no mejora |
| v14 | Detección por objetos (SNIC) | Esposito et al. (2020) | 22 a 29 | 2 a 5 | No supera a la v11 |
| v15 | Prueba t por píxel y fusiones con 4 manchas | Ballinger (2025) (por verificar) | 27 a 30 | 0 a 2 | Ninguna supera a la v11 sola |
| — | v11 con 8 manchas en un solo carril | — | 33 | 4 | Muestra que la ganancia de la v15 no se debe solo a entregar más manchas |
| v18 | Máscaras de geometría con margen de 10° y 20°; pasos por píxel; misma órbita relativa | — | 27 a 34 | — | Pierden deslizamientos reales |
| v19 | Signo de la geometría corregido (dirección de vista girada 180°) | Vollrath et al. (2020) | 34 | 2 | No pasa la regla (ver limitaciones) |
| P51 | Criterio "toca y p0 ≤ 0,05" | — | 6 de los 35 | 0 | Corrige el sesgo por tamaño, pero pierde casi todos los aciertos |
| v20 | Máscara de curvatura (fuera curvatura < −0,005 m⁻¹) | Handwerger et al. (2022) | 31 | 2 | Pierde en 0,1 a 0,25 ha (6 → 3): en el Coello los deslizamientos arrancan en laderas convexas |
| v21 | Filtro multitemporal de speckle | Quegan y Yu (2001); Mullissa et al. (2021) | 34 | 4 | Con 15 a 28 imágenes por ventana (medianas) la mediana ya promedia el speckle |
| v22 | Criterios de acierto (intersección / área menor; centroide dentro) | — | 29 y 34 | 0 | No son variantes del detector: se reportan junto a "toca" (sección 2) |

Detalle de las tres últimas pruebas del detector, contra la v15 (35 de 63 y 0 de 25):

| Medida | v19 signo corregido | v20 curvatura | v21 Quegan-Yu |
|---|---|---|---|
| Detecta (63) | 34 | 31 | 34 |
| Falsas alarmas (25) | 2 | 2 (C23, C25) | 4 (C3, C4, C23, C25) |
| Gana / pierde | 1 / 2 | 1 / 5 | 3 / 4 |
| McNemar exacto | — | p = 0,22 | p = 1,0 |
| Suma de p0 en los 63 (v15: 6,2) | — | 6,0 | 6,4 |
| AUC por evento (v15: 0,728) | — | 0,715 | 0,738 |

## 5. El dibujo del deslizamiento (v16)

La detección entrega manchas; el dibujo las hace crecer hacia los píxeles vecinos con un poco
menos de cambio, sin cambiar la detección. Elegido (DIB16): crecimiento por histéresis hacia el
p95 de la caja, con pendiente ≥ 10°, sobre el cambio suavizado a 15 m, hasta 150 m, y un cierre
final de 1 píxel.

Medido en los 35 eventos detectados, con las manchas que tocan el polígono:

| Dibujo | Parte del polígono cubierta (mediana) | Parte del dibujo que cae dentro (mediana) | IoU mediana | Eventos con IoU ≥ 0,3 |
|---|---|---|---|---|
| Sin crecer (manchas de la v15) | 17 % | 69 % | 0,16 | 10 de 35 |
| **v16 (DIB16)** | **44 %** | **54 %** | **0,29** | **16 de 35** |

La v16 mejora la IoU en 28 eventos y la baja en 6 (prueba de signos p < 0,001). En los mayores
de 1 ha, la IoU mediana pasa de 0,13 a 0,24.

Intentos posteriores de mejorar el dibujo (v23), también descartados:

| Dibujo | Cubierta | Dentro | IoU mediana | IoU ≥ 0,3 | Área dibujada en los 25 controles |
|---|---|---|---|---|---|
| DIB16 (referencia) | 0,435 | 0,538 | 0,287 | 16 | 49,0 ha |
| D1: crecer solo ladera arriba o abajo | 0,417 | 0,541 | 0,278 | 15 | 24,0 ha |
| D1 + D4: además, apertura de 1 píxel | 0,324 | 0,568 | 0,236 | 14 | 21,2 ha |

D1 casi no cambia el dibujo de los deslizamientos (21 de 35 iguales; IoU: 9 mejoran, 5
empeoran, p = 0,42), aunque dibuja la mitad de área en los controles. D1 + D4 sube la parte que
cae dentro (26 contra 6, p = 0,001) pero baja la cubierta en 21 eventos. El dibujo final sigue
siendo la v16.

## 6. Limitaciones

### 6.1 Tamaño frente a resolución

El píxel de Sentinel-1 GRD es de 10 m, pero la resolución real en modo IW es de unos 20 m. Un
deslizamiento de 0,1 ha tiene apenas unos 10 píxeles y muy pocos independientes. En la
literatura se reconoce que los deslizamientos muy pequeños son difíciles de ver con Sentinel-1
(Mondini et al., 2021; Handwerger et al., 2022). En el Coello, justamente el tamaño típico
(0,197 ha) es donde el detector pierde más. Además, 14 de los 28 no detectados no tienen ninguna
mancha encima con ninguna variante: ahí el límite es la señal, no la regla.

### 6.2 Fechas del inventario

Con un diagnóstico óptico (solo para revisar, no dentro del detector):

| Grupo | Eventos | Detecta la v15 |
|---|---|---|
| Fecha coherente | 38 | 25 (66 %) |
| Aparece en parte antes de la fecha pre | 8 | 5 |
| Ya se ve en la ventana pre | 8 | 4 |
| Sin huella óptica después | 9 | 1 |

Una baja del NDVI antes de la fecha pre puede ser un precursor superficial, y las fechas del
inventario corresponden al evento completo; por eso se trata como incertidumbre de la ventana y
no como error del inventario. La ventana es la misma para todos los eventos: no se ajustó
mirando el polígono.

### 6.3 Signo de la geometría

La corrección por pendiente del script usa como dirección de vista el rumbo + 90°, que apunta en
sentido contrario al que usa el modelo de Vollrath et al. (2020). Una prueba de brillo lo
confirmó: las laderas que el script toma como "de espaldas" al sensor son las más brillantes, es
decir, las que están de frente. Por eso, de la v8 en adelante la corrección es el espejo de la
publicada. Con el signo corregido, la v15 da 34 de 63 y 2 de 25, así que no pasa la regla de
parada y se dejó la versión original. En la tesis se debe decir que la corrección por pendiente
usada es **empírica y no la física publicada**, y que su beneficio se midió, no se derivó.

### 6.4 Número de pruebas sobre los mismos 63

Se probaron más de 45 variantes sobre los mismos 63 eventos y 25 controles. Con tantas pruebas,
una mejora de 1 o 2 eventos puede ser azar, y los valores p no están corregidos por
comparaciones múltiples. Ninguna mejora posterior a la v11 fue significativa por sí sola (la v15
frente a la v11: McNemar p = 0,063). La única evidencia independiente son los 12 controles de la
prueba ciega, y allí la especificidad cae a 66,7 %. Una confirmación real de la detección
requiere deslizamientos nuevos, fuera de los 63.

### 6.5 Lo que queda fuera del alcance con GRD

La coherencia interferométrica y las descomposiciones polarimétricas necesitan datos SLC, que no
están en Google Earth Engine. Con 63 eventos tampoco se puede entrenar un modelo de aprendizaje
profundo.

## Referencias

- Canty, M. J., Nielsen, A. A., Conradsen, K. y Skriver, H. (2020). *Remote Sensing*, 12(1), 46. (DOI por verificar)
- Esposito, G. et al. (2020). *Natural Hazards and Earth System Sciences*, 20, 2379–2395. (DOI por verificar)
- Handwerger, A. L., Huang, M.-H., Jones, S. Y., Amatya, P., Kerner, H. R. y Kirschbaum, D. B. (2022). Generating landslide density heatmaps for rapid detection using open-access satellite radar data in Google Earth Engine. *Natural Hazards and Earth System Sciences*, 22, 753–773. https://doi.org/10.5194/nhess-22-753-2022
- Lindsay, E., Ganerød, A. J., Devoli, G., Reiche, J., Nordal, S. y Frauenfelder, R. (2025). Understanding landslide expression in SAR backscatter data: Global study and disaster response application. *Remote Sensing*, 17(19), 3313. https://doi.org/10.3390/rs17193313
- Mondini, A. C., Guzzetti, F., Chang, K.-T., Monserrat, O., Martha, T. R. y Manconi, A. (2021). Landslide failures detection and mapping using Synthetic Aperture Radar: Past, present and future. *Earth-Science Reviews*, 216, 103574. https://doi.org/10.1016/j.earscirev.2021.103574
- Mullissa, A., Vollrath, A., Odongo-Braun, C., Slagter, B., Balling, J., Gou, Y. et al. (2021). Sentinel-1 SAR backscatter analysis ready data preparation in Google Earth Engine. *Remote Sensing*, 13(10), 1954. https://doi.org/10.3390/rs13101954
- Quegan, S. y Yu, J. J. (2001). Filtering of multichannel SAR images. *IEEE Transactions on Geoscience and Remote Sensing*, 39(11), 2373–2379. https://doi.org/10.1109/36.964973
- Santa-Ramírez, Cuevas-González, Leal-Villamil y Muñoz-Ramos (2020). *Ingeniería y Ciencia*, 16(31), 145–168. https://doi.org/10.17230/ingciencia.16.31.7
- Santangelo, M., Cardinali, M., Bucci, F., Fiorucci, F. y Mondini, A. C. (2022). Exploring event landslide mapping using Sentinel-1 SAR backscatter products. *Geomorphology*, 397, 108021. https://doi.org/10.1016/j.geomorph.2021.108021
- Vollrath, A., Mullissa, A. y Reiche, J. (2020). Angular-based radiometric slope correction for Sentinel-1 on Google Earth Engine. *Remote Sensing*, 12(11), 1867. (DOI por verificar; página de la revista: mdpi.com/2072-4292/12/11/1867)
- Ballinger (2025), prueba t por píxel (PWTT), *Remote Sensing of Environment*: **por verificar** (autores completos, volumen y DOI).
