// Одноразовый замер для стенда: какую ширину браузер на самом деле даёт
// странице и во сколько раз он её увеличивает. В сборку не уезжает — имя
// начинается с подчёркивания.
document.getElementById("итог").textContent = JSON.stringify({
  innerWidth: window.innerWidth,
  dpr: window.devicePixelRatio,
  корень: getComputedStyle(document.documentElement).fontSize,
  scrollWidth: document.documentElement.scrollWidth,
});
