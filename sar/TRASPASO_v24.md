# Traspaso v24 — tres pruebas para subir la detección del detector radar

Preparado el 1 de octubre de 2026 en una sesión de Claude Code (nube, sin acceso a Earth Engine
ni al vault). Este documento es para el chat que maneja el Code Editor de Earth Engine y el
segundo cerebro. Se le pasa **entero**.

---

## 0. Mensaje para pegar en el otro chat

> Sigamos con la tesis, **BITÁCORA RADAR**. Reabro el detector radar (estaba congelado desde el
> 29 de septiembre) para probar tres ideas nuevas, la v24. Te paso el archivo
> `TRASPASO_v24.md` con todo: qué cambia en el script, las hipótesis escritas antes de correr,
> las corridas en orden, cómo analizarlas y qué guardar en el vault.
>
> El script nuevo es `MODELO_SAR_v24_pruebas.txt` (lo dejé en `CODIGO TESIS/DETECTOR SAR/`).
> Cárgalo en el Code Editor **sin guardar** encima de `MODELO_SAR_v1`. Verifica el hash.
> Corre primero el GRUPO `ORDEN` sobre los 63 y los 25 controles, y revisa que el orden por
> área repita la v15 guardada antes de seguir. Después `POST90` y `ESCALON`.
>
> Devuélveme cada salida en un txt con el nombre de la tabla de la sección 4. Al terminar,
> restaura el editor. **No corras la prueba ciega (FUENTE `'30'`) sin preguntarme.**

---

## 1. Contexto en cinco líneas

| Qué | Valor |
|---|---|
| Detector de base | v15 de dos carriles + dibujo v16. Script `users/fernandofariasrodri/Shapes:MODELO_SAR_v1` |
| Cifras de base (63 eventos + 25 controles) | 35 de 63 detectados, 0 de 25 falsas alarmas (de `wiki/Cifras vigentes.md`; verificar ahí) |
| Regla de parada | Un cambio se conserva solo si sube la detección en los 63 y la especificidad en los 25 no baja de 83,8 % |
| Protocolo | Un cambio a la vez, hipótesis escrita antes, línea base de azar (p0) al lado, los negativos también se escriben |
| Por qué se reabre | El autor lo pidió el 2026-10-01 ("necesito mejorarlo"). Se registra en la Bitácora |

## 2. De dónde salen las tres pruebas

Con la tabla guardada de la v15 (`sar/datos/v15c_63.csv`) se miró dónde se pierden los 28
eventos no detectados:

| Grupo | Eventos | Qué pasa |
|---|---|---|
| Hay una mancha que toca el polígono, pero queda en el puesto 5 a 38 de su carril | **14** (IDs 1, 2, 4, 7, 9, 10, 21, 22, 31, 53, 55, 59, 60, 63) | Pierden porque se escogen las 4 manchas **más grandes**, y otras de la caja son más grandes |
| Ninguna mancha toca el polígono | 14 | El radar no ve el cambio (tamaño, fechas o sitio sin huella) |

En los 25 controles pasa lo mismo: 15 tienen una mancha que toca y no entra. Por eso:

- **Entregar más manchas no sirve.** Con los puestos 1 a 8 entran 3 eventos (IDs 9, 31 y 63) y
  5 controles (C2, C3, C22, C23 y C25), y la especificidad baja a 80 %.
- **El margen está en cómo se ordenan las manchas** (prueba A).
- **Las fechas son el otro frente** (pruebas B y C): según el diagnóstico óptico, en 16 eventos el
  deslizamiento ya se veía antes o en la ventana pre.

Techo realista: aun ordenando perfecto, no pasa de unos 49 de 63. Lo esperable es ganar pocos
eventos, no llegar a 80 %.

## 3. Qué cambia en el script (v24)

**Con los ajustes por defecto y en el panel, el script hace exactamente lo mismo que la v23.**
Solo se agregaron tres grupos de lote y dos opciones internas.

