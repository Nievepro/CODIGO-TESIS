// Linter para el script de Earth Engine: marca nombres sin definir (errores de copia).
// Uso, desde sar/: eslint -c pruebas/eslint.config.mjs modelo_sar_coello.js
export default [{
  files: ["**/*.js"],
  languageOptions: {
    ecmaVersion: 5, sourceType: "script",
    globals: { ee: "readonly", ui: "readonly", Map: "writable", print: "readonly", Export: "readonly",
               require: "readonly", JSON: "readonly", Math: "readonly", Number: "readonly", String: "readonly" }
  },
  rules: { "no-undef": "error", "no-unused-vars": ["warn", {vars: "local", args: "none"}],
           "no-redeclare": "warn", "no-dupe-keys": "error", "no-unreachable": "error" }
}];
