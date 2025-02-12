import '@mdi/font/css/materialdesignicons.css';
import 'vuetify/styles';

import { createVuetify } from 'vuetify';
import { aliases, mdi } from 'vuetify/iconsets/mdi';

export default defineNuxtPlugin((app) => {
  const vuetify = createVuetify({
    icons: {
      defaultSet: 'mdi',
      aliases,
      sets: { mdi },
    },
    theme: {
      defaultTheme: 'light',
      themes: {
        light: {
          colors: {
            primary: '#1976D2',
            secondary: '#424242',
            accent: '#82B1FF',
            error: '#FF5252',
            info: '#2196F3',
            success: '#4CAF50',
            warning: '#FFC107',
          },
        },
        dark: {
          colors: {
            primary: '#BB86FC',
            secondary: '#03DAC6',
            background: '#121212',
            surface: '#1E1E1E',
            error: '#CF6679',
            info: '#03DAC6',
            success: '#03DAC6',
            warning: '#FFDE03',
          },
        },
      },
    },
  });

  app.vueApp.use(vuetify);
});
