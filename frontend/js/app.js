// Punto de entrada: decide qué mostrar según la sesión y la ruta (#/...).

import { api, borrarToken, obtenerToken } from './api.js';
import { esc } from './ui.js';
import { vistaIngreso } from './vistas/ingreso.js';
import { vistaPerfil } from './vistas/perfil.js';
import { vistaMascotas } from './vistas/mascotas.js';
import { vistaReservas } from './vistas/reservas.js';
import { vistaDisponibles, vistaMisPaseos } from './vistas/paseos.js';
import { vistaPagos } from './vistas/pagos.js';
import { vistaPenalidades } from './vistas/penalidades.js';

// Pantallas de cada rol: [ruta, texto del menú, función que la dibuja]
const RUTAS = {
  DUENO: [
    ['reservas', 'Mis reservas', vistaReservas],
    ['mascotas', 'Mis mascotas', vistaMascotas],
    ['pagos', 'Pagos', vistaPagos],
    ['penalidades', 'Penalidades', vistaPenalidades],
    ['perfil', 'Mi perfil', vistaPerfil],
  ],
  PASEADOR: [
    ['disponibles', 'Paseos disponibles', vistaDisponibles],
    ['paseos', 'Mis paseos', vistaMisPaseos],
    ['pagos', 'Cobros', vistaPagos],
    ['penalidades', 'Penalidades', vistaPenalidades],
    ['perfil', 'Mi perfil', vistaPerfil],
  ],
};

// El usuario logueado (o null). Las vistas lo reciben como `contexto.usuario`.
let usuario = null;

const raiz = document.getElementById('app');

async function iniciar() {
  if (!obtenerToken()) {
    usuario = null;
    return mostrarIngreso();
  }
  try {
    usuario = await api('/usuarios/me');
  } catch {
    borrarToken();
    return mostrarIngreso();
  }
  mostrarApp();
}

function mostrarIngreso() {
  raiz.innerHTML = '';
  vistaIngreso(raiz, { alIngresar: iniciar });
}

function rutaActual() {
  return location.hash.replace(/^#\/?/, '') || RUTAS[usuario.rol][0][0];
}

function mostrarApp() {
  const rutas = RUTAS[usuario.rol];
  raiz.innerHTML = `
    <header class="barra">
      <a class="marca" href="#/"><img src="img/logo.png" alt="Yendog" class="logo"></a>
      <div class="usuario">
        <span class="nombre">${esc(usuario.nombre)}</span>
        <span class="rol">${usuario.rol === 'DUENO' ? 'Dueño' : 'Paseador'}</span>
        <button class="chico" id="salir">Salir</button>
      </div>
    </header>
    <div class="layout">
      <nav class="menu" aria-label="Secciones">
        ${rutas.map(([ruta, texto]) => `<a href="#/${ruta}" data-ruta="${ruta}">${texto}</a>`).join('')}
      </nav>
      <main id="contenido"></main>
    </div>`;
  document.getElementById('salir').addEventListener('click', salir);
  dibujarRuta();
}

async function dibujarRuta() {
  if (!usuario) return;
  const rutas = RUTAS[usuario.rol];
  const actual = rutaActual();
  const encontrada = rutas.find(([ruta]) => ruta === actual) ?? rutas[0];

  for (const enlace of document.querySelectorAll('.menu a')) {
    if (enlace.dataset.ruta === encontrada[0]) enlace.setAttribute('aria-current', 'page');
    else enlace.removeAttribute('aria-current');
  }

  const contenido = document.getElementById('contenido');
  contenido.innerHTML = '<p class="etiqueta">Cargando…</p>';
  try {
    await encontrada[2](contenido, {
      usuario,
      // Las vistas lo llaman cuando cambian datos del usuario (perfil).
      actualizarUsuario: async () => {
        usuario = await api('/usuarios/me');
        mostrarApp();
      },
      salir,
    });
  } catch (error) {
    contenido.innerHTML = `<div class="vacio">No se pudo cargar esta sección: ${esc(error.message)}</div>`;
  }
}

function salir() {
  borrarToken();
  usuario = null;
  location.hash = '';
  mostrarIngreso();
}

window.addEventListener('hashchange', dibujarRuta);
window.addEventListener('sesion-vencida', () => { usuario = null; mostrarIngreso(); });

iniciar();
