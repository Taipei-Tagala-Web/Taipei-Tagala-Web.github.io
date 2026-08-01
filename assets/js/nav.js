/* 手機版導覽：漢堡選單開合、背景鎖捲動、次級選單手風琴。
   原生 JS，無框架無套件。所有文字由 HTML 的 data-* 帶入，不在此檔寫死文案。 */
(function () {
  'use strict';

  var body = document.body;
  var header = document.querySelector('.site-header');
  var nav = document.getElementById('main-nav');
  var btn = document.querySelector('.nav-toggle');
  if (!header || !nav || !btn) return;

  var labelOpen = btn.getAttribute('data-label-open') || '';
  var labelClose = btn.getAttribute('data-label-close') || '';
  var DESKTOP = 768;

  /* 滿版選單從頁首下緣開始，故需要頁首實際高度。
     頁首高度會隨換行與字型載入改變，因此重新量測。 */
  function syncHeaderHeight() {
    document.documentElement.style.setProperty('--header-h', header.offsetHeight + 'px');
  }
  syncHeaderHeight();
  window.addEventListener('resize', syncHeaderHeight);
  window.addEventListener('load', syncHeaderHeight);
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(syncHeaderHeight);
  }
  /* 字型載入、換行變化、轉向都會改變頁首高度，直接觀察最可靠 */
  if (window.ResizeObserver) {
    new ResizeObserver(syncHeaderHeight).observe(header);
  }

  function closeSubmenus(except) {
    var opened = nav.querySelectorAll('.submenu-btn[aria-expanded="true"]');
    for (var i = 0; i < opened.length; i++) {
      if (opened[i] !== except) opened[i].setAttribute('aria-expanded', 'false');
    }
  }

  function setOpen(open) {
    body.classList.toggle('nav-open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    btn.setAttribute('aria-label', open ? labelClose : labelOpen);
    if (!open) closeSubmenus();
  }

  btn.addEventListener('click', function () {
    setOpen(!body.classList.contains('nav-open'));
  });

  /* Esc 關閉選單，焦點回到按鈕 */
  document.addEventListener('keydown', function (e) {
    if ((e.key === 'Escape' || e.key === 'Esc') && body.classList.contains('nav-open')) {
      setOpen(false);
      btn.focus();
    }
  });

  /* 轉成橫向或放大到桌機寬度時，還原成一般導覽列，避免捲動被鎖住 */
  window.addEventListener('resize', function () {
    if (window.innerWidth >= DESKTOP && body.classList.contains('nav-open')) setOpen(false);
  });

  /* 次級選單手風琴：一次只開一個 */
  nav.addEventListener('click', function (e) {
    var target = e.target;
    var toggle = null;
    while (target && target !== nav) {
      if (target.classList && target.classList.contains('submenu-btn')) { toggle = target; break; }
      target = target.parentNode;
    }
    if (!toggle) return;
    e.preventDefault();
    var isOpen = toggle.getAttribute('aria-expanded') === 'true';
    closeSubmenus(toggle);
    toggle.setAttribute('aria-expanded', isOpen ? 'false' : 'true');
  });
})();
