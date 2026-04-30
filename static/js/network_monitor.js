/**
 * Cyber Nexus Network Monitor - Wireshark-style Packet Capture
 * Real-time network packet analysis with cyberpunk interface
 */

class NetworkMonitor {
    constructor() {
        this.updateInterval = 5000; // Update every 5 seconds
        this.isMonitoring = false;
        this.isCapturing = false;
        this.metrics = {};
        this.connections = [];
        this.alerts = [];
        this.packets = [];
        this.selectedPacket = null;
        this.packetCount = 0;
        this.bytesCaptured = 0;
        this.startTime = null;
        this.captureInterval = null;
        this.runtimeInterval = null;
        this.packetFilter = '';
        this.currentInterface = 'eth0';
    }

    async init() {
        try {
            console.log('Initializing Cyber Nexus Network Monitor...');
            this.setupEventListeners();
            this.initializePacketCapture();
            this.addTerminalLine('[CYBER NEXUS] Network monitoring system initialized', 'system');
            this.addTerminalLine('[CYBER NEXUS] Ready for packet capture operations', 'system');
        } catch (error) {
            console.error('Error initializing network monitor:', error);
        }
    }

    setupEventListeners() {
        // Packet capture controls
        const startCaptureBtn = document.getElementById('start-capture');
        const stopCaptureBtn = document.getElementById('stop-capture');
        const restartCaptureBtn = document.getElementById('restart-capture');
        const saveCaptureBtn = document.getElementById('save-capture');
        const packetFilterInput = document.getElementById('packet-filter');
        const interfaceSelect = document.getElementById('interface-select');

        if (startCaptureBtn) {
            startCaptureBtn.addEventListener('click', () => this.startPacketCapture());
        }
        if (stopCaptureBtn) {
            stopCaptureBtn.addEventListener('click', () => this.stopPacketCapture());
        }
        if (restartCaptureBtn) {
            restartCaptureBtn.addEventListener('click', () => this.restartPacketCapture());
        }
        if (saveCaptureBtn) {
            saveCaptureBtn.addEventListener('click', () => this.saveCapture());
        }
        if (packetFilterInput) {
            packetFilterInput.addEventListener('input', (e) => this.applyPacketFilter(e.target.value));
        }
        if (interfaceSelect) {
            interfaceSelect.addEventListener('change', (e) => this.changeInterface(e.target.value));
        }

        // Packet list click handler
        const packetList = document.getElementById('packet-list');
        if (packetList) {
            packetList.addEventListener('click', (e) => {
                const row = e.target.closest('tr');
                if (row && row.dataset.packetId) {
                    this.selectPacket(parseInt(row.dataset.packetId));
                }
            });
        }
    }

    // Wireshark-style Packet Capture Methods
    initializePacketCapture() {
        this.updateCaptureStatus();
        this.updateMetrics();
    }

    startPacketCapture() {
        if (this.isCapturing) {
            this.addTerminalLine('[WARNING] Packet capture already running', 'warning');
            return;
        }

        this.isCapturing = true;
        this.startTime = Date.now();
        this.packetCount = 0;
        this.bytesCaptured = 0;
        this.packets = [];
        
        this.addTerminalLine('[CAPTURE] Starting packet capture on ' + this.currentInterface, 'success');
        this.updateCaptureStatus();
        this.startPacketGeneration();
        
        // Start real-time updates
        this.captureInterval = setInterval(() => {
            this.updateMetrics();
        }, 1000);
        
        // Start runtime update interval
        this.runtimeInterval = setInterval(() => {
            this.updateRuntime();
        }, 1000);
    }

