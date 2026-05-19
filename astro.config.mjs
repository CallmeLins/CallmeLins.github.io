import react from "@astrojs/react"
import tailwind from "@astrojs/tailwind"
import { defineConfig } from "astro/config"

// https://astro.build/config
export default defineConfig({
  site: "https://callmelins.github.io",
  devToolbar: {
    enabled: false,
  },
  integrations: [
    react(),
    tailwind({
      applyBaseStyles: false,
    }),
  ],
})
