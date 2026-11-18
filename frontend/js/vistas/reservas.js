// Mis reservas (dueño): crear, ver, cancelar y pagar
// (/reservas, /reservas/mias, /reservas/{id}/cancelar y /pagos).

import { api } from '../api.js';
import {
  avisar, chapita, conBoton, datosDe, dinero, enviarFormulario, esc, finDeMesIso,
  hoyIso, METODOS, nombreBarrio, nombreEstado, turnoTexto,
} from '../ui.js';
import { formularioPago } from './pagos.js';

export async function vistaReservas(contenedor) {
  contenedor.innerHTML = `
    <div class="encabezado">
      <h1>Mis reservas</h1>
      <p>Los paseos son entre las 8 y las 20 h, dentro del mes actual y con al menos
         2 horas de anticipación. Podés cancelar sin cargo hasta 30 minutos antes.</p>
    </div>
    <section class="panel">
      <h2>Reservar un paseo</h2>
      <form id="form-reserva"></form>
    </section>
    <div style="display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap">
      <h2>Tus paseos</h2>
      <label class="opcion"><input type="checkbox" id="solo-activas"> Solo pendientes y aceptadas</label>
    </div>
    <div class="lista" id="lista"></div>`;

  const form = contenedor.querySelector('#form-reserva');
  const lista = contenedor.querySelector('#lista');
  const soloActivas = contenedor.querySelector('#solo-activas');
  const mascotas = await api('/mascotas');
  const nombreMascota = (id) => mascotas.find((m) => m.id === id)?.nombre ?? `Mascota ${id}`;

  // ---- Formulario de reserva ----
  if (mascotas.length === 0) {
    form.outerHTML = '<div class="vacio">Primero registrá a tu perro en <a href="#/mascotas">Mis mascotas</a>.</div>';
  } else {
    form.innerHTML = `
      <div class="fila">
        <label>Perro
          <select name="mascota_id" required>
            ${mascotas.map((m) => `<option value="${m.id}">${esc(m.nombre)}</option>`).join('')}
          </select>
        </label>
        <label>Día <input name="fecha" type="date" required min="${hoyIso()}" max="${finDeMesIso()}"></label>
        <label>Sale a las <input name="hora_inicio" type="time" required min="08:00" max="19:00" value="10:00"></label>
        <label>Vuelve a las <input name="hora_fin" type="time" required min="09:00" max="20:00" value="11:00"></label>
      </div>
      <p class="error-form" role="alert"></p>
      <div><button type="submit">Reservar paseo</button></div>`;

    // Al elegir la salida, proponemos la vuelta una hora después.
    const inicio = form.querySelector('[name=hora_inicio]');
    const fin = form.querySelector('[name=hora_fin]');
    inicio.addEventListener('change', () => {
      const [h, m] = inicio.value.split(':').map(Number);
      if (!Number.isNaN(h)) fin.value = `${String(Math.min(h + 1, 20)).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
    });

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      enviarFormulario(form, async () => {
        const datos = datosDe(form);
        datos.mascota_id = Number(datos.mascota_id);
        const reserva = await api('/reservas', { metodo: 'POST', cuerpo: datos });
        avisar(`Paseo reservado para ${nombreMascota(reserva.mascota_id)}. Tarifa: ${dinero(reserva.tarifa)}`);
        await cargar();
      });
    });
  }

  // ---- Lista ----
  soloActivas.addEventListener('change', cargar);

  async function cargar() {
    const [reservas, pagos] = await Promise.all([
      api(`/reservas/mias?solo_activas=${soloActivas.checked}`),
      api('/pagos/mios'),
    ]);
    if (reservas.length === 0) {
      lista.innerHTML = '<div class="vacio">No tenés paseos en esta lista.</div>';
      return;
    }
    // El pago más reciente de cada reserva (la API los devuelve del más nuevo al más viejo).
    const pagoDe = (id) => pagos.find((p) => p.reserva_id === id);

    lista.innerHTML = reservas.map((r) => {
      const pago = pagoDe(r.id);
      return `
        <article class="item" data-id="${r.id}">
          ${chapita(r.estado)}
          <div>
            <div class="titulo">${esc(nombreMascota(r.mascota_id))}</div>
            <div class="detalle">${turnoTexto(r.turno)}, ${nombreBarrio(r.barrio)}</div>
            <div class="detalle">${nombreEstado(r.estado)}${r.paseador_id ? ', con paseador asignado' : ''}${r.devolucion_tardia ? ', devuelto tarde' : ''}</div>
            ${pago ? `<div class="detalle">Pago en ${METODOS[pago.metodo].toLowerCase()}: ${textoPago(pago)}</div>` : ''}
            <div class="pago-form"></div>
          </div>
          <span class="monto">${dinero(r.tarifa)}</span>
            <div class="acciones">
            ${['PENDIENTE', 'ACEPTADA'].includes(r.estado)
              ? '<button class="peligro chico" data-accion="cancelar">Cancelar</button>' : ''}
            ${r.estado === 'FINALIZADA' && (!pago || pago.estado === 'RECHAZADO')
              ? '<button class="chico" data-accion="pagar">Pagar</button>' : ''}
          </div>
        </article>`;
    }).join('');

    for (const fila of lista.querySelectorAll('.item')) {
      const reserva = reservas.find((r) => r.id === Number(fila.dataset.id));
      fila.querySelector('[data-accion=cancelar]')?.addEventListener('click', (e) => {
        if (!confirm('¿Cancelar este paseo? Si faltan menos de 30 minutos, se registra una penalidad.')) return;
        conBoton(e.currentTarget, async () => {
          await api(`/reservas/${reserva.id}/cancelar`, { metodo: 'POST' });
          avisar('Paseo cancelado');
          await cargar();
        });
      });
      fila.querySelector('[data-accion=pagar]')?.addEventListener('click', (e) => {
        e.currentTarget.remove();
        formularioPago(fila.querySelector('.pago-form'), reserva, cargar);
      });
    }
  }

  await cargar();
}

function textoPago(pago) {
  if (pago.estado === 'APROBADO') return 'aprobado';
  if (pago.estado === 'RECHAZADO') return 'rechazado, podés volver a pagar';
  return 'esperando que el paseador lo confirme';
}
