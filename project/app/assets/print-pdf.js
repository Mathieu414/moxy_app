window.dash_clientside = Object.assign({}, window.dash_clientside, {
  clientside: {
    printPdf: function (n_clicks) {
      window.print();
    },
  },
});
