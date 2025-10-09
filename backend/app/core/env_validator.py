"""
Environment Variable Validator

Validiert kritische Environment-Variablen beim Server-Start.
Verhindert unsichere Konfigurationen in Produktion.
"""

import os
import sys
from typing import List, Optional, Tuple
import secrets


class EnvValidationError(Exception):
    """Fehler bei Environment-Validierung"""
    pass


class EnvironmentValidator:
    """Validiert und prüft Environment-Variablen"""
    
    # Kritische Variablen, die immer gesetzt sein müssen
    REQUIRED_VARS = [
        "SECRET_KEY",
    ]
    
    # Empfohlene Variablen für volle Funktionalität
    RECOMMENDED_VARS = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "PERPLEXITY_API_KEY",
    ]
    
    # Variablen mit Default-Werten
    OPTIONAL_VARS_WITH_DEFAULTS = {
        "JWT_ALGORITHM": "HS256",
        "JWT_EXPIRE_MINUTES": "1440",
        "DEBUG": "false",
        "HOST": "0.0.0.0",
        "PORT": "8001",
        "LOG_LEVEL": "INFO",
    }
    
    def __init__(self, strict_mode: bool = False):
        """
        Args:
            strict_mode: Wenn True, werden auch empfohlene Variablen geprüft
        """
        self.strict_mode = strict_mode
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_required_vars(self) -> None:
        """Prüft, ob alle kritischen Variablen gesetzt sind"""
        for var in self.REQUIRED_VARS:
            value = os.getenv(var)
            if not value:
                self.errors.append(
                    f"❌ Kritische Variable fehlt: {var}\n"
                    f"   Bitte in .env setzen (siehe .env.example)"
                )
    
    def validate_secret_key(self) -> None:
        """Prüft SECRET_KEY auf Sicherheit"""
        secret_key = os.getenv("SECRET_KEY")
        
        if not secret_key:
            return  # Bereits in validate_required_vars behandelt
        
        # Prüfe auf unsichere Defaults
        insecure_defaults = [
            "your-secret-key-here",
            "changeme",
            "secret",
            "test",
            "development",
        ]
        
        if any(default in secret_key.lower() for default in insecure_defaults):
            self.errors.append(
                f"❌ SECRET_KEY ist unsicher (enthält bekanntes Muster)\n"
                f"   Generiere sicheren Key mit:\n"
                f"   python -c \"import secrets; print(secrets.token_hex(32))\""
            )
            return
        
        # Prüfe Länge (minimum 32 Zeichen für 256-bit security)
        if len(secret_key) < 32:
            self.warnings.append(
                f"⚠️  SECRET_KEY ist zu kurz ({len(secret_key)} Zeichen)\n"
                f"   Empfohlen: Mindestens 32 Zeichen (256-bit)"
            )
    
    def validate_database_url(self) -> None:
        """Prüft MONGO_URL auf Gültigkeit"""
        mongo_url = os.getenv("MONGO_URL")
        
        if not mongo_url:
            return  # Bereits in validate_required_vars behandelt
        
        # Prüfe grundlegendes Format
        if not (mongo_url.startswith("mongodb://") or mongo_url.startswith("mongodb+srv://")):
            self.errors.append(
                f"❌ MONGO_URL hat ungültiges Format\n"
                f"   Muss mit 'mongodb://' oder 'mongodb+srv://' beginnen"
            )
    
    def validate_recommended_vars(self) -> None:
        """Prüft empfohlene Variablen (nur Warnungen)"""
        missing_recommended = []
        
        for var in self.RECOMMENDED_VARS:
            if not os.getenv(var):
                missing_recommended.append(var)
        
        if missing_recommended:
            self.warnings.append(
                f"⚠️  Keine AI Provider API Keys konfiguriert: {', '.join(missing_recommended)}\n"
                f"   Die AI-Funktionalität ist eingeschränkt\n"
                f"   Konfiguriere mindestens einen Provider in .env"
            )
    
    def validate_production_settings(self) -> None:
        """Prüft Produktion-spezifische Einstellungen"""
        debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Wenn nicht in Debug-Mode, prüfe Produktion-Settings
        if not debug:
            # CORS sollte nicht zu permissiv sein
            cors_origins = os.getenv("CORS_ORIGINS", "")
            if "*" in cors_origins:
                self.warnings.append(
                    f"⚠️  CORS_ORIGINS='*' ist unsicher für Produktion\n"
                    f"   Setze spezifische Domains"
                )
            
            # Log-Level sollte nicht DEBUG sein
            log_level = os.getenv("LOG_LEVEL", "INFO").upper()
            if log_level == "DEBUG":
                self.warnings.append(
                    f"⚠️  LOG_LEVEL=DEBUG in Produktion nicht empfohlen\n"
                    f"   Verwende INFO oder WARNING"
                )
    
    def set_defaults(self) -> None:
        """Setzt Default-Werte für optionale Variablen"""
        for var, default_value in self.OPTIONAL_VARS_WITH_DEFAULTS.items():
            if not os.getenv(var):
                os.environ[var] = default_value
    
    def validate_all(self) -> Tuple[bool, str]:
        """
        Führt alle Validierungen durch
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        self.errors = []
        self.warnings = []
        
        # Kritische Validierungen
        self.validate_required_vars()
        self.validate_secret_key()
        self.validate_database_url()
        
        # Empfohlene Validierungen
        self.validate_recommended_vars()
        self.validate_production_settings()
        
        # Setze Defaults
        self.set_defaults()
        
        # Erstelle Bericht
        if self.errors:
            message = "\n" + "="*70 + "\n"
            message += "🚨 ENVIRONMENT VALIDATION FAILED\n"
            message += "="*70 + "\n\n"
            message += "\n\n".join(self.errors)
            message += "\n\n" + "-"*70 + "\n"
            message += "💡 LÖSUNG:\n"
            message += "   1. Kopiere .env.example nach .env\n"
            message += "   2. Fülle alle kritischen Variablen aus\n"
            message += "   3. Starte Server neu\n"
            message += "-"*70 + "\n"
            return False, message
        
        # Nur Warnungen
        if self.warnings:
            message = "\n" + "="*70 + "\n"
            message += "⚠️  ENVIRONMENT WARNINGS\n"
            message += "="*70 + "\n\n"
            message += "\n\n".join(self.warnings)
            message += "\n\n" + "-"*70 + "\n"
            message += "Server startet trotzdem, aber mit eingeschränkter Funktionalität\n"
            message += "-"*70 + "\n"
            # Nur ausgeben, nicht abbrechen
            print(message)
        
        return True, "✅ Environment validation successful"


def validate_environment(strict_mode: bool = False) -> None:
    """
    Validiert Environment-Variablen beim Server-Start
    
    Args:
        strict_mode: Wenn True, werden auch empfohlene Variablen geprüft
        
    Raises:
        EnvValidationError: Wenn kritische Validierungen fehlschlagen
    """
    validator = EnvironmentValidator(strict_mode=strict_mode)
    success, message = validator.validate_all()
    
    if not success:
        print(message, file=sys.stderr)
        raise EnvValidationError("Environment validation failed - siehe Details oben")
    
    if message != "✅ Environment validation successful":
        print(message)


# Auto-Validierung beim Import (kann mit ENV deaktiviert werden)
if __name__ != "__main__":
    if os.getenv("SKIP_ENV_VALIDATION", "false").lower() != "true":
        try:
            validate_environment()
        except EnvValidationError as e:
            # In Tests oder bestimmten Kontexten kann Validierung übersprungen werden
            if os.getenv("ENV", "production") != "test":
                sys.exit(1)
