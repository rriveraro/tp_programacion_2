// Funciones chicas que usan todas las pantallas.

// Escapa texto antes de meterlo en innerHTML (evita inyectar HTML).
export function esc(valor) {
  return String(valor ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

export function avisar(mensaje, tipo = 'ok') {
  const caja = document.getElementById('avisos');
  const aviso = document.createElement('div');
  aviso.className = `aviso ${tipo === 'error' ? 'error' : ''}`;
  aviso.setAttribute('role', tipo === 'error' ? 'alert' : 'status');
  aviso.textContent = mensaje;
  caja.append(aviso);
  setTimeout(() => aviso.remove(), 4500);
}

// Ejecuta una acción de un botón: lo deshabilita mientras espera y
// muestra el error de la API si falla.
export async function conBoton(boton, accion) {
  boton.disabled = true;
  try {
    await accion();
  } catch (error) {
    avisar(error.message, 'error');
  } finally {
    boton.disabled = false;
  }
}

// Lee los campos de un <form> como objeto. Los vacíos quedan afuera.
export function datosDe(form) {
  const datos = {};
  for (const [clave, valor] of new FormData(form)) {
    if (valor !== '') datos[clave] = valor;
  }
  return datos;
}

// ---- Formatos ----

const pesos = new Intl.NumberFormat('es-AR', {
  style: 'currency', currency: 'ARS', maximumFractionDigits: 0,
});
export const dinero = (valor) => pesos.format(Number(valor));

export function fecha(iso) {
  if (!iso) return '';
  const [a, m, d] = iso.slice(0, 10).split('-');
  return `${d}/${m}/${a}`;
}
export const hora = (texto) => (texto ? texto.slice(0, 5) : '');
export const fechaHora = (iso) => (iso ? `${fecha(iso)} ${hora(iso.slice(11))}` : '');

export function edad(nacimiento) {
  const hoy = new Date();
  const n = new Date(`${nacimiento}T00:00:00`);
  let anios = hoy.getFullYear() - n.getFullYear();
  if (hoy < new Date(hoy.getFullYear(), n.getMonth(), n.getDate())) anios -= 1;
  return anios;
}

// Fecha local en formato AAAA-MM-DD (para inputs type=date).
export function hoyIso(dias = 0) {
  const d = new Date();
  d.setDate(d.getDate() + dias);
  const z = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${z(d.getMonth() + 1)}-${z(d.getDate())}`;
}
export function finDeMesIso() {
  const d = new Date();
  const ultimo = new Date(d.getFullYear(), d.getMonth() + 1, 0);
  const z = (n) => String(n).padStart(2, '0');
  return `${ultimo.getFullYear()}-${z(ultimo.getMonth() + 1)}-${z(ultimo.getDate())}`;
}

// ---- Textos de los enums del back ----

export const BARRIOS = [
  'AGRONOMIA', 'ALMAGRO', 'BALVANERA', 'BARRACAS', 'BELGRANO', 'BOEDO',
  'CABALLITO', 'CHACARITA', 'COGHLAN', 'COLEGIALES', 'CONSTITUCION', 'FLORES',
  'FLORESTA', 'LA_BOCA', 'LA_PATERNAL', 'LINIERS', 'MATADEROS', 'MONTE_CASTRO',
  'MONSERRAT', 'NUEVA_POMPEYA', 'NUNEZ', 'PALERMO', 'PARQUE_AVELLANEDA',
  'PARQUE_CHACABUCO', 'PARQUE_CHAS', 'PARQUE_PATRICIOS', 'PUERTO_MADERO',
  'RECOLETA', 'RETIRO', 'SAAVEDRA', 'SAN_CRISTOBAL', 'SAN_NICOLAS', 'SAN_TELMO',
  'VELEZ_SARSFIELD', 'VERSALLES', 'VILLA_CRESPO', 'VILLA_DEL_PARQUE',
  'VILLA_DEVOTO', 'VILLA_GENERAL_MITRE', 'VILLA_LUGANO', 'VILLA_LURO',
  'VILLA_ORTUZAR', 'VILLA_PUEYRREDON', 'VILLA_REAL', 'VILLA_RIACHUELO',
  'VILLA_SANTA_RITA', 'VILLA_SOLDATI', 'VILLA_URQUIZA',
];

const ESPECIALES = {
  AGRONOMIA: 'Agronomía', CONSTITUCION: 'Constitución', NUNEZ: 'Núñez',
  SAN_CRISTOBAL: 'San Cristóbal', SAN_NICOLAS: 'San Nicolás',
  VELEZ_SARSFIELD: 'Vélez Sarsfield', VILLA_ORTUZAR: 'Villa Ortúzar',
  VILLA_PUEYRREDON: 'Villa Pueyrredón',
};
export function nombreBarrio(valor) {
  if (!valor) return '';
  if (ESPECIALES[valor]) return ESPECIALES[valor];
  return valor.toLowerCase().split('_')
    .map((p) => (['del', 'la'].includes(p) ? p : p[0].toUpperCase() + p.slice(1)))
    .join(' ');
}
export function opcionesBarrio(seleccionado = '') {
  return BARRIOS.map((b) => `<option value="${b}" ${b === seleccionado ? 'selected' : ''}>${nombreBarrio(b)}</option>`).join('');
}

export const TAMANIOS = { PEQUEÑO: 'Pequeño', MEDIANO: 'Mediano', GRANDE: 'Grande' };
export const METODOS = { EFECTIVO: 'Efectivo', TRANSFERENCIA: 'Transferencia', TARJETA: 'Tarjeta' };
export const MOTIVOS = {
  CANCELACION_DUENO: 'Cancelaste tarde una reserva',
  CANCELACION_PASEADOR: 'Retiraste tarde una aceptación',
};

// La chapita con el estado (de una reserva o de un pago).
const TEXTO_ESTADO = {
  PENDIENTE: 'Pend.', ACEPTADA: 'Acept.', FINALIZADA: 'Final.',
  CANCELADA: 'Canc.', EXPIRADA: 'Venc.', APROBADO: 'Aprob.', RECHAZADO: 'Rech.',
};
const NOMBRE_ESTADO = {
  PENDIENTE: 'Pendiente', ACEPTADA: 'Aceptada', FINALIZADA: 'Finalizada',
  CANCELADA: 'Cancelada', EXPIRADA: 'Vencida', APROBADO: 'Aprobado', RECHAZADO: 'Rechazado',
};
export function chapita(estado) {
  return `<div class="chapita ${estado.toLowerCase()}" title="${NOMBRE_ESTADO[estado]}" aria-label="Estado: ${NOMBRE_ESTADO[estado]}">${TEXTO_ESTADO[estado]}</div>`;
}
export const nombreEstado = (estado) => NOMBRE_ESTADO[estado] ?? estado;

export function turnoTexto(turno) {
  return `${fecha(turno.fecha)}, de ${hora(turno.hora_inicio)} a ${hora(turno.hora_fin)}`;
}

// Envía un formulario: deshabilita el botón y muestra el error de la API
// en el <p class="error-form"> del mismo formulario.
export async function enviarFormulario(form, accion) {
  const boton = form.querySelector('button[type=submit]');
  const error = form.querySelector('.error-form');
  if (error) error.textContent = '';
  boton.disabled = true;
  try {
    await accion();
  } catch (e) {
    if (error) error.textContent = e.message;
    else avisar(e.message, 'error');
  } finally {
    boton.disabled = false;
  }
}
