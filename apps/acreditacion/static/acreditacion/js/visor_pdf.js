/* Certificado en PDF: visor propio con PDF.js (dominio «carreras acreditadas»).
   No depende del visor PDF del navegador (que Edge/Brave bloquean o no ofrecen en móviles).
   Requiere que pdf.min.js se cargue antes (ver acreditacion/detalle.html). */
(function () {
  'use strict';

  function listo(fn) {
    if (document.readyState !== 'loading') { fn(); } else { document.addEventListener('DOMContentLoaded', fn); }
  }
  function lista(sel, raiz) { return Array.prototype.slice.call((raiz || document).querySelectorAll(sel)); }

  function visoresPdf() {
    lista('[data-visor-pdf]').forEach(function (visor) {
      var lienzo = visor.querySelector('[data-pdf-lienzo]');
      var canvas = visor.querySelector('[data-pdf-canvas]');
      var estado = visor.querySelector('[data-pdf-estado]');
      var etqActual = visor.querySelector('[data-pdf-actual]');
      var etqTotal = visor.querySelector('[data-pdf-total]');
      var etqZoom = visor.querySelector('[data-pdf-zoom]');
      var grupoPaginas = visor.querySelector('[data-pdf-paginas]');
      var btn = function (n) { return visor.querySelector('[data-pdf-' + n + ']'); };

      function error(texto) {
        estado.hidden = false;
        estado.className = 'visor-pdf__estado visor-pdf__estado--error';
        estado.textContent = texto || 'No pudimos mostrar el certificado en esta página. Usa los botones «Abrir» o «Descargar» para verlo.';
      }
      if (!window.pdfjsLib) { error(); return; }
      window.pdfjsLib.GlobalWorkerOptions.workerSrc = visor.getAttribute('data-worker');

      var pdf = null, pagina = 1, zoom = 1, ocupado = false, repetir = false;
      var PASOS = [0.5, 0.75, 1, 1.25, 1.5, 2, 3];

      function dibujar(conFundido) {
        if (!pdf) { return; }
        if (ocupado) { repetir = true; return; }
        ocupado = true;
        if (conFundido) { canvas.classList.add('cambiando'); }
        pdf.getPage(pagina).then(function (pg) {
          var base = pg.getViewport({ scale: 1 });
          var disponible = Math.max(lienzo.clientWidth - 36, 220);
          var escalaCss = (disponible / base.width) * zoom;
          var dpr = Math.min(window.devicePixelRatio || 1, 3);
          var vista = pg.getViewport({ scale: escalaCss * dpr });
          canvas.width = Math.floor(vista.width);
          canvas.height = Math.floor(vista.height);
          canvas.style.width = Math.floor(vista.width / dpr) + 'px';
          canvas.style.height = Math.floor(vista.height / dpr) + 'px';
          return pg.render({ canvasContext: canvas.getContext('2d'), viewport: vista }).promise;
        }).then(function () {
          canvas.classList.remove('cambiando');
          estado.hidden = true;
          etqActual.textContent = pagina;
          etqZoom.textContent = Math.round(zoom * 100) + '%';
          btn('prev').disabled = pagina <= 1;
          btn('next').disabled = pagina >= pdf.numPages;
          btn('menos').disabled = zoom <= PASOS[0];
          btn('mas').disabled = zoom >= PASOS[PASOS.length - 1];
        }).catch(function () { error(); }).then(function () {
          ocupado = false;
          if (repetir) { repetir = false; dibujar(false); }
        });
      }

      function irPagina(n) {
        if (!pdf || n < 1 || n > pdf.numPages || n === pagina) { return; }
        pagina = n;
        lienzo.scrollTop = 0;
        dibujar(true);
      }
      function cambiarZoom(direccion) {
        var i = PASOS.indexOf(zoom);
        if (i < 0) { i = 2; }
        var nuevo = PASOS[Math.min(Math.max(i + direccion, 0), PASOS.length - 1)];
        if (nuevo !== zoom) { zoom = nuevo; dibujar(false); }
      }

      btn('prev').addEventListener('click', function () { irPagina(pagina - 1); });
      btn('next').addEventListener('click', function () { irPagina(pagina + 1); });
      btn('menos').addEventListener('click', function () { cambiarZoom(-1); });
      btn('mas').addEventListener('click', function () { cambiarZoom(1); });
      btn('ajustar').addEventListener('click', function () { zoom = 1; dibujar(false); });

      var btnPantalla = btn('pantalla');
      if (btnPantalla) {
        if (!visor.requestFullscreen) { btnPantalla.hidden = true; }
        else {
          btnPantalla.addEventListener('click', function () {
            if (document.fullscreenElement) { document.exitFullscreen(); } else { visor.requestFullscreen(); }
          });
          document.addEventListener('fullscreenchange', function () { dibujar(false); });
        }
      }

      lienzo.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowLeft' || e.key === 'PageUp') { irPagina(pagina - 1); }
        else if (e.key === 'ArrowRight' || e.key === 'PageDown') { irPagina(pagina + 1); }
        else if (e.key === '+' || e.key === '=') { cambiarZoom(1); }
        else if (e.key === '-') { cambiarZoom(-1); }
        else { return; }
        if (e.key.indexOf('Arrow') !== 0) { e.preventDefault(); }
      });

      var temporizador = null;
      window.addEventListener('resize', function () {
        clearTimeout(temporizador);
        temporizador = setTimeout(function () { dibujar(false); }, 180);
      });

      window.pdfjsLib.getDocument({ url: visor.getAttribute('data-src') }).promise.then(function (doc) {
        pdf = doc;
        etqTotal.textContent = doc.numPages;
        if (grupoPaginas) { grupoPaginas.hidden = doc.numPages < 2; }
        dibujar(false);
      }).catch(function () { error(); });
    });
  }

  listo(visoresPdf);
})();
