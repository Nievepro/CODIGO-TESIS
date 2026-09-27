#!/usr/bin/env python3
"""Metricas del detector SAR del Coello a partir de la salida del script de Earth Engine.

Lee la salida tal como sale: el texto de la consola (filas separadas por ';'), el CSV
que deja SALIDA = 'DRIVE' (columna 'fila') o los CSV con encabezado de sar/datos/.
Solo usa la libreria estandar de Python.

  python3 metricas.py resumen                      # v15 guardada: reproduce el informe
  python3 metricas.py resumen --eventos A --controles B [--ciega C]
  python3 metricas.py comparar --antes A --despues B [--antes-ctrl C --despues-ctrl D]
  python3 metricas.py tamano                       # sesgo por tamano en los 25 controles
  python3 metricas.py signo ARCHIVO                # salida del GRUPO 'SIGNO'
  python3 metricas.py p51 --eventos A --controles B [--ciega C]   # salida del GRUPO 'P51'

Detecta = puesto entre 1 y TOP_N (4). AUC por evento con el puntaje -min(rk v11, rk
fusion), rk = -1 cuenta como 1 (el peor). Intervalos: Wilson para proporciones y
bootstrap estratificado (2000 repeticiones, semilla fija) para kappa y AUC.
"""
import argparse
import math
import os
import random
import statistics

TOP_N = 4
AQUI = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(AQUI, '..', 'datos')
SEMILLA = 20260927
REPS = 2000


# ------------------------------------------------------------------ lectura
def leer_filas(ruta, ncol):
    """Filas con ncol campos numericos; lo demas (titulos, encabezados) se ignora."""
    with open(ruta, encoding='utf-8') as fh:
        texto = fh.read()
    filas = []
    for linea in texto.splitlines():
        for trozo in linea.strip().strip('"').split(';'):
            campos = [c.strip().strip('"') for c in trozo.split(',')]
            if len(campos) != ncol:
                continue
            try:
                filas.append([float(c) for c in campos])
            except ValueError:
                continue
    if not filas:
        raise SystemExit('No encontre filas de %d columnas en %s' % (ncol, ruta))
    return filas


def leer_v15c(ruta):
    cols = ['indice', 'ha', 'p11', 'pfus', 'p15', 'rk11', 'rkfus']
    return [dict(zip(cols, f)) for f in leer_filas(ruta, 7)]


def partir_ciega(filas):
    """Prueba ciega: indices 0 a 11 son controles y 12 a 29 deslizamientos."""
    return [r for r in filas if r['indice'] >= 12], [r for r in filas if r['indice'] < 12]


# ------------------------------------------------------------------ estadistica
def detecta(p):
    return 1 <= p <= TOP_N


def wilson(k, n, z=1.96):
    if n == 0:
        return float('nan'), float('nan')
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - m), min(1.0, c + m)


def kappa(tp, fn, fp, tn):
    n = tp + fn + fp + tn
    po = (tp + tn) / n
    pe = ((tp + fp) / n) * ((tp + fn) / n) + ((fn + tn) / n) * ((fp + tn) / n)
    return 0.0 if pe == 1 else (po - pe) / (1 - pe)


def auc(pos, neg):
    if not pos or not neg:
        return float('nan')
    s = sum(1.0 if p > q else (0.5 if p == q else 0.0) for p in pos for q in neg)
    return s / (len(pos) * len(neg))


def puntaje(r):
    rk = [1.0 if x < 0 else x for x in (r['rk11'], r['rkfus'])]
    return -min(rk)


def bootstrap(estad, grupos, reps=REPS, semilla=SEMILLA):
    """IC 95 % percentil; remuestrea cada grupo por separado (eventos y controles)."""
    rnd = random.Random(semilla)
    vals = []
    for _ in range(reps):
        muestra = [[g[rnd.randrange(len(g))] for _ in g] for g in grupos]
        v = estad(*muestra)
        if not math.isnan(v):
            vals.append(v)
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]


def binom_dos_colas(k, n):
    """Prueba exacta de signo (McNemar exacto) con p = 0,5."""
    if n == 0:
        return 1.0
    k = min(k, n - k)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def fisher(a, b, c, d):
    """Fisher exacto de dos colas para [[a, b], [c, d]]."""
    n1, n2, m1 = a + b, c + d, a + c
    n = n1 + n2

    def prob(x):
        return math.comb(n1, x) * math.comb(n2, m1 - x) / math.comb(n, m1)
    p_obs = prob(a)
    lo, hi = max(0, m1 - n2), min(n1, m1)
    return min(1.0, sum(prob(x) for x in range(lo, hi + 1) if prob(x) <= p_obs * (1 + 1e-9)))


