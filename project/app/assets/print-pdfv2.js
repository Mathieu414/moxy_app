/* window.dash_clientside = Object.assign({}, window.dash_clientside, {
  clientside: {
    changeVariable: function (n_clicks) {
      if (n_clicks > 0) {
        var opt = {
          margin: 1,
          filename: "out.pdf",
          image: { type: "jpeg", quality: 0.98 },
          html2canvas: { scale: 3 },
          jsPDF: { unit: "cm", format: "a4", orientation: "p" },
          pagebreak: { mode: ["avoid-all"] },
        };
        alert("impression en pdf");
        html2pdf()
          .set(opt)
          .from(document.querySelector(":not(.no-print)"))
          .save();
      }
    },
  },
}); */
