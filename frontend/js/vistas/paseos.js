// Pantallas del paseador: paseos disponibles y mis paseos
// (/reservas/pendientes, /reservas/mias y las acciones sobre cada reserva).

import { api } from '../api.js';
import {
  avisar, chapita, conBoton, dinero, esc, nombreBarrio, nombreEstado, opcionesBarrio, turnoTexto,
} from '../ui.js';

const ganancia = (r) => Number(r.tarifa) - Number(r.comision);

export async function vistaDisponibles(contenedor, { usuario }) {
  contenedor.innerHTML = `
    <div class="encabezado">
      <h1>Paseos disponibles</h1>
      <p>Reservas que todavía nadie aceptó. Podés llevar hasta 4 perros en el mismo turno.
         Cuando aceptás, ves el domicilio del dueño.</p>
    </div>
    <label style="max-width:320px;margin-bottom:1rem">Barrio
      <select id="barrio">
        <option value="">Todos los barrios</option>
        ${opcionesBarrio(usuario.barrio)}
      </select>
    </label>
    <div class="lista" id="lista"></div>`;

  const lista = contenedor.querySelector('#lista');
  const barrio = contenedor.querySelector('#barrio');
  barrio.addEventListener('change', cargar);

  async function cargar() {
    const filtro = barrio.value ? `?barrio=${barrio.value}` : '';
    const reservas = await api(`/reservas/pendientes${filtro}`);
    if (reservas.length === 0) {
      lista.innerHTML = `<div class="vacio">No hay paseos pendientes${barrio.value ? ` en ${nombreBarrio(barrio.value)}` : ''}.
        Probá con otro barrio.</div>`;
      return;
    }
    lista.innerHTML = reservas.map((r) => `
      <article class="item" data-id="${r.id}">
        ${chapita(r.estado)}
        <div>
          <div class="titulo">${turnoTexto(r.turno)}</div>
          <div class="detalle">${nombreBarrio(r.barrio)}, paseo n.º ${r.id}</div>
          <div class="detalle">El dueño paga ${dinero(r.tarifa)}; la app se queda ${dinero(r.comision)}</div>
        </div>
        <span class="monto">Ganás ${dinero(ganancia(r))}</span>
          <div class="acciones">
          <button class="chico" data-accion="aceptar">Aceptar</button>
        </div>
      </article>`).join('');

    for (const boton of lista.querySelectorAll('[data-accion=aceptar]')) {
      const id = boton.closest('.item').dataset.id;
      boton.addEventListener('click', () => conBoton(boton, async () => {
        await api(`/reservas/${id}/aceptar`, { metodo: 'POST' });
        avisar('Paseo aceptado. Lo encontrás en Mis paseos.');
        await cargar();
      }));
    }
  }

  await cargar();
}

export async function vistaMisPaseos(contenedor) {
  contenedor.innerHTML = `
    <div class="encabezado">
      <h1>Mis paseos</h1>
      <p>Si retirás tu aceptación faltando menos de 30 minutos, se registra una penalidad.
         Cuando devolvés al perro, marcá el paseo como terminado.</p>
    </div>
    <div class="lista" id="lista"></div>`;
  const lista = contenedor.querySelector('#lista');

  async function cargar() {
    const reservas = await api('/reservas/mias');
    if (reservas.length === 0) {
      lista.innerHTML = '<div class="vacio">Todavía no aceptaste paseos. Buscalos en <a href="#/disponibles">Paseos disponibles</a>.</div>';
      return;
    }
    lista.innerHTML = reservas.map((r) => `
      <article class="item" data-id="${r.id}">
        ${chapita(r.estado)}
        <div>
          <div class="titulo">${turnoTexto(r.turno)}</div>
          <div class="detalle">${nombreBarrio(r.barrio)}, paseo n.º ${r.id}, ${nombreEstado(r.estado).toLowerCase()}${r.devolucion_tardia ? ', devuelto tarde' : ''}</div>
          <div class="detalle domicilio"></div>
        </div>
        <span class="monto">${dinero(ganancia(r))}</span>
          <div class="acciones">
          ${r.estado === 'ACEPTADA' ? `
            <button class="secundario chico" data-accion="domicilio">Ver domicilio</button>
            <button class="chico" data-accion="finalizar">Terminé el paseo</button>
            <button class="peligro chico" data-accion="retirar">Retirar aceptación</button>` : ''}
        </div>
      </article>`).join('');

    for (const fila of lista.querySelectorAll('.item')) {
      const id = fila.dataset.id;
      fila.querySelector('[data-accion=domicilio]')?.addEventListener('click', (e) => conBoton(e.currentTarget, async () => {
        const d = await api(`/reservas/${id}/domicilio`);
        fila.querySelector('.domicilio').innerHTML = `<strong>Retiro y devolución:</strong> ${esc(d.calle)} ${esc(d.numero)}, ${nombreBarrio(d.barrio)}`;
      }));
      fila.querySelector('[data-accion=finalizar]')?.addEventListener('click', (e) => conBoton(e.currentTarget, async () => {
        await api(`/reservas/${id}/finalizar`, { metodo: 'POST' });
        avisar('Paseo terminado. El dueño ya puede pagarlo.');
        await cargar();
      }));
      fila.querySelector('[data-accion=retirar]')?.addEventListener('click', (e) => {
        if (!confirm('¿Retirar tu aceptación? El paseo vuelve a quedar disponible para otros paseadores.')) return;
        conBoton(e.currentTarget, async () => {
          await api(`/reservas/${id}/retirar-aceptacion`, { metodo: 'POST' });
          avisar('Retiraste tu aceptación');
          await cargar();
        });
      });
    }
  }

  await cargar();
}