def rangos(x):
    orden = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(orden):
        j = i
        while j + 1 < len(orden) and x[orden[j + 1]] == x[orden[i]]:
            j += 1
        for k in range(i, j + 1):
            r[orden[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x, y, reps=5000, semilla=SEMILLA):
    def rho(a, b):
        ra, rb = rangos(a), rangos(b)
        ma, mb = statistics.mean(ra), statistics.mean(rb)
        num = sum((p - ma) * (q - mb) for p, q in zip(ra, rb))
        den = math.sqrt(sum((p - ma) ** 2 for p in ra) * sum((q - mb) ** 2 for q in rb))
        return num / den if den else 0.0
    obs = rho(x, y)
    rnd = random.Random(semilla)
    yy = list(y)
    extremos = 0
    for _ in range(reps):
        rnd.shuffle(yy)
        if abs(rho(x, yy)) >= abs(obs) - 1e-12:
            extremos += 1
    return obs, (extremos + 1) / (reps + 1)


def pct(x):
    return ('%.1f %%' % (100 * x)).replace('.', ',')


def num(x, d=3):
    return ('%.*f' % (d, x)).replace('.', ',')


# ------------------------------------------------------------------ comandos
def fila_resumen(nombre, ev, ct, clave):
    tp = sum(detecta(r[clave]) for r in ev)
    fp = sum(detecta(r[clave]) for r in ct)
    fn, tn = len(ev) - tp, len(ct) - fp
    s_lo, s_hi = wilson(tp, len(ev))
    e_lo, e_hi = wilson(tn, len(ct))
    k = kappa(tp, fn, fp, tn)

    def k_est(e, c):
        a = sum(detecta(r[clave]) for r in e)
        b = sum(detecta(r[clave]) for r in c)
        return kappa(a, len(e) - a, b, len(c) - b)
    k_lo, k_hi = bootstrap(k_est, [ev, ct])
    print('| %s | %d de %d | %d de %d | %s (%s a %s) | %s (%s a %s) | %s (%s a %s) |' % (
        nombre, tp, len(ev), fp, len(ct), pct(tp / len(ev)), pct(s_lo), pct(s_hi),
        pct(tn / len(ct)), pct(e_lo), pct(e_hi), num(k), num(k_lo), num(k_hi)))


def cmd_resumen(a):
    conjuntos = []
    ev = leer_v15c(a.eventos or os.path.join(DATOS, 'v15c_63.csv'))
    ct = leer_v15c(a.controles or os.path.join(DATOS, 'v15c_ctrl.csv'))
    conjuntos.append(('63 + 25', ev, ct))
    ruta_ciega = a.ciega or (None if (a.eventos or a.controles) else os.path.join(DATOS, 'v15c_30.csv'))
    if ruta_ciega:
        ev30, ct30 = partir_ciega(leer_v15c(ruta_ciega))
        conjuntos.append(('prueba ciega 18 + 12', ev30, ct30))
        conjuntos.append(('63 + 37 controles', ev, ct + ct30))
    for nombre, e, c in conjuntos:
        print('\n## %s\n' % nombre)
        print('| carril | eventos | falsas alarmas | sensibilidad (IC 95 %) | especificidad (IC 95 %) | kappa (IC 95 %) |')
        print('|---|---|---|---|---|---|')
        fila_resumen('v11', e, c, 'p11')
        fila_resumen('fusion', e, c, 'pfus')
        fila_resumen('**v15**', e, c, 'p15')
        ar = auc([puntaje(r) for r in e], [puntaje(r) for r in c])
        lo, hi = bootstrap(lambda x, y: auc([puntaje(r) for r in x], [puntaje(r) for r in y]), [e, c])
        print('\nAUC por evento de la v15: %s (IC 95 %% %s a %s)' % (num(ar), num(lo), num(hi)))


def cmd_comparar(a):
    antes = {int(r['indice']): r for r in leer_v15c(a.antes)}
    despues = {int(r['indice']): r for r in leer_v15c(a.despues)}
    comunes = sorted(set(antes) & set(despues))
    if len(comunes) < len(antes) or len(comunes) < len(despues):
        print('Ojo: solo %d sitios estan en los dos archivos.' % len(comunes))

    def contar(tabla_a, tabla_b, ids, etiqueta):
        for clave, nombre in (('p11', 'v11'), ('pfus', 'fusion'), ('p15', 'v15')):
            gana = [i for i in ids if not detecta(tabla_a[i][clave]) and detecta(tabla_b[i][clave])]
            pierde = [i for i in ids if detecta(tabla_a[i][clave]) and not detecta(tabla_b[i][clave])]
            na = sum(detecta(tabla_a[i][clave]) for i in ids)
            nb = sum(detecta(tabla_b[i][clave]) for i in ids)
            print('| %s | %s | %d -> %d | %s | %s | %s |' % (
                etiqueta, nombre, na, nb, ', '.join(map(str, gana)) or '-',
                ', '.join(map(str, pierde)) or '-', num(binom_dos_colas(len(gana), len(gana) + len(pierde)))))
    print('| conjunto | carril | detecta antes -> despues | gana | pierde | McNemar p |')
    print('|---|---|---|---|---|---|')
    contar(antes, despues, comunes, 'eventos')
    if a.antes_ctrl and a.despues_ctrl:
        ca = {int(r['indice']): r for r in leer_v15c(a.antes_ctrl)}
        cd = {int(r['indice']): r for r in leer_v15c(a.despues_ctrl)}
        cc = sorted(set(ca) & set(cd))
        contar(ca, cd, cc, 'controles (falsas alarmas)')
        ev_a, ev_d = [antes[i] for i in comunes], [despues[i] for i in comunes]
        ct_a, ct_d = [ca[i] for i in cc], [cd[i] for i in cc]
        auc_a = auc([puntaje(r) for r in ev_a], [puntaje(r) for r in ct_a])
        auc_d = auc([puntaje(r) for r in ev_d], [puntaje(r) for r in ct_d])
        # bootstrap pareado: los mismos sitios en las dos corridas
        pares_e, pares_c = list(zip(ev_a, ev_d)), list(zip(ct_a, ct_d))

        def dif(pe, pc):
            return (auc([puntaje(d) for _, d in pe], [puntaje(d) for _, d in pc])
                    - auc([puntaje(x) for x, _ in pe], [puntaje(x) for x, _ in pc]))
        lo, hi = bootstrap(dif, [pares_e, pares_c])
        print('\nAUC por evento v15: %s -> %s; diferencia %s (IC 95 %% %s a %s)' % (
            num(auc_a), num(auc_d), num(auc_d - auc_a), num(lo), num(hi)))


def cmd_tamano(a):
    """Sesgo por tamano, solo con los 25 controles de ajuste (los 30 no se usan aqui)."""
    ct = leer_v15c(a.controles or os.path.join(DATOS, 'v15c_ctrl.csv'))
    ha = [r['ha'] for r in ct]
    mejor = [r['p15'] if r['p15'] > 0 else 99 for r in ct]   # 99 = ninguna mancha toca
    rho, p = spearman(ha, [-m for m in mejor])
    print('25 controles de ajuste: Spearman entre area y cercania al top (puesto v15) = %s, p = %s' % (
        num(rho, 2), num(p)))
    print('\n| control | ha | puesto v15 |')
    print('|---|---|---|')
    for r in sorted(ct, key=lambda r: -r['ha']):
        print('| C%d | %s | %s |' % (r['indice'], num(r['ha'], 2), int(r['p15']) if r['p15'] > 0 else 'ninguna toca'))
    grandes = [r for r in ct if r['ha'] >= 5]
    chicos = [r for r in ct if r['ha'] < 5]
    cerca = lambda g: sum(1 <= r['p15'] <= 8 for r in g)
    print('\nPuesto 1 a 8 (a un paso de ser falsa alarma): %d de %d controles de 5 ha o mas, %d de %d de menos '
          'de 5 ha; Fisher p = %s' % (cerca(grandes), len(grandes), cerca(chicos), len(chicos),
                                      num(fisher(cerca(grandes), len(grandes) - cerca(grandes),
                                                 cerca(chicos), len(chicos) - cerca(chicos)))))
    ev = leer_v15c(a.eventos or os.path.join(DATOS, 'v15c_63.csv'))
    print('Eventos: mediana %s ha, maximo %s ha; controles: mediana %s ha, maximo %s ha' % (
        num(statistics.median([r['ha'] for r in ev]), 2), num(max(r['ha'] for r in ev), 2),
        num(statistics.median(ha), 2), num(max(ha), 2)))


def cmd_signo(a):
    filas = leer_filas(a.archivo, 19)
    nombres = ['rumbo', 'vvMas', 'vvMenos', 'nMas', 'nMenos', 'difUso', 'acuUso', 'difGir', 'acuGir']
    print('Salida del GRUPO SIGNO: %d sitios. -99 = sin dato.\n' % len(filas))
    print('| paso | sitios | rumbo mediano | VV+ < VV- | dif. con el modulo (uso / girada) | acuerdo de mascara (uso / girada) |')
    print('|---|---|---|---|---|---|')
    for k, paso in enumerate(('ASCENDING', 'DESCENDING')):
        d = [dict(zip(nombres, f[1 + 9 * k: 10 + 9 * k])) for f in filas]
        d = [x for x in d if x['rumbo'] != -99]
        if not d:
            print('| %s | 0 | - | - | - | - |' % paso)
            continue
        brillo = [x for x in d if x['vvMas'] != -99 and x['vvMenos'] != -99]
        inv = sum(x['vvMas'] < x['vvMenos'] for x in brillo)
        med = lambda c: statistics.median([x[c] for x in d if x[c] != -99] or [float('nan')])
        print('| %s | %d | %s | %d de %d | %s / %s dB | %s / %s |' % (
            paso, len(d), num(med('rumbo'), 1), inv, len(brillo), num(med('difUso'), 2), num(med('difGir'), 2),
            num(med('acuUso'), 3), num(med('acuGir'), 3)))
    print('\nLectura: si VV+ < VV- en casi todos y la columna "girada" coincide con el modulo '
          '(diferencia cerca de 0, acuerdo cerca de 1), alfa_r esta al reves con la VISTA usada.')


def cmd_p51(a):
    cols = ['indice', 'ha', 'p11', 'p0_11', 'p15', 'p0_15', 'cob8', 'ent8']

    def leer(ruta):
        return [dict(zip(cols, f)) for f in leer_filas(ruta, 8)]
    conjuntos = [('63 + 25', leer(a.eventos), leer(a.controles))]
    if a.ciega:
        ci = leer(a.ciega)
        conjuntos.append(('prueba ciega 18 + 12', [r for r in ci if r['indice'] >= 12],
                          [r for r in ci if r['indice'] < 12]))
    alfa = a.alfa
    for nombre, ev, ct in conjuntos:
        print('\n## %s  (criterio fijado antes: toca y p0 <= %s)\n' % (nombre, num(alfa, 2)))
        print('| carril | conjunto | toca (regla de siempre) | esperado por azar (suma de p0) | exceso sobre el azar | '
              'toca y p0 <= %s | toca y cobertura >= 1 %% |' % num(alfa, 2))
        print('|---|---|---|---|---|---|---|')
        for carril, pk, p0k in (('v11', 'p11', 'p0_11'), ('v15', 'p15', 'p0_15')):
            for etiqueta, g in (('eventos', ev), ('controles', ct)):
                toca = sum(detecta(r[pk]) for r in g)
                esp = sum(r[p0k] for r in g)
                exceso = (toca - esp) / (len(g) - esp) if len(g) > esp else float('nan')
                crit = sum(detecta(r[pk]) and r[p0k] <= alfa for r in g)
                cob = sum(detecta(r[pk]) and r['cob8'] >= 0.01 for r in g) if carril == 'v15' else None
                print('| %s | %s | %d de %d | %s | %s | %d de %d | %s |' % (
                    carril, etiqueta, toca, len(g), num(esp, 1), pct(exceso), crit, len(g),
                    '%d de %d' % (cob, len(g)) if cob is not None else '-'))
        print('\nMediana de p0 (v15): eventos %s, controles %s' % (
            num(statistics.median([r['p0_15'] for r in ev])), num(statistics.median([r['p0_15'] for r in ct]))))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('resumen')
    r.add_argument('--eventos')
    r.add_argument('--controles')
    r.add_argument('--ciega')
    c = sub.add_parser('comparar')
    c.add_argument('--antes', required=True)
    c.add_argument('--despues', required=True)
    c.add_argument('--antes-ctrl')
    c.add_argument('--despues-ctrl')
    t = sub.add_parser('tamano')
    t.add_argument('--eventos')
    t.add_argument('--controles')
    s = sub.add_parser('signo')
    s.add_argument('archivo')
    p = sub.add_parser('p51')
    p.add_argument('--eventos', required=True)
    p.add_argument('--controles', required=True)
    p.add_argument('--ciega')
    p.add_argument('--alfa', type=float, default=0.05)
    a = ap.parse_args()
    {'resumen': cmd_resumen, 'comparar': cmd_comparar, 'tamano': cmd_tamano,
     'signo': cmd_signo, 'p51': cmd_p51}[a.cmd](a)


if __name__ == '__main__':
    main()
