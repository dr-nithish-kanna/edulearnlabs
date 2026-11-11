// Site-wide switches. Ads stay off until about 5k to 10k monthly visitors (planning/decisions.md).
// The flag is read at build time, so ad slots are either in the layout or not: no layout shift (CLS 0).
export const SITE = {
  name: 'EduLearnLabs',
  tagline: 'Free learning games for kids',
  maker: 'Nifty Games Studios',
  makerUrl: 'https://niftygamesstudios.in/',
  ads: { enabled: false },
};

const BASE = import.meta.env.BASE_URL.replace(/\/?$/, '/');
/** Link to a page inside the site, respecting the base path. url('math-games/') -> /edulearnlabs/math-games/ */
export const url = (path = '') => BASE + path.replace(/^\//, '');