| Cambio | Dónde | Efecto con valores por defecto |
|---|---|---|
| Encabezado v24 con las tres hipótesis | líneas 307 a 350 | ninguno (comentario) |
| `V24_POST = 90` y `ESC_N = 4` | ajustes, junto a `MTF_LADO` | ninguno |
| `cambio(...)` y `s1c(...)` aceptan una ventana pre distinta (`vPx`) | dentro de `modelo` | ninguno: sin `vPx` usan la de siempre |
| `escalon()` y `opc.escalon` en el carril 1 (`VHVVc`) | dentro de `modelo` | ninguno: solo se activa en el GRUPO `ESCALON` |
| `modelo` devuelve `esc` (corte ganador por píxel) | retorno de `modelo` | `null` sin `opc.escalon` |
| GRUPOS `ORDEN`, `POST90`, `ESCALON` (y `conMasa`, `carrilOrden`) | después del GRUPO `ACIERTO` | solo corren con `MODO = 'LOTE'` y ese `GRUPO` |

### Verificación antes de correr

| Comprobación | Valor esperado |
|---|---|
| Líneas | 2.073 |
| SHA-256 del archivo | `5570bd8736799ae477825b6ab34d71a397f1c65855cd77c3efe1cb6dff06d44f` |
| SHA-256 sin el salto de línea final (lo que suele dar `getValue()` del editor) | `e3bb05d2d2462a1c3157564754b05e956d60eb178032fb6b766925950e86ba01` |

Para sacar el hash del texto cargado en el editor (consola del navegador):

```js
const t = document.querySelector('.ace_editor').env.editor.getValue();
crypto.subtle.digest('SHA-256', new TextEncoder().encode(t))
  .then(b => console.log([...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join('')));
```

Si no coincide ninguno de los dos, no correr: comparar contra el archivo y avisar.

Pruebas que ya pasó en la nube (sin Earth Engine):

- `node --check`: sin errores;
- `eslint`: sin errores;
- prueba de humo (`pruebas/humo.js`): todos los grupos con las 4 fuentes, consola y Drive, y el panel, sin fallas.

Los errores propios de Earth Engine solo aparecen al correr en el Code Editor.

## 4. Las tres pruebas (hipótesis escritas antes de correr)

### v24-A — GRUPO `ORDEN`: cómo se escogen las 4 manchas de cada carril

Las manchas y el umbral p99 son los de la v15. Solo cambia la propiedad con que se escogen
las 4 de cada carril:

| Orden | Qué es | Papel |
|---|---|---|
| `a` | área (la v15) | control: **debe repetir los puestos guardados** |
| `masa` | (cambio medio − umbral del carril) × área. Es la "masa" de un grupo de píxeles sobre el umbral (Bullmore et al., 1999; Maris y Oostenveld, 2007) | **hipótesis principal** |
| `s` | cambio medio × área (la v3 lo usó con el contraste local, nunca con estas manchas) | secundaria |

- **Hipótesis.** Una cicatriz fresca es una mancha compacta con cambio fuerte. Un cultivo o un
  cambio de temporada es una mancha grande con cambio apenas sobre el umbral. Ordenar por masa
  sube a los 14 eventos que hoy pierden por área sin subir a los controles grandes.
- **Riesgo escrito antes.** Los controles grandes (5 a 20 ha) también pueden tener manchas con
  mucha masa; entonces suben las falsas alarmas.
- **Nota.** El AUC por evento no cambia, porque `rk` no depende del orden.
- **Costo.** Es la corrida más barata en radar (los mismos dos modelos de la v15), pero calcula
  p0 tres veces.

### v24-B — GRUPO `POST90`: ventana post de 90 días

La pre sigue en 180 días; los dos carriles usan la post de 90.

- **Hipótesis.** En el Coello la cicatriz se revegeta en meses, y la mediana de 180 días mezcla
  la cicatriz con el rebrote. Lindsay et al. (2025) detectan con la primera imagen después del
  evento.
