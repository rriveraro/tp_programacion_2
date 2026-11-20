// Pantalla de ingreso: login y registro (endpoints /auth).

import { api, ingresar } from '../api.js';
import { datosDe, opcionesBarrio } from '../ui.js';

export function vistaIngreso(raiz, { alIngresar }) {
  raiz.innerHTML = `
    <div class="ingreso">
      <section class="cartel">
        <div class="marca"><img src="img/logo.png" alt="Yendog" class="logo"></div>
        <div>
          <h1>Tu perro sale a pasear.</h1>
          <p>Reservá un paseo y lo acepta un paseador de tu barrio.
             Si sos paseador, encontrá paseos cerca tuyo.</p>
        </div>
        <p class="etiqueta" style="color:inherit">Por ahora, solo en CABA y solo perros.</p>
      </section>
      <section class="formulario" id="formulario"></section>
    </div>`;

  const caja = raiz.querySelector('#formulario');
  mostrarLogin();

  function mostrarLogin() {
    caja.innerHTML = `
      <h2>Ingresá a tu cuenta</h2>
      <form id="form-login">
        <label>Email <input name="email" type="email" required autocomplete="email"></label>
        <label>Contraseña <input name="password" type="password" required autocomplete="current-password"></label>
        <p class="error-form" role="alert"></p>
        <button type="submit">Ingresar</button>
      </form>
      <p class="cambiar">¿No tenés cuenta? <button type="button" id="ir-registro">Creá una</button></p>`;

    caja.querySelector('#ir-registro').addEventListener('click', mostrarRegistro);
    const form = caja.querySelector('#form-login');
    form.addEventListener('submit', async (evento) => {
      evento.preventDefault();
      const { email, password } = datosDe(form);
      await enviar(form, () => ingresar(email, password));
    });
  }

  function mostrarRegistro() {
    caja.innerHTML = `
      <h2>Creá tu cuenta</h2>
      <form id="form-registro">
        <fieldset>
          <legend>¿Cómo vas a usar Yendog?</legend>
          <label class="opcion"><input type="radio" name="rol" value="DUENO" checked> Tengo perro</label>
          <label class="opcion"><input type="radio" name="rol" value="PASEADOR"> Soy paseador</label>
        </fieldset>
        <label>Nombre y apellido <input name="nombre" required minlength="2" maxlength="100" autocomplete="name"></label>
        <div class="fila">
          <label>DNI <input name="dni" required pattern="\\d{7,8}" inputmode="numeric" title="7 u 8 números, sin puntos"></label>
          <label>Fecha de nacimiento <input name="fecha_nacimiento" type="date" required></label>
        </div>
        <label>Email <input name="email" type="email" required autocomplete="email"></label>
        <label>Contraseña <span class="ayuda">Mínimo 8 caracteres.</span>
          <input name="password" type="password" required minlength="8" autocomplete="new-password"></label>
        <div class="fila">
          <label>Calle <input name="calle" required minlength="2" autocomplete="address-line1"></label>
          <label>Número <input name="numero" required maxlength="10"></label>
        </div>
        <label>Barrio
          <select name="barrio" required><option value="">Elegí tu barrio</option>${opcionesBarrio()}</select>
        </label>
        <p class="error-form" role="alert"></p>
        <button type="submit">Crear cuenta</button>
      </form>
      <p class="cambiar">¿Ya tenés cuenta? <button type="button" id="ir-login">Ingresá</button></p>`;

    caja.querySelector('#ir-login').addEventListener('click', mostrarLogin);
    const form = caja.querySelector('#form-registro');
    form.addEventListener('submit', async (evento) => {
      evento.preventDefault();
      const datos = datosDe(form);
      await enviar(form, async () => {
        await api('/auth/registro', { metodo: 'POST', cuerpo: datos });
        await ingresar(datos.email, datos.password);
      });
    });
  }

  // Envía un formulario: muestra el error abajo o, si sale bien, entra a la app.
  async function enviar(form, accion) {
    const boton = form.querySelector('button[type=submit]');
    const error = form.querySelector('.error-form');
    error.textContent = '';
    boton.disabled = true;
    try {
      await accion();
      alIngresar();
    } catch (e) {
      error.textContent = e.message;
      boton.disabled = false;
    }
  }
}
