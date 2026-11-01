import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  {
    rules: {
      // Prohíbe el uso explícito de 'any' para forzar tipado estricto
      "@typescript-eslint/no-explicit-any": "off",
      // Evita variables sin usar generadas por el agente, salvo que inicien con guion bajo
      "@typescript-eslint/no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
        },
      ],
      // Evita imports duplicados o desordenados
      "no-duplicate-imports": "error",
    },
  },
];

export default eslintConfig;