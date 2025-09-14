import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { dirname, resolve } from "path";
import { fileURLToPath } from "url";
import { defineConfig } from "vite";

const rootDirname = dirname(fileURLToPath(import.meta.url));

export default defineConfig(({ mode }) => {
  return {
    plugins: [react(), tailwindcss()],
    server: {
      host: "0.0.0.0",
      port: 3000,
    },
    resolve: {
      alias: {
        "@app": resolve(rootDirname, "./src"),
        "@assets": resolve(rootDirname, "./src/assets"),
        "@components": resolve(rootDirname, "./src/components"),
        "@contexts": resolve(rootDirname, "./src/contexts"),
        "@features": resolve(rootDirname, "./src/features"),
        "@hooks": resolve(rootDirname, "./src/hooks"),
        "@routes": resolve(rootDirname, "./src/routes"),
        "@services": resolve(rootDirname, "./src/services"),
        "@styles": resolve(rootDirname, "./src/styles"),
        "@utils": resolve(rootDirname, "./src/utils"),
        "@validators": resolve(rootDirname, "./src/validators"),
        "@live2d": resolve(rootDirname, "./src/live2d"),
        "@audio": resolve(rootDirname, "./src/audio"),
        "@stores": resolve(rootDirname, "./src/stores"),
        "@ws": resolve(rootDirname, "./src/ws"),
      },
    },
  };
});