- **Riesgo escrito antes.** Con la mitad de imágenes post (hoy la mediana es 15) sube el
  moteado y, con él, las falsas alarmas.
- **Lo que ya se sabe.** Solo se había probado alargar (365 días, v10), nunca acortar.

### v24-C — GRUPO `ESCALON`: buscar el momento del cambio dentro del intervalo del inventario

Solo en el carril 1; el carril 2 no cambia.

- **Cómo funciona.**
  - Además del corte de siempre (pre hasta `FECHA_PRE`, post desde `FECHA_POS`), se prueban 4
    fechas de corte repartidas por igual entre `FECHA_PRE` y `FECHA_POS`.
  - Es la misma regla para todos los eventos y no mira el polígono.
  - En cada corte: pre = 180 días antes y post = 180 días después.
  - Cada mapa se lleva a la escala de la caja; en cada píxel gana el mayor.
  - Con solo el corte de siempre, el resultado sería idéntico a la v11.
- **Idea de base.** Burrows et al. (2022): la serie de amplitud de Sentinel-1 marca cuándo
  ocurrió el cambio.
- **Hipótesis.** Suben los eventos cuya fecha real queda lejos de los bordes del intervalo: la
  cicatriz ya revegetada en la ventana post, o una caída justo después de la fecha pre.
- **Riesgo escrito antes.** Tomar el mayor de cinco mapas infla el ruido y las falsas alarmas.
- **Diagnóstico.** `k` = qué corte ganó en el píxel más alto del polígono (0 = el de siempre).
  Si los eventos que gana tienen `k = 0`, la ganancia no vino de la fecha.
- **Costo.** Es la corrida más pesada (cinco cortes en el carril 1).

## 5. Las corridas, en orden

En los ajustes de arriba del script: `MODO = 'LOTE'`, `VISTA = 'SCRIPT'` (la de siempre) y el
`GRUPO`, `FUENTE`, `DESDE` y `HASTA` de la tabla.

- **Tramos.** Si la consola se queda sin tiempo, partir en tramos más chicos o usar
  `SALIDA = 'DRIVE'` (el CSV queda en Drive, carpeta `SAR_COELLO`; se le da Run en Tasks).
- **Posiciones.** `DESDE` y `HASTA` son posiciones, no IDs. En los 63, `DESDE = 16` empieza en
  el ID 17.

| Paso | GRUPO | FUENTE | Tramos sugeridos (DESDE/HASTA) | Archivo que se devuelve |
|---|---|---|---|---|
| 1 | `ORDEN` | `'63'` | 0/16, 16/32, 32/48, 48/99 | `orden_63.txt` (todos los tramos pegados) |
| 2 | `ORDEN` | `'CTRL'` | 0/13, 13/99 | `orden_ctrl.txt` |
| — | **Control** | — | — | Con `metricas.py orden`, el orden `a` debe REPETIR la v15 guardada. Si no repite, parar y avisar |
| 3 | `POST90` | `'63'` | 0/16, 16/32, 32/48, 48/99 | `post90_63.txt` |
| 4 | `POST90` | `'CTRL'` | 0/13, 13/99 | `post90_ctrl.txt` |
| 5 | `ESCALON` | `'63'` | 0/8, 8/16 … 56/99 (8 por tramo) | `escalon_63.txt` |
| 6 | `ESCALON` | `'CTRL'` | 0/8, 8/16, 16/99 | `escalon_ctrl.txt` |

**Formato de cada fila** (separador de filas `;`, de columnas `,`):

| GRUPO | Columnas |
|---|---|
| `ORDEN` (16) | índice, ha, rk v11, rk fusión; y para `a`, `s` y `masa`: puesto v11, puesto fusión, puesto v15, p0 v15 |
| `POST90` (10) | índice, ha, puesto v11, puesto fusión, puesto v15, rk v11, rk fusión, p0 v15, imágenes pre, imágenes post |
| `ESCALON` (10) | índice, ha, puesto v11, puesto fusión, puesto v15, rk v11, rk fusión, p0 v15, días entre fechas, k |

