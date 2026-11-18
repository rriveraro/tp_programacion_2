// Mis penalidades (/reservas/penalidades/mias). En el MVP solo se registran.

import { api } from '../api.js';
import { dinero, fechaHora, MOTIVOS } from '../ui.js';

export async function vistaPenalidades(contenedor) {
  const penalidades = await api('/reservas/penalidades/mias');
  contenedor.innerHTML = `
    <div class="encabezado">
      <h1>Penalidades</h1>
      <p>Se registran cuando se cancela un paseo faltando menos de 30 minutos.
         Equivalen al 15 % de la tarifa. Por ahora no se cobran.</p>
    </div>
    <div class="lista">
      ${penalidades.length === 0
        ? '<div class="vacio">No tenés penalidades.</div>'
        : penalidades.map((p) => `
          <article class="item">
            <div class="chapita cancelada" aria-hidden="true">!</div>
            <div>
              <div class="titulo">${MOTIVOS[p.motivo] ?? p.motivo}</div>
              <div class="detalle">Paseo n.º ${p.reserva_id}, ${fechaHora(p.creada_en)}</div>
            </div>
            <span class="monto">${dinero(p.monto)}</span><div class="acciones"></div>
          </article>`).join('')}
    </div>`;
}
