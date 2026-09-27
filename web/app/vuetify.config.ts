import { defineVuetifyConfiguration } from 'vuetify-nuxt-module/custom-configuration'

// Warm-neutral, cozy palette per the product's visual direction. This is a
// starting point, not a finished brand system — swap tokens once real
// brand colors are approved.
export default defineVuetifyConfiguration({
  theme: {
    defaultTheme: 'muratoriLight',
    themes: {
      muratoriLight: {
        dark: false,
        colors: {
          background: '#FAF6F1',
          surface: '#FFFFFF',
          primary: '#B5502F',
          'primary-darken-1': '#8F3D22',
          secondary: '#5B7065',
          error: '#B3261E',
          warning: '#8A6D3B',
          info: '#3A6EA5',
          success: '#3F7D4F',
        },
      },
      muratoriDark: {
        dark: true,
        colors: {
          background: '#1B1712',
          surface: '#241F19',
          primary: '#E08A63',
          'primary-darken-1': '#C46C46',
          secondary: '#9AB0A2',
          error: '#E5847B',
          warning: '#D8B36B',
          info: '#8FB4DE',
          success: '#8FCB9E',
        },
      },
    },
  },
  defaults: {
    VBtn: { rounded: 'lg' },
    VCard: { rounded: 'lg' },
  },
})