Detecta = puesto v15 entre 1 y 4. Un puesto de −1 significa que ninguna mancha toca.

**Para copiar la consola** (como en las corridas anteriores):

1. Leer `document.body.textContent` después del título que imprime el grupo.
2. Pegar cada tramo seguido en el mismo txt; el analizador ignora títulos y encabezados.
3. Los errores del script salen dentro de un shadow DOM ("Line N: ...").

## 6. Cómo analizar

En la carpeta `sar/` del repositorio (o con una copia de `analisis/metricas.py` y `datos/`):

```bash
python3 analisis/metricas.py orden    --eventos orden_63.txt   --controles orden_ctrl.txt
python3 analisis/metricas.py variante --eventos post90_63.txt  --controles post90_ctrl.txt  --tipo post
python3 analisis/metricas.py variante --eventos escalon_63.txt --controles escalon_ctrl.txt --tipo escalon
```

Cada uno imprime, contra la v15:

- detección por tamaño;
- falsas alarmas y especificidad;
- eventos que gana y que pierde;
- McNemar exacto;
- falsas alarmas nuevas;
- suma de p0 (aciertos esperados por azar);
- AUC por evento;
- el veredicto de la regla de parada.

Extras por grupo:

| Grupo | Qué agrega |
|---|---|
| `orden` | Primero verifica que el orden `a` repita la v15 guardada |
| `escalon` | Cuántos aciertos vienen de un corte intermedio (`k` > 0) |

Si el otro chat no puede correr Python, que devuelva los txt y se analizan en la sesión de
Claude Code.

## 7. Cómo decidir

| Resultado | Qué hacer |
|---|---|
| No pasa la regla de parada | Se descarta. Se escribe igual: es un hallazgo negativo del capítulo |
| Pasa la regla, pero la suma de p0 sube tanto como los aciertos | No es mejora real: entregar más área sube el azar. Se descarta y se explica |
| Pasa la regla y la suma de p0 no sube | Candidata. **Antes de adoptarla**, pedir permiso al autor para correr el mismo GRUPO con `FUENTE '30'`: los 12 controles independientes son la única prueba que no se usó para escoger. Hoy la v15 tiene 4 de 12 falsas alarmas; la candidata no debe tener más |
| Pasan dos pruebas | No combinarlas sin una corrida nueva con las dos juntas (otra hipótesis escrita antes) |

**Advertencia para el capítulo.** Con estas, van cerca de 50 variantes sobre los mismos 63.
- Se prueban 4 cosas a la vez (masa, s, post 90 y escalón), así que una ganancia de 1 o 2
  eventos puede ser azar.
- Ninguna mejora posterior a la v11 fue significativa por sí sola.
- Si alguna gana, se reporta como exploratoria hasta confirmarla con deslizamientos nuevos (P52).

## 8. Qué guardar en el vault

Con las reglas de siempre: una cifra en una sola nota, sin tildes en `wiki/`, sin `transaction apply`.

| Nota | Qué va |
|---|---|
| `wiki/concepts/Bitacora del detector radar.md` | v24-A, B y C con hipótesis, configuración, conjunto, resultado, ganados y perdidos, p0, AUC, y si pasó o no la regla. También los negativos |
| `DETECTOR SAR/Capitulo_resultados_...` (archivo **nuevo**, no sobrescribir) | Tres filas más en la tabla de variantes descartadas, o la sección nueva si alguna pasa |
| `wiki/Cifras vigentes.md` | **Solo** si una variante se adopta después de la prueba ciega; la vieja pasa a "superadas" |
| `wiki/Pendientes.md` | Un ID nuevo (el siguiente libre después del último que exista; no reciclar) para "v24: correr ORDEN, POST90 y ESCALON", dueño autor (correr) y agente (analizar) |
| `wiki/log.md` y `wiki/hot.md` | La entrada del día: el autor reabrió el detector y qué salió |
| `source-ledger.json` y `Mapa de datos` | Los txt de las corridas si se guardan en `datos/` |

