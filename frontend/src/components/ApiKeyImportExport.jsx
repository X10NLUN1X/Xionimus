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

  // Export API keys
  const handleExport = async () => {
    if (!exportPassword) {
      alert('Bitte geben Sie ein Passwort ein');
      return;
    }

    setIsProcessing(true);
    try {
      // Get current API keys from localStorage
      const apiKeys = {
        perplexity: localStorage.getItem('perplexity_api_key') || '',
        anthropic: localStorage.getItem('anthropic_api_key') || '',
        openai: localStorage.getItem('openai_api_key') || ''
      };

      // Check if any keys exist
      if (!apiKeys.perplexity && !apiKeys.anthropic && !apiKeys.openai) {
        alert('Keine API-Schlüssel zum Exportieren gefunden');
        return;
      }

      // Encrypt the keys
      const encryptedKeys = encryptApiKeys(apiKeys, exportPassword);
      
      // Create export data
      const exportData = {
        version: '1.0',
        encrypted: true,
        timestamp: new Date().toISOString(),
        data: encryptedKeys
      };

      // Download as JSON file
      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `xionimus-api-keys-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      alert('API-Schlüssel erfolgreich exportiert!');
      setExportPassword('');
      
    } catch (error) {
      console.error('Export error:', error);
      alert('Fehler beim Exportieren der API-Schlüssel');
    } finally {
      setIsProcessing(false);
    }
  };

  // Import API keys
  const handleImport = async () => {
    if (!importFile) {
      alert('Bitte wählen Sie eine Datei aus');
      return;
    }

    if (!importPassword) {
      alert('Bitte geben Sie das Passwort ein');
      return;
    }

    setIsProcessing(true);
    try {
      const fileContent = await importFile.text();
      const importData = JSON.parse(fileContent);

      // Validate file format
      if (!importData.encrypted || !importData.data) {
        throw new Error('Ungültiges Dateiformat');
      }

      // Decrypt the keys
      const decryptedKeys = decryptApiKeys(importData.data, importPassword);

      // Validate decrypted data
      if (!decryptedKeys || typeof decryptedKeys !== 'object') {
        throw new Error('Ungültige Datenstruktur');
      }

      // Save to localStorage and backend
      let importedCount = 0;
      const importPromises = [];

      if (decryptedKeys.perplexity) {
        localStorage.setItem('perplexity_api_key', decryptedKeys.perplexity);
        importPromises.push(saveKeyToBackend('perplexity', decryptedKeys.perplexity));
        importedCount++;
      }

      if (decryptedKeys.anthropic) {
        localStorage.setItem('anthropic_api_key', decryptedKeys.anthropic);
        importPromises.push(saveKeyToBackend('anthropic', decryptedKeys.anthropic));
        importedCount++;
      }

      if (decryptedKeys.openai) {
        localStorage.setItem('openai_api_key', decryptedKeys.openai);
        importPromises.push(saveKeyToBackend('openai', decryptedKeys.openai));
        importedCount++;
      }

      // Wait for all saves to complete
      await Promise.all(importPromises);

      alert(`${importedCount} API-Schlüssel erfolgreich importiert!`);
      setImportPassword('');
      setImportFile(null);
      
      // Reload the page to refresh API key status
      window.location.reload();
      
    } catch (error) {
      console.error('Import error:', error);
      alert(`Fehler beim Importieren: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Save key to backend
  const saveKeyToBackend = async (service, key) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.VITE_BACKEND_URL;
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
        throw new Error(`Backend save failed for ${service}`);
      }
    } catch (error) {
      console.error(`Failed to save ${service} key to backend:`, error);
      // Don't throw error - localStorage save was successful
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