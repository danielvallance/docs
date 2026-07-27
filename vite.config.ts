/** @type {import('vite').UserConfig} */
export default {
  // This is used at build-time to adjust all the paths.  This is necessary as
  // the site is built statically and placed inside of a /docs subdirectory.
  base: '/docs',
  server: {
    watch: {
      // Don't watch the local pnpm store; it holds tens of thousands of
      // files and exhausts the inotify watcher limit in dev mode.
      ignored: ['**/.pnpm-store/**'],
    },
  },
};