    stopPacketCapture() {
        if (!this.isCapturing) {
            this.addTerminalLine('[WARNING] No capture in progress', 'warning');
            return;
        }

        this.isCapturing = false;
        if (this.captureInterval) {
            clearInterval(this.captureInterval);
            this.captureInterval = null;
        }
        if (this.runtimeInterval) {
            clearInterval(this.runtimeInterval);
            this.runtimeInterval = null;
        }

        const duration = this.formatDuration(Date.now() - this.startTime);
        this.addTerminalLine('[CAPTURE] Stopped packet capture', 'success');
        this.addTerminalLine('[STATS] ' + this.packetCount + ' packets captured in ' + duration, 'info');
        this.updateCaptureStatus();
    }

    restartPacketCapture() {
        this.stopPacketCapture();
        setTimeout(() => {
            this.startPacketCapture();
        }, 100);
    }

    generatePacket() {
        const protocols = ['TCP', 'UDP', 'ICMP', 'ARP', 'DNS', 'HTTP', 'HTTPS', 'FTP', 'SSH'];
        const protocol = protocols[Math.floor(Math.random() * protocols.length)];
        
        const packet = {
            id: ++this.packetCount,
            timestamp: new Date(),
            time: this.formatTime(new Date()),
            source: this.generateRandomIP(),
            destination: this.generateRandomIP(),
            protocol: protocol,
            length: Math.floor(Math.random() * 1500) + 64,
            info: this.generatePacketInfo(protocol)
        };

        this.packets.push(packet);
        this.bytesCaptured += packet.length;

        // Keep only last 1000 packets
        if (this.packets.length > 1000) {
            this.packets.shift();
        }

        this.addPacketToList(packet);
        this.updatePacketCount();
    }

    startPacketGeneration() {
        console.log('Starting real-time packet generation...');
        
        // Generate some initial packets immediately
        for (let i = 0; i < 5; i++) {
            this.generatePacket();
        }
        this.updatePacketList();
        this.updateMetrics();
        
        // Generate packets every 2 seconds for real-time effect
        this.packetGenerationInterval = setInterval(() => {
            if (this.isCapturing) {
                this.generatePacket();
                this.updatePacketList();
                this.updateMetrics();
            }
        }, 2000);
        
        console.log('Real-time packet generation started');
    }

    generateRandomIP() {
        return Math.floor(Math.random() * 256) + '.' +
               Math.floor(Math.random() * 256) + '.' +
               Math.floor(Math.random() * 256) + '.' +
               Math.floor(Math.random() * 256);
    }

    generatePacketInfo(protocol) {
        const infos = {
            'TCP': ['SYN', 'ACK', 'FIN', 'RST', 'PSH, ACK'],
            'UDP': ['DNS Query', 'DNS Response', 'DHCP', 'SNMP'],
            'ICMP': ['Echo (ping) request', 'Echo (ping) reply', 'Destination unreachable'],
            'ARP': ['Who has 192.168.1.1? Tell 192.168.1.100', '192.168.1.1 is at 00:11:22:33:44:55'],
            'DNS': ['Standard query 0x1234 A google.com', 'Standard query response 0x1234 A 172.217.12.206'],
            'HTTP': ['GET / HTTP/1.1', 'HTTP/1.1 200 OK', 'POST /api/data HTTP/1.1'],
            'HTTPS': ['TLSv1.2 Client Hello', 'TLSv1.2 Server Hello', 'Application Data'],
            'FTP': ['220 (vsFTPd 3.0.3)', 'USER anonymous', 'PASS guest@example.com'],
            'SSH': ['SSH-2.0-OpenSSH_8.2p1', 'Key exchange init', 'New keys']
        };

        const protocolInfos = infos[protocol] || ['Data packet'];
        return protocolInfos[Math.floor(Math.random() * protocolInfos.length)];
    }

    formatTime(date) {
        return date.toTimeString().split(' ')[0] + '.' + 
               String(date.getMilliseconds()).padStart(3, '0');
    }

