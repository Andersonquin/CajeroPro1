// --- UTILIDADES ---
function alerta(msg, icon = 'info') {
    Swal.fire({ title: 'Cajero Virtual', text: msg, icon: icon, confirmButtonColor: '#3085d6' });
}

// --- LOGIN ---
async function login() {
    const id = document.getElementById('login-id').value;
    const pin = document.getElementById('login-pin').value;

    if (!id || !pin) return alerta("Completa todos los campos", "warning");

    const res = await fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ id, pin })
    });

    const data = await res.json();

    if (data.success) {
        document.getElementById('login-section').classList.add('hidden');
        document.getElementById('dashboard-section').classList.remove('hidden');
        document.getElementById('welcome-msg').innerText = data.msg;
        
        // Al loguear, cargamos los datos iniciales
        actualizarHistorial();
        // Nota: Si quieres que el saldo aparezca de entrada, 
        // podrías devolverlo también en el JSON de /login.
    } else {
        alerta(data.msg, 'error');
    }
}

// --- OPERACIONES (RETIRO, DEPÓSITO, TRANSFERENCIA) ---
async function operacion(accion) {
    const monto = parseFloat(document.getElementById('monto').value);
    const id_destino = document.getElementById('id_destino').value;

    if (!monto || monto <= 0) return alerta("Monto no válido", "warning");

    const res = await fetch('/operacion', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ accion, monto, id_destino })
    });

    const data = await res.json();

    if (data.success) {
        alerta(data.msg, 'success');
        // Actualizamos el saldo en pantalla dinámicamente
        document.getElementById('balance-display').innerText = `$${data.nuevo_saldo.toLocaleString('es-CO')}`;
        actualizarHistorial();
        
        // Limpiamos inputs
        document.getElementById('monto').value = '';
        document.getElementById('id_destino').value = '';
    } else {
        alerta(data.msg, 'error');
    }
}

// --- CARGAR HISTORIAL ---
async function actualizarHistorial() {
    const res = await fetch('/historial');
    const data = await res.json();

    if (data.success) {
        const tabla = document.getElementById('historial-tabla');
        tabla.innerHTML = ''; 
        
        data.historial.forEach(mov => {
            // Lógica de colores: Rojo para egresos, Verde para ingresos
            const esEgreso = mov.tipo.includes('Retiro') || mov.tipo.includes('enviada');
            const colorClase = esEgreso ? 'text-danger' : 'text-success';
            const simbolo = esEgreso ? '-' : '+';

            const row = `
                <tr>
                    <td><small class="text-muted">${mov.fecha}</small></td>
                    <td><strong>${mov.tipo}</strong></td>
                    <td class="${colorClase} fw-bold">${simbolo} $${mov.monto.toFixed(2)}</td>
                </tr>`;
            tabla.innerHTML += row;
        });
    }
}

// --- CERRAR SESIÓN ---
function logout() {
    window.location.href = '/logout';
}