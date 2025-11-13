async function loadPlayers() {
    try {
        const response = await fetch('/players');
        const data = await response.json();

        let html = `<p><strong>Total Players: ${data.count}</strong></p>`;
        html += '<table><thead><tr><th>Player Name</th><th>Status</th></tr></thead><tbody>';

        for (const [_name, player] of Object.entries(data.players)) {
            const statusClass = player.online ? 'online' : 'offline';
            const statusText = player.online ? 'Online' : 'Offline';
            html += `<tr><td>${player.name}</td><td class="${statusClass}">${statusText}</td></tr>`;
        }

        html += '</tbody></table>';
        document.getElementById('players-container').innerHTML = html;
    } catch (error) {
        console.error('Error loading players:', error);
        document.getElementById('players-container').innerHTML = '<p>Error loading players</p>';
    }
}

async function loadAdmins() {
    try {
        const response = await fetch('/admins');
        const admins = await response.json();

        let html = `<p><strong>Total Admins: ${admins.length}</strong></p>`;
        html += '<table><thead><tr><th>Admin Name</th><th>Status</th></tr></thead><tbody>';

        for (const admin of admins) {
            const statusClass = admin.online ? 'online' : 'offline';
            const statusText = admin.online ? 'Online' : 'Offline';
            html += `<tr><td>${admin.name}</td><td class="${statusClass}">${statusText}</td></tr>`;
        }

        html += '</tbody></table>';
        document.getElementById('admins-container').innerHTML = html;
    } catch (error) {
        console.error('Error loading admins:', error);
        document.getElementById('admins-container').innerHTML = '<p>Error loading admins</p>';
    }
}

async function loadFooterInfo() {
    try {
        const [seedResponse, uptimeResponse] = await Promise.all([
            fetch('/seed'),
            fetch('/uptime')
        ]);

        const seed = await seedResponse.json();
        const uptime = await uptimeResponse.json();

        let uptimeText = '';
        if (uptime.hours) uptimeText += `${uptime.hours}h `;
        if (uptime.minutes) uptimeText += `${uptime.minutes}m `;
        if (uptime.seconds) uptimeText += `${uptime.seconds}s`;

        const html = `
            <div class="footer-content">
                <span><strong>Seed:</strong> ${seed}</span>
                <span><strong>Game Time:</strong> ${uptimeText}</span>
            </div>
        `;

        document.getElementById('server-info').innerHTML = html;
    } catch (error) {
        console.error('Error loading footer info:', error);
        document.getElementById('server-info').innerHTML = '<p>Error loading server info</p>';
    }
}

// Load immediately and then every 5 seconds
loadPlayers();
setInterval(loadPlayers, 5000);

loadAdmins();
setInterval(loadAdmins, 5000);

loadFooterInfo();
setInterval(loadFooterInfo, 10000);

// RCON command form handler
document.getElementById('rcon-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const commandInput = document.getElementById('rcon-command');
    const resultPre = document.getElementById('rcon-result');
    const command = commandInput.value.trim();

    if (!command) return;

    resultPre.textContent = 'Executing...';

    try {
        const response = await fetch('/rcon', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command: command }),
        });

        const data = await response.json();

        if (response.ok) {
            resultPre.textContent = data.result;
        } else {
            resultPre.textContent = `Error: ${data.detail || 'Unknown error'}`;
        }
    } catch (error) {
        console.error('Error executing RCON command:', error);
        resultPre.textContent = `Error: ${error.message}`;
    }
});