    formatDuration(ms) {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        
        if (hours > 0) {
            return hours + ':' + String(minutes % 60).padStart(2, '0') + ':' + String(seconds % 60).padStart(2, '0');
        } else {
            return String(minutes).padStart(2, '0') + ':' + String(seconds % 60).padStart(2, '0');
        }
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    addPacketToList(packet) {
        const packetList = document.getElementById('packet-list');
        if (!packetList) return;

        // Apply filter if set
        if (this.packetFilter && !this.packetMatchesFilter(packet)) {
            return;
        }

        const row = document.createElement('tr');
        row.dataset.packetId = packet.id;
        row.className = 'protocol-' + packet.protocol.toLowerCase();
        
        row.innerHTML = `
            <td>${packet.id}</td>
            <td>${packet.time}</td>
            <td>${packet.source}</td>
            <td>${packet.destination}</td>
            <td class="protocol-${packet.protocol.toLowerCase()}">${packet.protocol}</td>
            <td>${packet.length}</td>
            <td>${packet.info}</td>
        `;

        // Add to top of list
        packetList.insertBefore(row, packetList.firstChild);

        // Limit displayed packets
        while (packetList.children.length > 100) {
            packetList.removeChild(packetList.lastChild);
        }
    }

    packetMatchesFilter(packet) {
        if (!this.packetFilter) return true;
        
        const filter = this.packetFilter.toLowerCase();
        return packet.protocol.toLowerCase().includes(filter) ||
               packet.source.includes(filter) ||
               packet.destination.includes(filter) ||
               packet.info.toLowerCase().includes(filter);
    }

    applyPacketFilter(filter) {
        this.packetFilter = filter;
        this.refreshPacketList();
    }

    refreshPacketList() {
        const packetList = document.getElementById('packet-list');
        if (!packetList) return;

        packetList.innerHTML = '';
        this.packets.forEach(packet => {
            if (this.packetMatchesFilter(packet)) {
                this.addPacketToList(packet);
            }
        });
    }

    selectPacket(packetId) {
        // Remove previous selection
        const previousSelected = document.querySelector('.packet-table tr.selected');
        if (previousSelected) {
            previousSelected.classList.remove('selected');
        }

        // Add selection to clicked row
        const selectedRow = document.querySelector(`tr[data-packet-id="${packetId}"]`);
        if (selectedRow) {
            selectedRow.classList.add('selected');
        }

        // Find packet data
        this.selectedPacket = this.packets.find(p => p.id === packetId);
        if (this.selectedPacket) {
            this.displayPacketDetails(this.selectedPacket);
            this.displayHexDump(this.selectedPacket);
        }
    }

    displayPacketDetails(packet) {
        const packetTree = document.getElementById('packet-tree');
        if (!packetTree) return;

        packetTree.innerHTML = `
            <div class="tree-node">
                <div class="tree-label">Frame</div>
                <div class="tree-value">${packet.length} bytes on wire</div>
            </div>
            <div class="tree-node">
                <div class="tree-label">Ethernet II</div>
                <div class="tree-value">Src: ${packet.source}, Dst: ${packet.destination}</div>
            </div>
            <div class="tree-node">
                <div class="tree-label">Internet Protocol</div>
                <div class="tree-value">Src: ${packet.source}, Dst: ${packet.destination}</div>
            </div>
            <div class="tree-node">
                <div class="tree-label">${packet.protocol}</div>
                <div class="tree-value">${packet.info}</div>
            </div>
            <div class="tree-node">
                <div class="tree-label">Timestamp</div>
                <div class="tree-value">${packet.timestamp.toISOString()}</div>
            </div>
        `;
    }

    displayHexDump(packet) {
        const hexDump = document.getElementById('hex-dump');
        if (!hexDump) return;

        // Generate realistic hex dump
        const hexData = this.generateHexData(packet.length);
        const asciiData = this.generateAsciiData(hexData);
        
        let dump = '';
        for (let i = 0; i < hexData.length; i += 16) {
            const offset = i.toString(16).padStart(4, '0').toUpperCase();
            const hex = hexData.substr(i, 16).match(/.{1,2}/g).join(' ').padEnd(47);
            const ascii = asciiData.substr(i, 16);
            dump += `${offset}   ${hex}   ${ascii}\n`;
        }

        hexDump.textContent = dump;
    }

    generateHexData(length) {
        let hex = '';
        for (let i = 0; i < length; i++) {
            hex += Math.floor(Math.random() * 256).toString(16).padStart(2, '0');
        }
        return hex;
    }

    generateAsciiData(hex) {
        let ascii = '';
        for (let i = 0; i < hex.length; i += 2) {
            const code = parseInt(hex.substr(i, 2), 16);
            ascii += (code >= 32 && code <= 126) ? String.fromCharCode(code) : '.';
        }
        return ascii;
    }

    updateCaptureStatus() {
        const statusElement = document.getElementById('capture-status');
        if (statusElement) {
            if (this.isCapturing) {
                statusElement.textContent = '● Capturing';
                statusElement.className = 'status-indicator online';
            } else {
                statusElement.textContent = '● Stopped';
                statusElement.className = 'status-indicator offline';
            }
        }
    }

    updatePacketCount() {
        const countElement = document.getElementById('packet-count');
        if (countElement) {
            countElement.textContent = this.packets.length + ' packets';
        }
    }

    updateRuntime() {
        // Update running time
        const runningTime = document.getElementById('running-time');
        if (runningTime && this.startTime) {
            runningTime.textContent = this.formatDuration(Date.now() - this.startTime);
        }
    }

    updateMetrics() {
        // Update packet count
        const packetsCaptured = document.getElementById('packets-captured');
        if (packetsCaptured) {
            packetsCaptured.textContent = this.packetCount.toLocaleString();
        }

        // Update bytes captured
        const bytesCaptured = document.getElementById('bytes-captured');
        if (bytesCaptured) {
            bytesCaptured.textContent = this.formatBytes(this.bytesCaptured);
        }

        // Update packets per second
        const packetsPerSec = document.getElementById('packets-per-sec');
        if (packetsPerSec && this.startTime) {
            const elapsed = (Date.now() - this.startTime) / 1000;
            const pps = Math.round(this.packetCount / elapsed);
            packetsPerSec.textContent = pps.toLocaleString();
        }

        // Update dropped packets (simulate)
        const droppedPackets = document.getElementById('dropped-packets');
        if (droppedPackets) {
            const dropped = Math.floor(this.packetCount * 0.001); // 0.1% drop rate
            droppedPackets.textContent = dropped.toLocaleString();
        }
    }

    changeInterface(interfaceName) {
        this.currentInterface = interfaceName;
        this.addTerminalLine('[INTERFACE] Changed to ' + interfaceName, 'info');
        
        if (this.isCapturing) {
            this.restartPacketCapture();
        }
    }

    saveCapture() {
        if (this.packets.length === 0) {
            this.addTerminalLine('[ERROR] No packets to save', 'error');
            return;
        }

        const captureData = {
            timestamp: new Date().toISOString(),
            interface: this.currentInterface,
            packetCount: this.packets.length,
            bytesCaptured: this.bytesCaptured,
            packets: this.packets
        };

        const blob = new Blob([JSON.stringify(captureData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `capture_${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);

        this.addTerminalLine('[SAVE] Capture saved to file', 'success');
    }

    addTerminalLine(text, className = '') {
        const terminalOutput = document.getElementById('terminal-output');
        if (!terminalOutput) return;

        const line = document.createElement('div');
        line.className = `terminal-line ${className}`;
        line.textContent = text;

        // Remove cursor if exists
        const cursorLine = terminalOutput.querySelector('.cursor');
        if (cursorLine) {
            cursorLine.remove();
        }

        terminalOutput.appendChild(line);

        // Add cursor back
        const cursor = document.createElement('div');
        cursor.className = 'terminal-line cursor';
        cursor.textContent = 'root@cybernexus:~# _';
        terminalOutput.appendChild(cursor);

        terminalOutput.scrollTop = terminalOutput.scrollHeight;

        // Keep terminal clean
        const lines = terminalOutput.querySelectorAll('.terminal-line');
        if (lines.length > 50) {
            lines[0].remove();
        }
    }
}

// Terminal command handler
function handleTerminalCommand(event) {
    if (event.key === 'Enter') {
        const input = event.target;
        const command = input.value.trim();
        
        if (command) {
            // Add command to terminal
            const terminalOutput = document.getElementById('terminal-output');
            const commandLine = document.createElement('div');
            commandLine.className = 'terminal-line command';
            commandLine.textContent = `root@cybernexus:~# ${command}`;
            
            // Remove cursor
            const cursor = terminalOutput.querySelector('.cursor');
            if (cursor) cursor.remove();
            
            // Add command
            terminalOutput.appendChild(commandLine);
            
            // Execute command
            executeTerminalCommand(command);
            
            // Clear input
            input.value = '';
            
            // Add cursor back
            const newCursor = document.createElement('div');
            newCursor.className = 'terminal-line cursor';
            newCursor.textContent = 'root@cybernexus:~# _';
            terminalOutput.appendChild(newCursor);
            
            terminalOutput.scrollTop = terminalOutput.scrollHeight;
        }
    }
}

function executeTerminalCommand(command) {
    const parts = command.toLowerCase().split(' ');
    const cmd = parts[0];
    const args = parts.slice(1);
    
    const networkMonitor = window.networkMonitor;
    if (!networkMonitor) return;
    
    switch(cmd) {
        case 'help':
            networkMonitor.addTerminalLine('Available commands:', 'info');
            networkMonitor.addTerminalLine('  start     - Start packet capture', 'info');
            networkMonitor.addTerminalLine('  stop      - Stop packet capture', 'info');
            networkMonitor.addTerminalLine('  restart   - Restart packet capture', 'info');
            networkMonitor.addTerminalLine('  status    - Show capture status', 'info');
            networkMonitor.addTerminalLine('  clear     - Clear terminal', 'info');
            networkMonitor.addTerminalLine('  save      - Save capture to file', 'info');
            networkMonitor.addTerminalLine('  filter    - Set packet filter', 'info');
            networkMonitor.addTerminalLine('  interface - Change network interface', 'info');
            break;
            
        case 'start':
            networkMonitor.startPacketCapture();
            break;
            
        case 'stop':
            networkMonitor.stopPacketCapture();
            break;
            
        case 'restart':
            networkMonitor.restartPacketCapture();
            break;
            
        case 'status':
            const status = networkMonitor.isCapturing ? 'Capturing' : 'Stopped';
            networkMonitor.addTerminalLine(`Capture Status: ${status}`, 'info');
            networkMonitor.addTerminalLine(`Packets Captured: ${networkMonitor.packetCount}`, 'info');
            networkMonitor.addTerminalLine(`Interface: ${networkMonitor.currentInterface}`, 'info');
            if (networkMonitor.startTime) {
                const duration = networkMonitor.formatDuration(Date.now() - networkMonitor.startTime);
                networkMonitor.addTerminalLine(`Running Time: ${duration}`, 'info');
            }
            break;
            
        case 'clear':
            const terminalOutput = document.getElementById('terminal-output');
            if (terminalOutput) {
                terminalOutput.innerHTML = '';
                networkMonitor.addTerminalLine('[TERMINAL] Terminal cleared', 'info');
            }
            break;
            
        case 'save':
            networkMonitor.saveCapture();
            break;
            
        case 'filter':
            if (args.length > 0) {
                const filter = args.join(' ');
                document.getElementById('packet-filter').value = filter;
                networkMonitor.applyPacketFilter(filter);
                networkMonitor.addTerminalLine(`Filter applied: ${filter}`, 'success');
            } else {
                networkMonitor.addTerminalLine('Usage: filter <expression>', 'warning');
            }
            break;
            
        case 'interface':
            if (args.length > 0) {
                const interfaceName = args[0];
                const interfaceSelect = document.getElementById('interface-select');
                if (interfaceSelect) {
                    interfaceSelect.value = interfaceName;
                    networkMonitor.changeInterface(interfaceName);
                }
            } else {
                networkMonitor.addTerminalLine('Usage: interface <name>', 'warning');
                networkMonitor.addTerminalLine('Available interfaces: eth0, wlan0, lo, any', 'info');
            }
            break;
            
        default:
            networkMonitor.addTerminalLine(`Command not found: ${cmd}`, 'error');
            networkMonitor.addTerminalLine('Type "help" for available commands', 'info');
    }
}

// Global functions for HTML onclick handlers
function clearTerminal() {
    const networkMonitor = window.networkMonitor;
    if (networkMonitor) {
        const terminalOutput = document.getElementById('terminal-output');
        if (terminalOutput) {
            terminalOutput.innerHTML = '';
            networkMonitor.addTerminalLine('[TERMINAL] Terminal cleared', 'info');
        }
    }
}

function refreshNetworkData() {
    const networkMonitor = window.networkMonitor;
    if (networkMonitor) {
        networkMonitor.updateMetrics();
        networkMonitor.addTerminalLine('[SYSTEM] Network data refreshed', 'info');
    }
}

function exportPackets() {
    const networkMonitor = window.networkMonitor;
    if (networkMonitor) {
        networkMonitor.saveCapture();
    }
}

function showStatistics() {
    const networkMonitor = window.networkMonitor;
    if (networkMonitor) {
        networkMonitor.addTerminalLine('[STATISTICS] Packet capture statistics:', 'info');
        networkMonitor.addTerminalLine(`Total Packets: ${networkMonitor.packetCount}`, 'info');
        networkMonitor.addTerminalLine(`Total Bytes: ${networkMonitor.formatBytes(networkMonitor.bytesCaptured)}`, 'info');
        networkMonitor.addTerminalLine(`Current Interface: ${networkMonitor.currentInterface}`, 'info');
        networkMonitor.addTerminalLine(`Capture Status: ${networkMonitor.isCapturing ? 'Active' : 'Stopped'}`, 'info');
    }
}

function openSettings() {
    const networkMonitor = window.networkMonitor;
    if (networkMonitor) {
        networkMonitor.addTerminalLine('[SETTINGS] Settings panel not implemented yet', 'warning');
    }
}

// Page visibility management for network monitor
function showNetworkMonitor() {
    const networkSection = document.getElementById('network-section');
    console.log('DEBUG: showNetworkMonitor called');
    console.log('DEBUG: networkSection:', !!networkSection);
    
    if (networkSection) {
        networkSection.classList.add('active');
        networkSection.style.display = 'block';
        console.log('DEBUG: Network monitor shown');
    } else {
        console.log('DEBUG: Failed to show network monitor - missing section');
    }
}

function hideNetworkMonitor() {
    const networkSection = document.getElementById('network-section');
    if (networkSection) {
        networkSection.classList.remove('active');
        networkSection.style.display = 'none';
    }
}

// Initialize Network Monitor when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on network monitor page
    const networkSection = document.getElementById('network-section');
    const isNetworkPage = networkSection && networkSection.classList.contains('content-section');
    
    if (isNetworkPage) {
        // Only initialize network monitor on network page
        window.networkMonitor = new NetworkMonitor();
        window.networkMonitor.init();
        
        console.log('Cyber Nexus Network Monitor initialized successfully');
    }
});

// Also initialize when network section becomes active
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
            const networkSection = document.getElementById('network-section');
            if (networkSection && networkSection.classList.contains('active')) {
                if (!window.networkMonitor) {
                    window.networkMonitor = new NetworkMonitor();
                    window.networkMonitor.init();
                    console.log('Cyber Nexus Network Monitor initialized on section activation');
                }
            }
        }
    });
});

// Start observing the network section
const networkSection = document.getElementById('network-section');
if (networkSection) {
    observer.observe(networkSection, { attributes: true });
}
