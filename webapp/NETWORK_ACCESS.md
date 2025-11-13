# 🌐 Network Access Information

## Your Local Network IP
**192.168.1.196**

## Dashboard URLs

### From This Computer (Localhost)
- **Dashboard UI**: http://localhost:3000
- **API Server**: http://localhost:5000
- **WebSocket**: ws://localhost:5001

### From Other Devices on Your Network
- **Dashboard UI**: http://192.168.1.196:3000
- **API Server**: http://192.168.1.196:5000
- **WebSocket**: ws://192.168.1.196:5001

## How to Access from Other Devices

### 📱 Phone/Tablet
1. Connect to the same WiFi network as this computer
2. Open browser and go to: **http://192.168.1.196:3000**
3. Click "🎮 Switch to Skyrim AGI" if needed

### 💻 Another Computer
1. Connect to the same network
2. Open browser and navigate to: **http://192.168.1.196:3000**
3. Dashboard should load and connect automatically

## Firewall Configuration

If you can't connect from other devices, you may need to allow the ports through Windows Firewall:

### Windows PowerShell (Run as Administrator)
```powershell
# Allow HTTP API server (port 5000)
New-NetFirewallRule -DisplayName "Singularis API Server" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow

# Allow WebSocket server (port 5001)
New-NetFirewallRule -DisplayName "Singularis WebSocket" -Direction Inbound -LocalPort 5001 -Protocol TCP -Action Allow

# Allow React dev server (port 3000)
New-NetFirewallRule -DisplayName "Singularis Dashboard" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
```

## Testing Connection

### From This Computer
```powershell
# Test API server
curl http://localhost:5000/api/health

# Or open in browser
start http://localhost:3000
```

### From Another Device
```bash
# Test API server (from another computer's terminal)
curl http://192.168.1.196:5000/api/health

# Or just open in browser
http://192.168.1.196:3000
```

## Troubleshooting

### Can't Connect from Other Devices?

1. **Check Firewall**: Run the PowerShell commands above as Administrator
2. **Verify Network**: Make sure devices are on the same WiFi/LAN
3. **Check Server Status**: Ensure both servers are running (see below)
4. **Test Locally First**: Visit http://localhost:3000 to confirm it works locally

### Required Running Services

You need 2 terminals running:

**Terminal 1: Backend Server**
```powershell
cd d:\Projects\Singularis\webapp
node server.js
```
Should show:
```
HTTP server running on:
  - Local:   http://localhost:5000
  - Network: http://192.168.1.196:5000

WebSocket server running on:
  - Local:   ws://localhost:5001
  - Network: ws://192.168.1.196:5001
```

**Terminal 2: React Dashboard**
```powershell
cd d:\Projects\Singularis\webapp
node node_modules\react-scripts\bin\react-scripts.js start
```

### IP Address Changed?

If your IP address changes (common with DHCP), run:
```powershell
ipconfig | Select-String -Pattern "IPv4"
```

Then update the URLs above with your new IP address.

## Security Note

⚠️ **Important**: These servers are accessible to anyone on your local network. 
- Do NOT expose to the public internet without proper security
- Only use on trusted networks (home/office WiFi)
- The dashboard is read-only - visitors can only view, not control

## Performance Tips

### For Best Performance on Remote Devices
1. Use the Skyrim AGI mode (better optimized)
2. Keep to the same network (not guest WiFi)
3. Use a 5GHz WiFi connection if available
4. Close unnecessary tabs on the viewing device

### Reducing Network Load
If you experience lag:
- Increase update interval in `server.js` from 1000ms to 2000ms
- Limit historical data displayed in charts
- Use Chrome/Edge for better WebSocket performance

---

**Generated**: November 13, 2025
**Local IP**: 192.168.1.196
**Status**: ✅ Servers configured for network access
