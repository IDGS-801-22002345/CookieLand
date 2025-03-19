module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/src/**/*.js",
    "./node_modules/flowbite/**/*.js",
  ],
  safelist: [
    'bg-custom-color-1',
    'bg-custom-color-2',
    'bg-custom-color-3',
    'bg-custom-color-4',
    'bg-custom-color-5',
    'bg-custom-color-6',
    'text-custom-color-1',
    'text-custom-color-2',
    'text-custom-color-3',
    'text-custom-color-4',
    'text-custom-color-5',
    'text-custom-color-6',
  ],
  theme: {
    extend: {
      colors: {
        'custom-color-1': '#B0A6A7',
        'custom-color-2': '#E7DFD8',
        'custom-color-3': '#795757',
        'custom-color-4': '#754146',
        'custom-color-5': '#B97F0C',
        'custom-color-6': '#24985A',
      },
    },
  },
  plugins: [require('flowbite/plugin')],
};