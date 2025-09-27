import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Upload, Download, Key, Lock, Unlock } from 'lucide-react';
import CryptoJS from 'crypto-js';

const ApiKeyImportExport = ({ isOpen, onClose }) => {
  const [exportPassword, setExportPassword] = useState('');
  const [importPassword, setImportPassword] = useState('');
  const [importFile, setImportFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // Generate a secure key from password
  const generateKey = (password) => {
    return CryptoJS.PBKDF2(password, 'xionimus-salt', {
      keySize: 256/32,
      iterations: 1000
    });
  };

  // Encrypt API keys
  const encryptApiKeys = (keys, password) => {
    const key = generateKey(password);
    const encrypted = CryptoJS.AES.encrypt(JSON.stringify(keys), key).toString();
    return encrypted;
  };

  // Decrypt API keys
  const decryptApiKeys = (encryptedData, password) => {
    try {
      const key = generateKey(password);
      const bytes = CryptoJS.AES.decrypt(encryptedData, key);
      const decryptedData = bytes.toString(CryptoJS.enc.Utf8);
      return JSON.parse(decryptedData);
    } catch (error) {
      throw new Error('Invalid password or corrupted file');
    }
  };

  // Save key to backend (lokaler Modus)
  const saveKeyToBackend = async (service, key) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001';
      const response = await fetch(`${backendUrl}/api/api-keys`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          service: service,
          api_key: key
        })
      });

      if (!response.ok) {
        console.warn(`Backend save failed for ${service} - continuing with localStorage only`);
        return; // Don't throw error - localStorage save is sufficient for local mode
      }
      
      console.log(`✅ ${service} key saved to local backend`);
    } catch (error) {
      console.warn(`Failed to save ${service} key to backend - using localStorage only:`, error);
      // Don't throw error - localStorage save was successful for local mode
    }
  };

  // Export API keys (vollständig lokaler Modus)
  const handleExport = async () => {
    if (!exportPassword) {
      alert('Bitte geben Sie ein Passwort für die Verschlüsselung ein');
      return;
    }

    setIsProcessing(true);
    try {
      console.log('🔄 Starting local API key export...');
      
      // Get current API keys from localStorage (lokaler Speicher)
      const apiKeys = {
        perplexity: localStorage.getItem('perplexity_api_key') || '',
        anthropic: localStorage.getItem('anthropic_api_key') || '',
        openai: localStorage.getItem('openai_api_key') || ''
      };

      // Check if any keys exist
      const hasKeys = apiKeys.perplexity || apiKeys.anthropic || apiKeys.openai;
      if (!hasKeys) {
        alert('Keine API-Schlüssel zum Exportieren gefunden. Bitte speichern Sie zuerst Ihre API-Schlüssel.');
        return;
      }

      console.log('🔐 Encrypting API keys locally...');
      
      // Encrypt the keys (lokale Verschlüsselung)
      const encryptedKeys = encryptApiKeys(apiKeys, exportPassword);
      
      // Create export data (lokales JSON-Format)
      const exportData = {
        version: '1.0',
        encrypted: true,
        timestamp: new Date().toISOString(),
        source: 'xionimus_local',
        data: encryptedKeys
      };

      // Download as JSON file (lokaler Download - keine externe Uploads)
      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `xionimus-api-keys-local-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      console.log('✅ Local API key export completed successfully');
      alert('API-Schlüssel erfolgreich lokal exportiert! Die Datei wurde heruntergeladen.');
      setExportPassword('');
      
    } catch (error) {
      console.error('❌ Local export error:', error);
      alert(`Fehler beim lokalen Exportieren der API-Schlüssel: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Import API keys (vollständig lokaler Modus)
  const handleImport = async () => {
    if (!importFile) {
      alert('Bitte wählen Sie eine lokale JSON-Datei aus');
      return;
    }

    if (!importPassword) {
      alert('Bitte geben Sie das Entschlüsselungs-Passwort ein');
      return;
    }

    setIsProcessing(true);
    try {
      console.log('🔄 Starting local API key import...');
      
      const fileContent = await importFile.text();
      const importData = JSON.parse(fileContent);

      // Validate file format (lokale Validation)
      if (!importData.encrypted || !importData.data) {
        throw new Error('Ungültiges Dateiformat. Bitte verwenden Sie eine gültige Xionimus Export-Datei.');
      }

      if (importData.version !== '1.0') {
        throw new Error('Nicht unterstützte Datei-Version');
      }

      console.log('🔐 Decrypting API keys locally...');
      
      // Decrypt the keys (lokale Entschlüsselung)
      const decryptedKeys = decryptApiKeys(importData.data, importPassword);

      // Validate decrypted data
      if (!decryptedKeys || typeof decryptedKeys !== 'object') {
        throw new Error('Entschlüsselung fehlgeschlagen. Bitte überprüfen Sie Ihr Passwort.');
      }

      console.log('💾 Saving keys to local storage...');
      
      // Save to localStorage and backend (lokale Speicherung)
      let importedCount = 0;
      const importPromises = [];

      if (decryptedKeys.perplexity && decryptedKeys.perplexity.trim()) {
        localStorage.setItem('perplexity_api_key', decryptedKeys.perplexity.trim());
        importPromises.push(saveKeyToBackend('perplexity', decryptedKeys.perplexity.trim()));
        importedCount++;
      }

      if (decryptedKeys.anthropic && decryptedKeys.anthropic.trim()) {
        localStorage.setItem('anthropic_api_key', decryptedKeys.anthropic.trim());
        importPromises.push(saveKeyToBackend('anthropic', decryptedKeys.anthropic.trim()));
        importedCount++;
      }

      if (decryptedKeys.openai && decryptedKeys.openai.trim()) {
        localStorage.setItem('openai_api_key', decryptedKeys.openai.trim());
        importPromises.push(saveKeyToBackend('openai', decryptedKeys.openai.trim()));
        importedCount++;
      }

      if (importedCount === 0) {
        throw new Error('Keine gültigen API-Schlüssel in der Datei gefunden');
      }

      // Wait for all saves to complete (lokale Speicher-Operationen)
      await Promise.allSettled(importPromises); // Use allSettled to continue even if backend fails

      console.log(`✅ Local import completed: ${importedCount} keys imported`);
      alert(`${importedCount} API-Schlüssel erfolgreich lokal importiert! Die Seite wird neu geladen.`);
      
      setImportPassword('');
      setImportFile(null);
      
      // Reload the page to refresh API key status (lokaler Reload)
      setTimeout(() => {
        window.location.reload();
      }, 1000);
      
    } catch (error) {
      console.error('❌ Local import error:', error);
      alert(`Fehler beim lokalen Importieren: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type === 'application/json' || file.name.endsWith('.json')) {
        setImportFile(file);
      } else {
        alert('Bitte wählen Sie eine JSON-Datei aus');
        e.target.value = '';
      }
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-black border-2 border-[#f4d03f] max-w-lg mx-auto shadow-2xl shadow-[#f4d03f]/20">
        <DialogHeader className="border-b border-[#f4d03f]/20 pb-4">
          <DialogTitle className="text-[#f4d03f] text-xl font-bold flex items-center gap-2">
            <Key className="h-5 w-5" />
            Verschlüsselter API Key Import/Export
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-8 py-6">
          {/* Export Section */}
          <div className="space-y-4">
            <h3 className="text-[#f4d03f] font-semibold flex items-center gap-2">
              <Download className="h-4 w-4" />
              API-Schlüssel Exportieren
            </h3>
            
            <div className="space-y-3">
              <div>
                <label className="text-white text-sm font-medium block mb-2">
                  Verschlüsselungs-Passwort:
                </label>
                <Input
                  type="password"
                  value={exportPassword}
                  onChange={(e) => setExportPassword(e.target.value)}
                  placeholder="Sicheres Passwort eingeben"
                  className="bg-black border-[#f4d03f]/30"
                />
              </div>
              
              <Button
                onClick={handleExport}
                disabled={!exportPassword || isProcessing}
                className="w-full bg-gradient-to-r from-[#f4d03f] to-[#d4af37] text-black hover:from-[#f9e79f] hover:to-[#f4d03f]"
              >
                <Lock className="h-4 w-4 mr-2" />
                {isProcessing ? 'Exportiere...' : 'Verschlüsselt Exportieren'}
              </Button>
            </div>
          </div>

          {/* Import Section */}
          <div className="space-y-4 border-t border-[#f4d03f]/20 pt-6">
            <h3 className="text-[#f4d03f] font-semibold flex items-center gap-2">
              <Upload className="h-4 w-4" />
              API-Schlüssel Importieren
            </h3>
            
            <div className="space-y-3">
              <div>
                <label className="text-white text-sm font-medium block mb-2">
                  JSON-Datei auswählen:
                </label>
                <input
                  type="file"
                  accept=".json"
                  onChange={handleFileChange}
                  className="w-full text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-[#f4d03f] file:text-black hover:file:bg-[#f9e79f]"
                />
              </div>
              
              <div>
                <label className="text-white text-sm font-medium block mb-2">
                  Entschlüsselungs-Passwort:
                </label>
                <Input
                  type="password"
                  value={importPassword}
                  onChange={(e) => setImportPassword(e.target.value)}
                  placeholder="Passwort zum Entschlüsseln"
                  className="bg-black border-[#f4d03f]/30"
                />
              </div>
              
              <Button
                onClick={handleImport}
                disabled={!importFile || !importPassword || isProcessing}
                className="w-full bg-black border border-[#f4d03f] text-[#f4d03f] hover:bg-[#f4d03f]/10"
              >
                <Unlock className="h-4 w-4 mr-2" />
                {isProcessing ? 'Importiere...' : 'Entschlüsseln & Importieren'}
              </Button>
            </div>
          </div>
        </div>

        {/* Info Section */}
        <div className="border-t border-[#f4d03f]/20 pt-4">
          <div className="text-xs text-gray-400 bg-black/50 p-3 rounded-lg border border-[#f4d03f]/10">
            <p className="mb-2"><strong>Sicherheitshinweise:</strong></p>
            <ul className="list-disc list-inside space-y-1">
              <li>Ihre API-Schlüssel werden mit AES-256 verschlüsselt</li>
              <li>Das Passwort wird nur lokal verwendet und nicht gespeichert</li>
              <li>Bewahren Sie das Passwort sicher auf - es kann nicht wiederhergestellt werden</li>
            </ul>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ApiKeyImportExport;