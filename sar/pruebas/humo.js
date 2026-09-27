// Prueba de humo (uso: node sar/pruebas/humo.js sar/modelo_sar_coello.js): corre el script con una API de Earth Engine simulada (todo devuelve un
// objeto comodin) para encontrar errores de JavaScript del lado del cliente: funciones
// que no existen, variables sin definir, ramas que se caen. No prueba el calculo real.
const fs = require('fs');
const vm = require('vm');

const archivo = process.argv[2];
const fuente = fs.readFileSync(archivo, 'utf8');

function hacerComodin(registro) {
  let profundidad = 0;
  const handler = {
    get(t, p) {
      if (p === Symbol.toPrimitive) return () => 1;
      if (p === 'then') return undefined;
      if (p === 'toString' || p === 'valueOf') return () => 1;
      return comodin;
    },
    apply(t, self, args) {
      // ejecuta los callbacks que reciba (map, evaluate, onChange, ...)
      if (profundidad < 6) {
        for (const a of args) {
          if (typeof a === 'function') {
            profundidad++;
            try { a(comodin, undefined); } finally { profundidad--; }
          }
        }
      }
      return comodin;
    },
    construct() { return comodin; }
  };
  const comodin = new Proxy(function () {}, handler);
  return comodin;
}

function correr(ajustes, simularPanel) {
  const registro = {prints: [], exports: [], callbacks: []};
  const ee = hacerComodin(registro);
  const selects = [];
  const ui = new Proxy({}, {
    get(t, p) {
      if (p === 'Select') {
        return function (o) {
          const s = {
            _cb: null, _v: o && o.value,
            items() { return {reset() {}}; }, setPlaceholder() {},
            onChange(cb) { this._cb = cb; }, getValue() { return this._v; }
          };
          selects.push(s);
          return s;
        };
      }
      return hacerComodin(registro);
    }
  });
  const ctx = {
    ee, ui,
    Map: hacerComodin(registro),
    print: (...a) => registro.prints.push(a.map(x => (typeof x === 'string' ? x : '<ee>')).join(' ')),
    Export: {table: {toDrive: (o) => registro.exports.push(o)}},
    require: () => hacerComodin(registro),   // modulos de Earth Engine (p. ej. el de Vollrath)
    console
  };
  vm.createContext(ctx);
  let codigo = fuente;
  for (const [k, v] of Object.entries(ajustes)) {
    const re = new RegExp('^var ' + k + '(\\s*)= [^;]+;', 'm');
    if (!re.test(codigo)) throw new Error('no encontre el ajuste ' + k);
    codigo = codigo.replace(re, 'var ' + k + '$1= ' + JSON.stringify(v) + ';');
  }
  vm.runInContext(codigo, ctx, {filename: archivo});
  if (simularPanel) {
    // elegir conjunto y evento como lo haria el usuario
    const [selFuente, selEvento] = selects;
    for (const fu of ['63', 'CTRL', '30']) {
      selFuente._v = fu;
      if (selFuente._cb) selFuente._cb(fu);
      if (selEvento._cb) selEvento._cb(fu === '30' ? 14 : 5);
    }
  }
  return registro;
}

const grupos = ['A', 'B', 'C', 'ROC', 'V12', 'V13', 'V14', 'V15', 'V15C', 'V16', 'V18',
                'SERIE', 'FECHAS', 'MANCHAS', 'SIGNO', 'P51', 'CURV', 'MTF', 'ACIERTO', 'NO_EXISTE'];
let fallos = 0;
for (const g of grupos) {
  for (const fu of ['63', 'CTRL', '30', '70R']) {
    for (const salida of ['CONSOLA', 'DRIVE']) {
      for (const vista of ['SCRIPT', 'VOLLRATH']) {
        const aj = {MODO: 'LOTE', GRUPO: g, FUENTE: fu};
        if (fuente.includes("var SALIDA")) aj.SALIDA = salida;
        if (fuente.includes("var VISTA")) aj.VISTA = vista;
        try {
          const r = correr(aj, false);
          if (salida === 'CONSOLA' && vista === 'SCRIPT')
            console.log(`OK  ${g.padEnd(9)} ${fu.padEnd(4)} prints=${r.prints.length} exports=${r.exports.length} :: ${(r.prints[r.prints.length - 1] || '').slice(0, 70)}`);
          if (salida === 'DRIVE' && vista === 'VOLLRATH' && r.exports.length)
            console.log(`    DRIVE ${g} ${fu}: ${r.exports.map(e => e.description).join(', ')}`);
        } catch (e) {
          fallos++;
          console.log(`FALLA ${g} ${fu} ${salida} ${vista}: ${e.stack.split('\n').slice(0, 3).join(' | ')}`);
        }
        if (!fuente.includes("var VISTA")) break;
      }
      if (!fuente.includes("var SALIDA")) break;
    }
  }
}
try {
  const r = correr({MODO: 'PANEL'}, true);
  console.log('OK  PANEL prints=' + r.prints.length);
} catch (e) {
  fallos++;
  console.log('FALLA PANEL: ' + e.stack.split('\n').slice(0, 4).join(' | '));
}
console.log(fallos ? `\n${fallos} FALLAS` : '\nSIN FALLAS');
