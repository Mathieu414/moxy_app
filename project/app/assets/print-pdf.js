window.dash_clientside = Object.assign({}, window.dash_clientside, {
  clientside: {
    printPdf: function (n_clicks) {
      window.print();
      location.reload();
    },
    changeVariable: function (n_clicks) {
      document.getElementById("container").style.width = "1000px";
    },
  },
});