**Referencias nuevas** (verificar volumen, páginas y DOI contra la revista antes de la entrega):

- Ballinger, O. (2025). Open access battle damage detection via Pixel-Wise T-Test on Sentinel-1
  imagery. *Remote Sensing of Environment*, 331, 115025. https://doi.org/10.1016/j.rse.2025.115025.
  Completa la cita "por verificar" del capítulo.
- Bullmore, E. T., Suckling, J., Overmeyer, S., Rabe-Hesketh, S., Taylor, E. y Brammer, M. J.
  (1999). Global, voxel, and cluster tests, by theory and permutation, for a difference between
  two groups of structural MR images of the brain. *IEEE Transactions on Medical Imaging*, 18(1),
  32–42. (DOI por verificar)
- Maris, E. y Oostenveld, R. (2007). Nonparametric statistical testing of EEG- and MEG-data.
  *Journal of Neuroscience Methods*, 164(1), 177–190. (DOI por verificar)
- Burrows, K. et al. (2020). A systematic exploration of satellite radar coherence methods for
  rapid landslide detection. *Natural Hazards and Earth System Sciences*, 20, 3197–. (autores y
  páginas por verificar)
- Burrows, K. et al. (2022). Using Sentinel-1 radar amplitude time series to constrain the
  timings of individual landslides: a step towards understanding the controls on
  monsoon-triggered landsliding. *Natural Hazards and Earth System Sciences*, 22, 2637–. (autores
  y páginas por verificar)
- Lindsay et al. (2025), *Remote Sensing* 17(19):3313: ya está en el capítulo.

## 9. Lo que se investigó y no se prueba (para la discusión)

| Idea | Por qué no |
|---|---|
| Coherencia interferométrica (InSAR) | Necesita datos SLC, que no están en Earth Engine. Burrows et al. (2020) hallan que en zonas con vegetación la coherencia de banda C rinde menos que la amplitud. Los productos de ASF HyP3 salen a 40–80 m, muy grueso para 0,2 ha |
| NISAR (banda L) | Datos públicos solo desde junio de 2026, fuera del periodo 2020–2025 |
| Aprendizaje profundo (redes, "Neural CFAR") | 63 eventos no alcanzan para entrenar. El CFAR clásico (contra un anillo) ya se probó en la v2 y la v3 |
| Corrección de terreno física (RTC por área) con productos de ASF | Habría que procesar fuera de GEE y subir assets. Queda como trabajo futuro, junto a la nota de que la corrección actual es empírica (sección 6.3 del capítulo) |
| Castigar manchas muy grandes | El umbral de área saldría de mirar los 63 (el mayor mide 4,07 ha): sería ajustar con los datos de prueba |
| Filtro óptico de NDVI sobre las manchas | Ya se probó (v10: 32 de 63, 1 de 25), pero rompe la regla "solo radar". Solo si el autor y el director deciden un detector híbrido aparte |
| Enlaces de divulgación revisados (Doppler para drones, radar meteorológico, blogs de radar automotriz) | No aplican a Sentinel-1 GRD ni a deslizamientos |

## 10. Dónde está todo

Repositorio `Nievepro/CODIGO-TESIS`, rama `claude/tender-goodall-du61qc`, carpeta `sar/`:

| Archivo | Qué es |
|---|---|
| `modelo_sar_coello.js` | Script v24 (se copia entero al Code Editor) |
| `MODELO_SAR_v24_pruebas.txt` | Copia idéntica, para guardarla en `DETECTOR SAR/` con nombre nuevo |
| `analisis/metricas.py` | Análisis; comandos nuevos `orden`, `variante --tipo post` y `variante --tipo escalon` |
| `datos/v15c_63.csv`, `datos/v15c_ctrl.csv` | La v15 guardada, base de comparación |
| `TRASPASO_v24.md` | Este documento |
