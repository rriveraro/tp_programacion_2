// Comunicación con la API.
// El front lo sirve la misma API (en /app/), así que las rutas son relativas
// y no hace falta configurar CORS.

const CLAVE_TOKEN = 'yendog_token';

export function obtenerToken() {
  try { return localStorage.getItem(CLAVE_TOKEN); } catch { return null; }
}

export function guardarToken(token) {
  try { localStorage.setItem(CLAVE_TOKEN, token); } catch { /* sin storage */ }
}

export function borrarToken() {
  try { localStorage.removeItem(CLAVE_TOKEN); } catch { /* sin storage */ }
}

// Error con el código HTTP y un mensaje listo para mostrar.
export class ErrorApi extends Error {
  constructor(status, mensaje) {
    super(mensaje);
    this.status = status;
  }
}

// FastAPI devuelve {detail: "texto"} en nuestros errores y
// {detail: [{loc, msg}, ...]} cuando falla la validación (422).
function mensajeDeError(cuerpo, status) {
  const detalle = cuerpo && cuerpo.detail;
  if (typeof detalle === 'string') return detalle;
  if (Array.isArray(detalle)) {
    return detalle
      .map((e) => `${e.loc ? e.loc[e.loc.length - 1] : ''}: ${e.msg}`)
      .join('. ');
  }
  return `Error ${status}`;
}

// Llamada genérica. `cuerpo` se manda como JSON; `formulario` como
// form-urlencoded (lo usa el login de OAuth2).
export async function api(ruta, { metodo = 'GET', cuerpo, formulario } = {}) {
  const headers = {};
  const token = obtenerToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let body;
  if (cuerpo !== undefined) {
    headers['Content-Type'] = 'application/json';
    body = JSON.stringify(cuerpo);
  } else if (formulario) {
    body = new URLSearchParams(formulario);
  }

  const respuesta = await fetch(ruta, { method: metodo, headers, body });
  if (respuesta.status === 204) return null;

  const datos = await respuesta.json().catch(() => null);
  if (!respuesta.ok) {
    // Token vencido o usuario dado de baja: volvemos al ingreso.
    if (respuesta.status === 401 && token) {
      borrarToken();
      window.dispatchEvent(new Event('sesion-vencida'));
    }
    throw new ErrorApi(respuesta.status, mensajeDeError(datos, respuesta.status));
  }
  return datos;
}

export async function ingresar(email, password) {
  const datos = await api('/auth/login', {
    metodo: 'POST',
    formulario: { username: email, password },
  });
  guardarToken(datos.access_token);
}
