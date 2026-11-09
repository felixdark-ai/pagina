/* DEAU — comportamiento del sitio (sin dependencias). */
(function () {
  'use strict';

  var reducirMovimiento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function listo(fn) {
    if (document.readyState !== 'loading') { fn(); } else { document.addEventListener('DOMContentLoaded', fn); }
  }
  function lista(sel, raiz) { return Array.prototype.slice.call((raiz || document).querySelectorAll(sel)); }

  /* ---------- Menú móvil ---------- */
  function menuMovil() {
    var toggle = document.getElementById('menuToggle');
    var menu = document.getElementById('menuPrincipal');
    if (!toggle || !menu) { return; }

    function cerrar(devolverFoco) {
      menu.classList.remove('abierto');
      document.body.classList.remove('menu-abierto');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', 'Abrir menú de navegación');
      if (devolverFoco) { toggle.focus(); }
    }
    function abrir() {
      menu.classList.add('abierto');
      document.body.classList.add('menu-abierto');
      toggle.setAttribute('aria-expanded', 'true');
      toggle.setAttribute('aria-label', 'Cerrar menú de navegación');
    }

    toggle.addEventListener('click', function () {
      if (menu.classList.contains('abierto')) { cerrar(false); } else { abrir(); }
    });
    lista('a', menu).forEach(function (a) { a.addEventListener('click', function () { cerrar(false); }); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menu.classList.contains('abierto')) { cerrar(true); }
    });
    document.addEventListener('click', function (e) {
      if (menu.classList.contains('abierto') && !menu.contains(e.target) && !toggle.contains(e.target)) { cerrar(false); }
    });
    window.matchMedia('(min-width: 769px)').addEventListener('change', function (m) { if (m.matches) { cerrar(false); } });
  }

  /* ---------- Cabecera compacta al hacer scroll ---------- */
  function cabeceraCompacta() {
    var cabecera = document.getElementById('cabecera');
    if (!cabecera) { return; }
    function actualizar() { cabecera.classList.toggle('cabecera--compacta', window.scrollY > 40); }
    window.addEventListener('scroll', actualizar, { passive: true });
    actualizar();
  }

  /* ---------- Hero: carrusel automático (5 s) ---------- */
  function heroCarrusel() {
    lista('[data-hero-carrusel]').forEach(function (hero) {
      var slides = lista('.hero__slide', hero);
      var puntos = lista('[data-hero-punto]', hero);
      if (slides.length < 2) { return; }

      var intervalo = parseInt(hero.getAttribute('data-intervalo'), 10) || 5000;
      var btnPausa = hero.querySelector('[data-hero-pausa]');
      var actual = 0;
      var temporizador = null;
      var pausaUsuario = reducirMovimiento;   // con "menos movimiento" no rota solo
      var pausaTemporal = false;              // hover / foco / pestaña oculta

      hero.style.setProperty('--intervalo', intervalo + 'ms');

      function reiniciarProgreso() {
        var punto = puntos[actual];
        if (!punto) { return; }
        punto.classList.remove('es-activo');
        void punto.offsetWidth;               // reinicia la animación de la barra
        punto.classList.add('es-activo');
      }

      function mostrar(indice) {
        slides[actual].classList.remove('es-activo');
        if (puntos[actual]) { puntos[actual].classList.remove('es-activo'); puntos[actual].removeAttribute('aria-current'); }
        actual = (indice + slides.length) % slides.length;
        slides[actual].classList.add('es-activo');
        if (puntos[actual]) { puntos[actual].classList.add('es-activo'); puntos[actual].setAttribute('aria-current', 'true'); }
      }

      function detener() { if (temporizador) { clearTimeout(temporizador); temporizador = null; } }

      function programar() {
        detener();
        hero.classList.toggle('esta-pausado', pausaUsuario || pausaTemporal);
        if (pausaUsuario || pausaTemporal) { return; }
        temporizador = setTimeout(function () { mostrar(actual + 1); programar(); }, intervalo);
      }

      function irA(indice) { mostrar(indice); reiniciarProgreso(); programar(); }

      var prev = hero.querySelector('[data-hero-prev]');
      var next = hero.querySelector('[data-hero-next]');
      if (prev) { prev.addEventListener('click', function () { irA(actual - 1); }); }
      if (next) { next.addEventListener('click', function () { irA(actual + 1); }); }
      puntos.forEach(function (p, i) { p.addEventListener('click', function () { irA(i); }); });

      function actualizarBotonPausa() {
        if (!btnPausa) { return; }
        btnPausa.setAttribute('aria-pressed', pausaUsuario ? 'true' : 'false');
        btnPausa.setAttribute('aria-label', pausaUsuario ? 'Reanudar rotación de imágenes' : 'Pausar rotación de imágenes');
      }
      if (btnPausa) {
        btnPausa.addEventListener('click', function () {
          pausaUsuario = !pausaUsuario;
          actualizarBotonPausa();
          if (!pausaUsuario) { reiniciarProgreso(); }
          programar();
        });
      }

      function pausarTemporal() { pausaTemporal = true; programar(); }
      function reanudarTemporal() { pausaTemporal = false; reiniciarProgreso(); programar(); }
      if (window.matchMedia('(hover: hover)').matches) {   // en pantallas táctiles el tap no debe congelar el carrusel
        hero.addEventListener('mouseenter', pausarTemporal);
        hero.addEventListener('mouseleave', reanudarTemporal);
      }
      hero.addEventListener('focusin', pausarTemporal);
      hero.addEventListener('focusout', reanudarTemporal);
      document.addEventListener('visibilitychange', function () {
        if (document.hidden) { pausarTemporal(); } else { reanudarTemporal(); }
      });

      // Gesto táctil: deslizar para cambiar de imagen
      var inicioX = null;
      hero.addEventListener('touchstart', function (e) { inicioX = e.changedTouches[0].clientX; }, { passive: true });
      hero.addEventListener('touchend', function (e) {
        if (inicioX === null) { return; }
        var dx = e.changedTouches[0].clientX - inicioX;
        inicioX = null;
        if (Math.abs(dx) > 50) { irA(actual + (dx < 0 ? 1 : -1)); }
      }, { passive: true });

      if (puntos[0]) { puntos[0].setAttribute('aria-current', 'true'); }
      actualizarBotonPausa();
      programar();
    });
  }

  /* ---------- Carruseles de escudos (desplazamiento horizontal) ---------- */
  function carruselesDeEscudos() {
    lista('[data-carrusel]').forEach(function (carrusel) {
      var pista = carrusel.querySelector('[data-carrusel-pista]');
      var prev = carrusel.querySelector('[data-carrusel-prev]');
      var next = carrusel.querySelector('[data-carrusel-next]');
      if (!pista) { return; }

      function desplazar(direccion) {
        var item = pista.querySelector('.carrusel__item');
        var paso = item ? item.getBoundingClientRect().width + 22 : 240;
        pista.scrollBy({ left: direccion * paso * 2, behavior: reducirMovimiento ? 'auto' : 'smooth' });
      }
      function estado() {
        var max = pista.scrollWidth - pista.clientWidth - 2;
        if (prev) { prev.disabled = pista.scrollLeft <= 2; }
        if (next) { next.disabled = pista.scrollLeft >= max; }
        carrusel.classList.toggle('carrusel--corto', max <= 0);
      }

      if (prev) { prev.addEventListener('click', function () { desplazar(-1); }); }
      if (next) { next.addEventListener('click', function () { desplazar(1); }); }
      pista.addEventListener('scroll', estado, { passive: true });
      window.addEventListener('resize', estado);
      estado();

      // Arrastrar con el mouse (en pantallas táctiles ya funciona deslizando)
      var arrastrando = false, movido = false, x0 = 0, desde = 0;
      pista.addEventListener('pointerdown', function (e) {
        if (e.pointerType !== 'mouse' || e.button !== 0) { return; }
        arrastrando = true; movido = false; x0 = e.clientX; desde = pista.scrollLeft;
      });
      window.addEventListener('pointermove', function (e) {
        if (!arrastrando) { return; }
        var dx = e.clientX - x0;
        if (!movido && Math.abs(dx) > 6) { movido = true; pista.classList.add('arrastrando'); }
        if (movido) { pista.scrollLeft = desde - dx; }
      });
      window.addEventListener('pointerup', function () {
        if (!arrastrando) { return; }
        arrastrando = false;
        pista.classList.remove('arrastrando');
      });
      pista.addEventListener('click', function (e) {
        if (movido) { e.preventDefault(); e.stopPropagation(); movido = false; }
      }, true);
      pista.addEventListener('dragstart', function (e) { e.preventDefault(); });
    });
  }

  /* ---------- Aparición escalonada al hacer scroll ----------
     La lista debe coincidir con la de style.css (los elementos nacen ocultos por CSS). */
  var SELECTOR_APARICION = [
    '.seccion__titulo', '.seccion__intro', '.tarjeta-proceso', '.tarjeta-noticia', '.linea-tiempo li', '.testimonio',
    '.tarjeta-documento', '.tarjeta-persona', '.tarjeta-convocatoria', '.galeria__item', '.grupo-acreditacion',
    '.indicador', '.tarjeta-destacada', '.tarjeta-lateral', '.certificado', '.articulo-noticia__resumen',
    '.articulo-noticia__contenido', '.articulo-noticia__externo', '.video-marco', '.tabla-documentos li', '.barra-filtros',
    '.filtros-categorias', '.formulario', '.acordeon__item', '.mapa-contenedor', '.lista-estructura li', '.lista-noticias li',
    '.tarjeta-acceso-externo', '.tarjeta-login', '.barra-confianza__item', '.imagen-redondeada', '.paginacion',
    '.sin-resultados', '.seccion--contacto-rapido'
  ].join(',');

  function aparicion() {
    var elementos = lista(SELECTOR_APARICION);
    if (reducirMovimiento || !('IntersectionObserver' in window)) {
      elementos.forEach(function (el) { el.classList.add('visto'); });
      return;
    }
    var observador = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (entrada) {
        if (!entrada.isIntersecting) { return; }
        observador.unobserve(entrada.target);
        entrada.target.classList.add('visto');
      });
    }, { threshold: 0, rootMargin: '0px 0px -40px 0px' });

    elementos.forEach(function (el) {
      var padre = el.parentElement;
      var hermanos = padre ? Array.prototype.filter.call(padre.children, function (h) { return h.matches(SELECTOR_APARICION); }) : [el];
      el.style.setProperty('--i', Math.min(Math.max(hermanos.indexOf(el), 0), 6));
      observador.observe(el);
    });
  }

  /* ---------- Indicadores: cuenta animada ---------- */
  function contadores() {
    var els = lista('[data-contador]');
    if (!els.length || reducirMovimiento || !('IntersectionObserver' in window)) { return; }
    var obs = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (entrada) {
        if (!entrada.isIntersecting) { return; }
        var el = entrada.target;
        obs.unobserve(el);
        var texto = el.textContent.trim();
        var m = texto.match(/^(\D*)(\d[\d.,]*)(.*)$/);
        if (!m) { return; }
        var destino = parseFloat(m[2].replace(/[.,]/g, ''));
        if (!isFinite(destino) || destino === 0) { return; }
        var duracion = 1400, t0 = null;
        function paso(t) {
          if (t0 === null) { t0 = t; }
          var p = Math.min((t - t0) / duracion, 1);
          var eased = 1 - Math.pow(1 - p, 3);
          el.textContent = m[1] + Math.round(destino * eased).toLocaleString('es') + m[3];
          if (p < 1) { requestAnimationFrame(paso); } else { el.textContent = texto; }
        }
        requestAnimationFrame(paso);
      });
    }, { threshold: 0.6 });
    els.forEach(function (el) { obs.observe(el); });
  }

  /* ---------- Visor de imágenes (galerías y certificados) ---------- */
  function visorImagenes() {
    var enlaces = lista('[data-lightbox]');
    if (!enlaces.length) { return; }
    var dlg = document.createElement('dialog');
    if (typeof dlg.showModal !== 'function') { return; }   // sin soporte: el enlace abre la imagen normalmente

    dlg.className = 'lightbox';
    dlg.setAttribute('aria-label', 'Visor de imágenes');
    dlg.innerHTML =
      '<button type="button" class="lightbox__btn lightbox__btn--cerrar" aria-label="Cerrar visor">&times;</button>' +
      '<button type="button" class="lightbox__btn lightbox__btn--prev" aria-label="Imagen anterior">&#8249;</button>' +
      '<figure class="lightbox__figura"><img alt=""><figcaption class="lightbox__pie"></figcaption></figure>' +
      '<button type="button" class="lightbox__btn lightbox__btn--next" aria-label="Imagen siguiente">&#8250;</button>';
    document.body.appendChild(dlg);

    var figura = dlg.querySelector('.lightbox__figura');
    var img = dlg.querySelector('img');
    var pie = dlg.querySelector('.lightbox__pie');
    var btnPrev = dlg.querySelector('.lightbox__btn--prev');
    var btnNext = dlg.querySelector('.lightbox__btn--next');
    var grupo = [], indice = 0;

    function mostrar(i) {
      indice = (i + grupo.length) % grupo.length;
      var a = grupo[indice];
      var miniatura = a.querySelector('img');
      img.src = a.getAttribute('href');
      img.alt = (miniatura && miniatura.alt) || '';
      var texto = a.getAttribute('data-pie') || '';
      pie.textContent = texto + (grupo.length > 1 ? (texto ? '  ·  ' : '') + (indice + 1) + ' / ' + grupo.length : '');
      btnPrev.hidden = btnNext.hidden = grupo.length < 2;
      figura.classList.remove('cambia');
      void figura.offsetWidth;
      figura.classList.add('cambia');
    }

    enlaces.forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        var nombre = a.getAttribute('data-lightbox');
        grupo = enlaces.filter(function (x) { return x.getAttribute('data-lightbox') === nombre; });
        mostrar(grupo.indexOf(a));
        dlg.showModal();
      });
    });

    dlg.querySelector('.lightbox__btn--cerrar').addEventListener('click', function () { dlg.close(); });
    btnPrev.addEventListener('click', function () { mostrar(indice - 1); });
    btnNext.addEventListener('click', function () { mostrar(indice + 1); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) { dlg.close(); } });
    dlg.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { mostrar(indice - 1); }
      if (e.key === 'ArrowRight') { mostrar(indice + 1); }
    });
    dlg.addEventListener('close', function () { img.removeAttribute('src'); });
  }

  /* ---------- Barra de progreso de lectura + botón «volver arriba» + parallax del hero ---------- */
  function efectosDeScroll() {
    var barra = document.createElement('div');
    barra.className = 'progreso-scroll';
    barra.setAttribute('aria-hidden', 'true');
    document.body.appendChild(barra);

    var subir = document.createElement('button');
    subir.type = 'button';
    subir.className = 'volver-arriba';
    subir.setAttribute('aria-label', 'Volver al inicio de la página');
    subir.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 19V5M5 12l7-7 7 7" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    subir.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: reducirMovimiento ? 'auto' : 'smooth' }); });
    document.body.appendChild(subir);

    var fondoHero = document.querySelector('.hero__fondo');
    var hero = fondoHero ? fondoHero.parentElement : null;
    var pendiente = false;

    function actualizar() {
      pendiente = false;
      var y = window.scrollY || window.pageYOffset;
      var total = document.documentElement.scrollHeight - window.innerHeight;
      barra.style.transform = 'scaleX(' + (total > 0 ? Math.min(y / total, 1) : 0) + ')';
      subir.classList.toggle('visible', y > 600);
      if (fondoHero && !reducirMovimiento && y < hero.offsetHeight) {
        fondoHero.style.transform = 'translate3d(0,' + Math.round(y * 0.12) + 'px,0)';
      }
    }
    window.addEventListener('scroll', function () {
      if (!pendiente) { pendiente = true; requestAnimationFrame(actualizar); }
    }, { passive: true });
    window.addEventListener('resize', actualizar);
    actualizar();
  }

  /* ---------- Imágenes diferidas: aparecen con fundido al terminar de cargar ---------- */
  function imagenesDiferidas() {
    lista('img[loading="lazy"]').forEach(function (img) {
      if (img.complete) { return; }
      img.classList.add('cargando');
      function fin() { img.classList.remove('cargando'); img.classList.add('cargada'); }
      img.addEventListener('load', fin, { once: true });
      img.addEventListener('error', fin, { once: true });
    });
  }

  /* ---------- Formularios: estado «enviando» (evita doble envío) ---------- */
  function formularios() {
    lista('form').forEach(function (form) {
      var boton = form.querySelector('.boton[type="submit"]');
      if (!boton) { return; }
      form.addEventListener('submit', function (e) {
        if (e.defaultPrevented) { return; }
        if (form.getAttribute('data-enviando')) { e.preventDefault(); return; }
        form.setAttribute('data-enviando', '1');
        boton.classList.add('enviando');
        boton.setAttribute('aria-busy', 'true');
      });
    });
    // Al volver con el botón «atrás» el formulario no debe quedar bloqueado.
    window.addEventListener('pageshow', function (e) {
      if (!e.persisted) { return; }
      lista('form[data-enviando]').forEach(function (f) {
        f.removeAttribute('data-enviando');
        lista('.boton.enviando', f).forEach(function (b) { b.classList.remove('enviando'); b.removeAttribute('aria-busy'); });
      });
    });
  }

  listo(function () {
    menuMovil();
    cabeceraCompacta();
    heroCarrusel();
    carruselesDeEscudos();
    aparicion();
    contadores();
    visorImagenes();
    efectosDeScroll();
    imagenesDiferidas();
    formularios();
  });
})();
