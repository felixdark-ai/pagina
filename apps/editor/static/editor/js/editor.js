/* Editor de texto enriquecido de las noticias (Jodit, licencia MIT). */
(function () {
  'use strict';

  function tokenCsrf() {
    var m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    if (m) { return decodeURIComponent(m[1]); }
    var campo = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return campo ? campo.value : '';
  }

  function iniciar() {
    if (!window.Jodit) { return; }
    Array.prototype.forEach.call(document.querySelectorAll('textarea[data-editor-jodit]'), function (area) {
      if (area.getAttribute('data-jodit-listo')) { return; }
      area.setAttribute('data-jodit-listo', '1');

      var editor = window.Jodit.make(area, {
        language: 'es',
        height: 440,
        minHeight: 320,
        placeholder: 'Escribe aquí el contenido de la noticia…',
        enter: 'P',
        spellcheck: true,

        // Barra de herramientas: solo lo que el sitio sabe mostrar
        toolbarAdaptive: false,
        toolbarSticky: false,
        buttons: [
          'bold', 'italic', 'underline', 'strikethrough', '|',
          'paragraph', '|',
          'ul', 'ol', '|',
          'link', 'image', 'table', 'hr', '|',
          'eraser', 'undo', 'redo', '|',
          'fullsize'
        ],
        controls: {
          paragraph: {
            list: window.Jodit.atom({ p: 'Párrafo', h2: 'Título', h3: 'Subtítulo', h4: 'Título menor', blockquote: 'Cita' })
          }
        },

        // Sin contadores ni barra de estado
        statusbar: false,
        showCharsCounter: false,
        showWordsCounter: false,
        showXPathInStatusbar: false,
        hidePoweredByJodit: true,

        // Al pegar (por ejemplo desde Word) se descarta el formato sobrante
        askBeforePasteHTML: false,
        askBeforePasteFromWord: false,
        defaultActionOnPaste: 'insert_clear_html',

        imageDefaultWidth: 600,
        link: { openInNewTabCheckbox: true, noFollowCheckbox: false },

        // Subida de imágenes: solo personal del panel, con protección CSRF
        uploader: {
          url: area.getAttribute('data-url-subida'),
          format: 'json',
          withCredentials: true,
          headers: { 'X-CSRFToken': tokenCsrf() }
        }
      });

      // Garantiza que el texto del formulario sea el último contenido del editor
      if (area.form) {
        area.form.addEventListener('submit', function () { editor.synchronizeValues(); });
      }
    });
  }

  if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', iniciar); } else { iniciar(); }
})();
