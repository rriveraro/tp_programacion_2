// Mis mascotas (dueño): listar, registrar, editar y borrar (/mascotas).

import { api } from '../api.js';
import {
  avisar, conBoton, datosDe, edad, enviarFormulario, esc, fecha, hoyIso, TAMANIOS,
} from '../ui.js';

export async function vistaMascotas(contenedor) {
  contenedor.innerHTML = `
    <div class="encabezado">
      <h1>Mis mascotas</h1>
      <p>Para reservar un paseo, tu perro tiene que tener la vacuna antirrábica vigente
         (aplicada hace menos de un año) el día del paseo.</p>
    </div>
    <section class="panel">
      <h2 id="titulo-form">Registrar un perro</h2>
      <form id="form-mascota"></form>
    </section>
    <h2>Tus perros</h2>
    <div class="lista" id="lista"></div>`;

  const form = contenedor.querySelector('#form-mascota');
  const titulo = contenedor.querySelector('#titulo-form');
  const lista = contenedor.querySelector('#lista');
  let editando = null; // mascota que se está editando, o null si es nueva

  function dibujarFormulario(m = {}) {
    form.innerHTML = `
      <div class="fila">
        <label>Nombre <input name="nombre" required value="${esc(m.nombre)}"></label>
        <label>Raza <input name="raza" required value="${esc(m.raza)}"></label>
      </div>
      <div class="fila">
        <label>Fecha de nacimiento <input name="fecha_nacimiento" type="date" required max="${hoyIso()}" value="${esc(m.fecha_nacimiento)}"></label>
        <label>Vacuna antirrábica <span class="ayuda">Fecha de la última dosis.</span>
          <input name="fecha_antirrabica" type="date" max="${hoyIso()}" value="${esc(m.fecha_antirrabica)}"></label>
      </div>
      <fieldset>
        <legend>Tamaño</legend>
        ${Object.entries(TAMANIOS).map(([valor, texto]) => `
          <label class="opcion"><input type="radio" name="tamaño" value="${valor}" required
            ${m['tamaño'] === valor ? 'checked' : ''}> ${texto}</label>`).join('')}
      </fieldset>
      <p class="error-form" role="alert"></p>
      <div>
        <button type="submit">${editando ? 'Guardar cambios' : 'Registrar perro'}</button>
        ${editando ? '<button type="button" class="secundario" id="cancelar-edicion">Cancelar</button>' : ''}
      </div>`;
    form.querySelector('#cancelar-edicion')?.addEventListener('click', () => {
      editando = null;
      titulo.textContent = 'Registrar un perro';
      dibujarFormulario();
    });
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    enviarFormulario(form, async () => {
      const datos = datosDe(form);
      if (editando) {
        await api(`/mascotas/${editando.id}`, { metodo: 'PATCH', cuerpo: datos });
        avisar(`Guardamos los cambios de ${datos.nombre}`);
      } else {
        await api('/mascotas', { metodo: 'POST', cuerpo: datos });
        avisar(`${datos.nombre} quedó registrado`);
      }
      editando = null;
      titulo.textContent = 'Registrar un perro';
      dibujarFormulario();
      await cargar();
    });
  });

  async function cargar() {
    const mascotas = await api('/mascotas');
    if (mascotas.length === 0) {
      lista.innerHTML = '<div class="vacio">Todavía no registraste ningún perro. Usá el formulario de arriba.</div>';
      return;
    }
    lista.innerHTML = mascotas.map((m) => `
      <article class="item" data-id="${m.id}">
        <div class="chapita finalizada" aria-hidden="true">${esc(m.nombre.slice(0, 2).toUpperCase())}</div>
        <div>
          <div class="titulo">${esc(m.nombre)}</div>
          <div class="detalle">${esc(m.raza)}, ${TAMANIOS[m['tamaño']].toLowerCase()}, ${edad(m.fecha_nacimiento)} años</div>
          <div class="detalle">${m.fecha_antirrabica
            ? `Antirrábica: ${fecha(m.fecha_antirrabica)}`
            : 'Sin vacuna antirrábica cargada'}</div>
        </div>
        <div class="acciones">
          <button class="secundario chico" data-accion="editar">Editar</button>
          <button class="peligro chico" data-accion="borrar">Borrar</button>
        </div>
      </article>`).join('');

    for (const fila of lista.querySelectorAll('.item')) {
      const mascota = mascotas.find((m) => m.id === Number(fila.dataset.id));
      fila.querySelector('[data-accion=editar]').addEventListener('click', () => {
        editando = mascota;
        titulo.textContent = `Editar a ${mascota.nombre}`;
        dibujarFormulario(mascota);
        form.scrollIntoView({ behavior: 'smooth' });
      });
      fila.querySelector('[data-accion=borrar]').addEventListener('click', (e) => {
        if (!confirm(`¿Borrar a ${mascota.nombre}?`)) return;
        conBoton(e.currentTarget, async () => {
          await api(`/mascotas/${mascota.id}`, { metodo: 'DELETE' });
          avisar(`${mascota.nombre} fue borrado`);
          await cargar();
        });
      });
    }
  }

  dibujarFormulario();
  await cargar();
}
