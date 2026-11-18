// Mi perfil: ver y editar datos, cambiar contraseña y darse de baja
// (endpoints /usuarios/me y /auth/cambiar-password).

import { api } from '../api.js';
import {
  avisar, datosDe, enviarFormulario as enviar, esc, fecha, nombreBarrio, opcionesBarrio,
} from '../ui.js';

export async function vistaPerfil(contenedor, { usuario, actualizarUsuario, salir }) {
  contenedor.innerHTML = `
    <div class="encabezado">
      <h1>Mi perfil</h1>
      <p>Tu domicilio solo lo ve el paseador cuando acepta un paseo.
         Las reservas ya creadas guardan el domicilio que tenían.</p>
    </div>

    <section class="panel">
      <h2>Tus datos</h2>
      <p><strong>${esc(usuario.nombre)}</strong><br>
        ${esc(usuario.email)}<br>
        DNI ${esc(usuario.dni)}, nacido el ${fecha(usuario.fecha_nacimiento)}<br>
        ${esc(usuario.calle)} ${esc(usuario.numero)}, ${nombreBarrio(usuario.barrio)}</p>
    </section>

    <section class="panel">
      <h2>Editar nombre o domicilio</h2>
      <form id="form-datos">
        <label>Nombre y apellido <input name="nombre" value="${esc(usuario.nombre)}" minlength="2"></label>
        <div class="fila">
          <label>Calle <input name="calle" value="${esc(usuario.calle)}" minlength="2"></label>
          <label>Número <input name="numero" value="${esc(usuario.numero)}"></label>
          <label>Barrio <select name="barrio">${opcionesBarrio(usuario.barrio)}</select></label>
        </div>
        <p class="error-form" role="alert"></p>
        <div><button type="submit">Guardar cambios</button></div>
      </form>
    </section>

    <section class="panel">
      <h2>Cambiar contraseña</h2>
      <form id="form-clave">
        <div class="fila">
          <label>Contraseña actual <input name="password_actual" type="password" required autocomplete="current-password"></label>
          <label>Contraseña nueva <input name="password_nueva" type="password" required minlength="8" autocomplete="new-password"></label>
        </div>
        <p class="error-form" role="alert"></p>
        <div><button type="submit">Cambiar contraseña</button></div>
      </form>
    </section>

    <section class="panel">
      <h2>Darte de baja</h2>
      <p>No vas a poder volver a ingresar. Si tenés reservas pendientes o aceptadas, primero cancelalas.</p>
      <p class="error-form" role="alert" id="error-baja"></p>
      <button class="peligro" id="baja">Darme de baja</button>
    </section>`;

  const formDatos = contenedor.querySelector('#form-datos');
  formDatos.addEventListener('submit', (e) => {
    e.preventDefault();
    enviar(formDatos, async () => {
      await api('/usuarios/me', { metodo: 'PATCH', cuerpo: datosDe(formDatos) });
      avisar('Datos guardados');
      await actualizarUsuario();
    });
  });

  const formClave = contenedor.querySelector('#form-clave');
  formClave.addEventListener('submit', (e) => {
    e.preventDefault();
    enviar(formClave, async () => {
      await api('/auth/cambiar-password', { metodo: 'POST', cuerpo: datosDe(formClave) });
      formClave.reset();
      avisar('Contraseña cambiada');
    });
  });

  contenedor.querySelector('#baja').addEventListener('click', async () => {
    if (!confirm('¿Seguro que querés darte de baja?')) return;
    try {
      await api('/usuarios/me', { metodo: 'DELETE' });
      salir();
    } catch (error) {
      contenedor.querySelector('#error-baja').textContent = error.message;
    }
  });
}

