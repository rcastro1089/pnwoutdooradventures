import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";
import tailwind from "@astrojs/tailwind";

// https://astro.build/config
export default defineConfig({
  site: "https://pnwoutdooradventures.com",
  // trailingSlash debe ser coherente con las canonicals (lo verifica el QA gate).
  trailingSlash: "always",
  integrations: [sitemap(), tailwind()],
});
