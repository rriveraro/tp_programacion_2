// Pagos (/pagos y /pagos/mios).
// El dueño paga desde "Mis reservas" (formularioPago) y ve acá su historial.
// El paseador confirma o rechaza los cobros en efectivo o transferencia.

import { api } from '../api.js';
import {
  avisar, chapita, conBoton, datosDe, dinero, enviarFormulario, fechaHora, METODOS, nombreEstado,
} from '../ui.js';

// Números de tarjeta de prueba (config.py del back).
const TARJETA_APROBADA = '4111111111111111';
const TARJETA_RECHAZADA = '4000000000000002';

export function formularioPago(contenedor, reserva, alPagar) {
  contenedor.innerHTML = `
    <form class="panel" style="margin:0.75rem 0 0">
      <fieldset>
        <legend>¿Cómo pagás ${dinero(reserva.tarifa)}?</legend>
        ${Object.entries(METODOS).map(([valor, texto], i) => `
          <label class="opcion"><input type="radio" name="metodo" value="${valor}" ${i === 0 ? 'checked' : ''}> ${texto}</label>`).join('')}
      </fieldset>
      <label class="oculto" id="campo-tarjeta">Número de tarjeta
        <span class="ayuda">Es una prueba: ${TARJETA_APROBADA} se aprueba y ${TARJETA_RECHAZADA} se rechaza. No se guarda.</span>
        <input name="numero_tarjeta" inputmode="numeric" pattern="\\d{12,19}" autocomplete="off">
      </label>
      <p class="error-form" role="alert"></p>
      <div><button type="submit">Pagar</button></div>
    </form>`;

  const form = contenedor.querySelector('form');
  const campoTarjeta = form.querySelector('#campo-tarjeta');
  const inputTarjeta = campoTarjeta.querySelector('input');
  form.addEventListener('change', () => {
    const conTarjeta = form.metodo.value === 'TARJETA';
    campoTarjeta.classList.toggle('oculto', !conTarjeta);
    inputTarjeta.required = conTarjeta;
  });

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    enviarFormulario(form, async () => {
      const datos = datosDe(form);
      if (datos.metodo !== 'TARJETA') delete datos.numero_tarjeta;
      const pago = await api('/pagos', {
        metodo: 'POST', cuerpo: { ...datos, reserva_id: reserva.id },
      });
      const mensajes = {
        APROBADO: 'Pago aprobado',
        RECHAZADO: 'La tarjeta fue rechazada. Probá con otro medio.',
        PENDIENTE: 'Pago registrado. El paseador tiene que confirmarlo.',
      };
      avisar(mensajes[pago.estado], pago.estado === 'RECHAZADO' ? 'error' : 'ok');
      await alPagar();
    });
  });
}

export async function vistaPagos(contenedor, { usuario }) {
  const esPaseador = usuario.rol === 'PASEADOR';
  contenedor.innerHTML = `
    <div class="encabezado">
      <h1>${esPaseador ? 'Cobros' : 'Pagos'}</h1>
      <p>${esPaseador
        ? 'Los pagos con tarjeta se resuelven solos. Los de efectivo y transferencia los confirmás vos cuando te llega la plata.'
        : 'Pagás desde Mis reservas cuando el paseo termina. Acá ves el estado de cada pago.'}</p>
    </div>
    <div class="lista" id="lista"></div>`;
  const lista = contenedor.querySelector('#lista');

  async function cargar() {
    const pagos = await api('/pagos/mios');
    if (pagos.length === 0) {
      lista.innerHTML = `<div class="vacio">${esPaseador ? 'Todavía no tenés cobros.' : 'Todavía no hiciste pagos.'}</div>`;
      return;
    }
    lista.innerHTML = pagos.map((p) => {
      // Solo el paseador confirma, y solo efectivo o transferencia que no estén aprobados.
      const confirmable = esPaseador && p.metodo !== 'TARJETA' && p.estado !== 'APROBADO';
      return `
        <article class="item" data-id="${p.id}">
          ${chapita(p.estado)}
          <div>
            <div class="titulo">${METODOS[p.metodo]}, paseo n.º ${p.reserva_id}</div>
            <div class="detalle">${nombreEstado(p.estado)}, ${fechaHora(p.creado_en)}</div>
          </div>
          <span class="monto">${dinero(p.monto)}</span>
            <div class="acciones">
            ${confirmable ? `
              <button class="chico" data-aprobar="true">Recibí el pago</button>
              ${p.estado === 'PENDIENTE' ? '<button class="peligro chico" data-aprobar="false">No lo recibí</button>' : ''}` : ''}
          </div>
        </article>`;
    }).join('');

    for (const boton of lista.querySelectorAll('[data-aprobar]')) {
      const id = boton.closest('.item').dataset.id;
      boton.addEventListener('click', () => conBoton(boton, async () => {
        const aprobar = boton.dataset.aprobar === 'true';
        await api(`/pagos/${id}/confirmar`, { metodo: 'POST', cuerpo: { aprobar } });
        avisar(aprobar ? 'Pago confirmado' : 'Pago marcado como no recibido');
        await cargar();
      }));
    }
  }

  await cargar();
}
