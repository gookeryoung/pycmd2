module.exports = {
  root: true,
  env: {
    // 你的环境变量（包含多个预定义的全局变量）
    //
    // browser: true,
    // node: true,
    // mocha: true,
    // jest: true,
    // jquery: true
    browser: true,
    es2021: true,
    es6: true,
    node: true,
  },
  extends: [
    "alloy",
    "alloy/React",
    "alloy/typescript",
    "plugin:React-hooks/recommended",
  ],
  globals: {
    // 你的全局变量（设置为 false 表示它不允许被重新赋值）
    //
    // myGlobal: false
    defineProps: "readonly",
    defineEmits: "readonly",
    defineExpose: "readonly",
    withDefaults: "readonly",
  },
  ignorePatterns: ["dist", ".eslintrc.cjs"],
  parser: "@typescript-eslint/parser",
  plugins: ["simple-import-sort"],
  rules: {
    "simple-import-sort/imports": "error",
    "react/require-default-props": "off",
  },
  settings: {
    react: {
      version: "detect",
    },
  },
};
