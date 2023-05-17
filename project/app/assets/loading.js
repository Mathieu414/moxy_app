window.dash_clientside = Object.assign({}, window.dash_clientside, {
  clientside: {
    set_loading: function (n_clicks) {
      document.getElementById("modal-print-article").hidden = true;
      document.getElementById("spinner").setAttribute("aria-busy", true);
    },
    unset_loading: function (n_clicks) {
      document.getElementById("modal-print-article").hidden = false;
      document.getElementById("spinner").setAttribute("aria-busy", false);
    },
  },
});
