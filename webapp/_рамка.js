// Раздел приезжает якорем самой рамки: #today, #plan, #out, #out-числа, #stock.
const раздел = decodeURIComponent(location.hash.slice(1)) || "today";
document.getElementById("телефон").src =
  "index.html?key=%D1%81%D1%82%D0%B5%D0%BD%D0%B4#" + encodeURIComponent(раздел);
