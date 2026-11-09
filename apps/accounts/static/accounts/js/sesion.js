/* Mantiene viva la sesión MIENTRAS la persona trabaja y avisa si ya caducó.
   Si no hay actividad (mouse, teclado, desplazamiento), no se envía nada: la sesión caduca sola
   en el servidor tras el tiempo de inactividad configurado. */
(function () {
  'use strict';

  var etiqueta = document.currentScript || document.querySelector('script[data-ping]');
  if (!etiqueta) { return; }
  var urlPing = etiqueta.getAttribute('data-ping');
  var urlLogin = etiqueta.getAttribute('data-login') || '/login/';
  var cada = (parseInt(etiqueta.getAttribute('data-intervalo'), 10) || 300) * 1000;

  var ultimaActividad = Date.now();
  var ultimoPing = Date.now();
  var caducada = false;

  function registrarActividad() { ultimaActividad = Date.now(); }
  ['mousemove', 'mousedown', 'keydown', 'scroll', 'touchstart', 'input', 'click'].forEach(function (evento) {
    window.addEventListener(evento, registrarActividad, { passive: true, capture: true });
  });

  function mostrarAviso() {
    if (document.getElementById('aviso-sesion')) { return; }
    var caja = document.createElement('div');
    caja.id = 'aviso-sesion';
    caja.setAttribute('role', 'alert');
    caja.style.cssText = 'position:fixed;left:16px;right:16px;bottom:16px;max-width:560px;margin:0 auto;z-index:100000;' +
      'background:#002B5C;color:#fff;border-left:6px solid #C8102E;border-radius:8px;padding:14px 18px;' +
      'box-shadow:0 10px 30px rgba(0,0,0,.35);font:15px/1.5 system-ui,sans-serif';
    caja.innerHTML = '<strong>Tu sesión se cerró por inactividad.</strong> Si estabas escribiendo algo, cópialo antes de salir. ' +
      '<a style="color:#FF7A87;font-weight:700" target="_blank" rel="noopener" href="' + urlLogin + '">Iniciar sesión de nuevo</a> ' +
      '<button type="button" style="margin-left:8px;background:transparent;border:1px solid #fff;color:#fff;border-radius:6px;padding:2px 10px;cursor:pointer">Cerrar</button>';
    caja.querySelector('button').addEventListener('click', function () { caja.remove(); });
    document.body.appendChild(caja);
  }

  function avisarAlServidor() {
    ultimoPing = Date.now();
    fetch(urlPing, { credentials: 'same-origin', cache: 'no-store' }).then(function (respuesta) {
      if (respuesta.status === 401) { caducada = true; mostrarAviso(); }
    }).catch(function () { /* sin conexión: se reintenta en el siguiente ciclo */ });
  }

  setInterval(function () {
    if (caducada) { return; }
    var ahora = Date.now();
    // Solo se avisa si ya pasó el intervalo Y hubo actividad reciente
    if (ahora - ultimoPing >= cada && ahora - ultimaActividad < cada) { avisarAlServidor(); }
  }, 15000);
})();
