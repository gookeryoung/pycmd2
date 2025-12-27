# ESLint 配置说明

## 问题解决

ESLint 9.x 版本使用了新的配置格式（`eslint.config.js`），不再支持旧的 `.eslintrc.json` 格式。我们已经为您创建了新的配置文件。

## 文件说明

### eslint.config.js

这是新的ESLint配置文件，包含以下特点：

- 使用ESLint 9.x的扁平配置格式
- 基本的JavaScript和TypeScript支持
- 常用的代码风格规则
- 忽略构建文件和依赖目录

## 使用方法

### 安装依赖

```bash
npm install
```

### 检查代码

```bash
npm run lint:check
```

### 自动修复

```bash
npm run lint
```

## 配置详情

当前的ESLint配置包含以下规则：

### 基本规则

- `no-unused-vars`: 检查未使用的变量
- `no-console`: 允许使用console
- `no-debugger`: 警告debugger语句
- `prefer-const`: 推荐使用const
- `no-var`: 禁止使用var

### 代码风格

- `indent`: 使用2空格缩进
- `quotes`: 使用单引号
- `semi`: 不使用分号
- `comma-dangle`: 不使用尾随逗号
- `eol-last`: 文件以换行符结尾
- `no-trailing-spaces`: 禁止尾随空格

## Vue支持

配置已包含完整的Vue支持，包括：

### Vue特定规则

- `vue/multi-word-component-names`: 关闭多词组件名称限制
- `vue/component-definition-name-casing`: 组件定义使用PascalCase
- `vue/component-name-in-template-casing`: 模板中组件名使用PascalCase
- `vue/custom-event-name-casing`: 自定义事件使用camelCase
- `vue/define-macros-order`: 强制define宏的顺序
- `vue/html-self-closing`: HTML自闭合标签规则
- `vue/max-attributes-per-line`: 每行最大属性数量
- `vue/multiline-html-element-content-newline`: 多行HTML元素内容换行
- `vue/no-unused-components`: 警告未使用的组件
- `vue/no-unused-vars`: 警告未使用的变量
- `vue/padding-line-between-blocks`: 块之间添加空行（使用`['error', 'always']`格式）

### Vue组合式API支持

配置中包含了Vue 3组合式API的全局变量：

- `defineProps`, `defineEmits`, `defineExpose`, `withDefaults`
- `ref`, `reactive`, `computed`, `watch`, `watchEffect`
- `onMounted`, `onUnmounted`, `nextTick`

### TypeScript支持

配置已包含TypeScript支持，适用于`.vue`文件中的`<script setup lang="ts">`块。

## 文件分离

配置按文件类型分离处理：

1. `**/*.{js,mjs,cjs,ts}` - JavaScript/TypeScript文件
2. `**/*.vue` - Vue单文件组件
3. `**/*.ts` - 纯TypeScript文件

每种文件类型使用适当的解析器和规则集。

## 故障排除

### 常见问题

#### Vue规则配置格式错误

错误示例：
```
Error: Key "vue/padding-line-between-blocks": Value {"always":true} should be equal to one of the allowed values.
```

解决方案：
某些Vue规则的配置格式在ESLint 9.x中有所变化。例如，`vue/padding-line-between-blocks`规则应使用以下格式：

```javascript
'vue/padding-line-between-blocks': ['error', 'always']
```

而不是：
```javascript
'vue/padding-line-between-blocks': ['error', { always: true }]
```

#### TypeScript ESLint插件未找到

错误示例：
```
Error: A configuration object specifies rule "@typescript-eslint/no-unused-vars", but could not find plugin "@typescript-eslint".
```

解决方案：
1. 确保已安装TypeScript ESLint插件：
   ```bash
   npm install --save-dev @typescript-eslint/eslint-plugin @typescript-eslint/parser
   ```

2. 在eslint.config.js中正确导入和配置插件：
   ```javascript
   import tseslint from '@typescript-eslint/eslint-plugin'
   import tsparser from '@typescript-eslint/parser'

   // 在配置中添加插件
   {
     files: ['**/*.ts', '**/*.vue'],
     languageOptions: {
       parser: tsparser
     },
     plugins: {
       '@typescript-eslint': tseslint
     },
     rules: {
       '@typescript-eslint/no-unused-vars': 'error'
     }
   }
   ```

#### 未使用下划线变量错误

错误示例：
```
Error: '_' is defined but never used  no-unused-vars
```

这个错误通常出现在使用下划线作为未使用参数占位符的情况下，例如：
```javascript
Array.from({ length: 20 }, _ => '')
```

解决方案有两种：

1. 修改ESLint配置以忽略下划线前缀的变量：
   ```javascript
   {
     files: ['**/*.vue'],
     rules: {
       'no-unused-vars': [
         'warn',
         {
           argsIgnorePattern: '^_',
           varsIgnorePattern: '^_',
           caughtErrorsIgnorePattern: '^_'
         }
       ]
     }
   }
   ```

2. 或者修改代码，使用不同的写法：
   ```javascript
   // 使用空函数参数
   Array.from({ length: 20 }, () => '')

   // 或者使用有意义的参数名
   Array.from({ length: 20 }, (index) => index.toString())
   ```

### 基本故障排除

如果遇到问题，请尝试：

1. 删除`node_modules`文件夹和`package-lock.json`
2. 重新安装依赖：`npm install`
3. 确保使用的是ESLint 9.x版本
4. 检查Vue ESLint插件版本是否兼容

## 迁移说明

从`.eslintrc.json`迁移到`eslint.config.js`的主要变化：

1. 配置格式从JSON变为JavaScript模块
2. 使用扁平配置数组代替嵌套对象
3. 语言选项和规则分离
4. 插件配置方式改变

如果您需要更复杂的配置（包括Vue和TypeScript支持），可以参考ESLint 9.x的官方文档。
