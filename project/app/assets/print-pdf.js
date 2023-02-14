/*
function printtag(tagid) {
  var hashid = "#" + tagid;
  var tagname = $(hashid).prop("tagName").toLowerCase();
  var attributes = "";
  var attrs = document.getElementById(tagid).attributes;
  $.each(attrs, function (i, elem) {
    attributes += " " + elem.name + " ='" + elem.value + "' ";
  });
  var divToPrint = $(hashid).html();
  var head = "<html><head>" + $("head").html() + "</head>";
  var allcontent =
    head +
    "<body  onload='window.print()' >" +
    "<" +
    tagname +
    attributes +
    ">" +
    divToPrint +
    "</" +
    tagname +
    ">" +
    "</body></html>";
  var newWin = window.open("", "Print-Window");
  newWin.document.open();
  newWin.document.write(allcontent);
  newWin.document.close();
*/

window.dash_clientside = Object.assign({}, window.dash_clientside, {
  clientside: {
    printPdf: function () {
      window.print();
    },
  },
});
