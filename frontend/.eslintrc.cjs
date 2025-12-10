module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
    es2021: true,
  },
  parser: "vue-eslint-parser",
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module",
  },
  extends: ["plugin:vue/vue3-recommended", "@vue/eslint-config-prettier"],
  ignorePatterns: ["auto-imports.d.ts", "components.d.ts"],
  rules: {
    "vue/multi-word-component-names": "off",
    "vue/no-v-html": "warn",
  },
};
