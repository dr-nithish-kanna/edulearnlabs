// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// The site lives under niftygamesstudios.in as a GitHub Pages project site. GitHub decides the path from the repo
// name (repo "edulearnlabs" -> /edulearnlabs/). The deploy workflow passes that path in BASE_PATH, so renaming the
// repo or moving to our own domain later is a settings change, not a code change.
const base = process.env.BASE_PATH || '/edulearnlabs';

export default defineConfig({
  site: process.env.SITE_URL || 'https://niftygamesstudios.in',
  base,
  trailingSlash: 'always',
  build: { format: 'directory' },
  integrations: [sitemap({ filter: page => !page.includes('/play/') })],
});
