"""
Auto Review Orchestrator - Coordinates automatic code review and fixes
Manages the full workflow: scan → review → fix → commit
"""
import sys
import logging
import subprocess
if sys.platform == "win32":
    subprocess.CREATE_NO_WINDOW = 0x08000000
from typing import Dict, Any, List
from datetime import datetime, timezone

IS_WINDOWS = sys.platform == 'win32'

from .repository_scanner import RepositoryScanner
from .code_review_agents import AgentManager
from .auto_code_fixer import AutoCodeFixer

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)  # Suppress warnings for legacy module


class AutoReviewOrchestrator:
    """Orchestrates automatic code review workflow"""
    
    def __init__(self):
        self.scanner = RepositoryScanner()
        self.agent_manager = AgentManager()
        self.fixer = AutoCodeFixer()
    
    async def run_auto_review(
        self, 
        api_keys: Dict[str, str],
        scope: str = 'full',
        language: str = 'de'
    ) -> Dict[str, Any]:
        """
        Run complete auto review workflow
        
        Args:
            api_keys: API keys for AI providers
            scope: 'full', 'backend', or 'frontend'
            language: 'de' or 'en'
            
        Returns:
            Summary of review and fixes
        """
        logger.info(f"🚀 Starting auto code review - Scope: {scope}")
        
        result = {
            'status': 'success',
            'scope': scope,
            'started_at': datetime.now(timezone.utc).isoformat(),
            'files_scanned': 0,
            'files_reviewed': 0,
            'total_findings': 0,
            'fixes_applied': 0,
            'files_modified': [],
            'summary': '',
            'errors': []
        }
        
        try:
            # Step 1: Scan repository
            logger.info("📂 Step 1/4: Scanning repository...")
            files = self._scan_repository(scope)
            result['files_scanned'] = len(files)
            
            if not files:
                result['status'] = 'no_files'
                result['summary'] = self._generate_no_files_message(language)
                return result
            
            logger.info(f"✅ Found {len(files)} files to review")
            
            # Step 2: Review files with all agents
            logger.info("🔍 Step 2/4: Running 4-agent review...")
            all_findings = await self._review_files(files, api_keys)
            result['files_reviewed'] = len(files)
            result['total_findings'] = len(all_findings)
            
            logger.info(f"✅ Found {len(all_findings)} total findings")
            
            # Step 3: Apply fixes automatically
            logger.info("🔧 Step 3/4: Applying automatic fixes...")
            fix_results = await self._apply_fixes(all_findings)
            result['fixes_applied'] = fix_results['fixes_applied']
            result['files_modified'] = fix_results['files_modified']
            
            logger.info(f"✅ Applied {fix_results['fixes_applied']} fixes")
            
            # Step 4: Create git commit
            if fix_results['fixes_applied'] > 0:
                logger.info("📝 Step 4/4: Creating git commit...")
                commit_result = self._create_git_commit(fix_results)
                result['commit_hash'] = commit_result.get('hash')
                result['commit_message'] = commit_result.get('message')
            else:
                logger.info("ℹ️ Step 4/4: No fixes to commit")
            
            # Generate summary
            result['summary'] = self._generate_summary(result, language)
            result['completed_at'] = datetime.now(timezone.utc).isoformat()
            
            logger.info("✅ Auto code review complete!")
            return result
            
        except Exception as e:
            logger.error(f"❌ Auto review failed: {e}", exc_info=True)
            result['status'] = 'error'
            result['errors'].append(str(e))
            result['summary'] = self._generate_error_message(str(e), language)
            return result
    
    def _scan_repository(self, scope: str) -> List[Dict[str, Any]]:
        """Scan repository based on scope"""
        all_files = self.scanner.scan_repository(max_files=50)
        
        if scope == 'backend':
            return [f for f in all_files if f['relative_path'].startswith('backend/')]
        elif scope == 'frontend':
            return [f for f in all_files if f['relative_path'].startswith('frontend/')]
        else:  # full
            return all_files
    
    async def _review_files(
        self, 
        files: List[Dict[str, Any]], 
        api_keys: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Review files with all agents"""
        all_findings = []
        
        # Review top files (limit to prevent timeout)
        files_to_review = files[:10]  # Top 10 files
        
        for file_info in files_to_review:
            logger.info(f"🔍 Reviewing: {file_info['relative_path']}")
            
            context = {
                'file_path': file_info['path'],
                'language': file_info['language'],
                'relative_path': file_info['relative_path']
            }
            
            try:
                # Run all 4 agents on this file
                review_results = await self.agent_manager.coordinate_review(
                    code=file_info['content'],
                    context=context,
                    api_keys=api_keys,
                    review_scope='full'  # Always use all 4 agents
                )
                
                # Collect findings
                findings = review_results.get('all_findings', [])
                
                # Add file path to findings
                for finding in findings:
                    if not finding.get('file_path'):
                        finding['file_path'] = file_info['path']
                
                all_findings.extend(findings)
                
                logger.info(f"✅ {file_info['relative_path']}: {len(findings)} findings")
                
            except Exception as e:
                logger.error(f"❌ Error reviewing {file_info['relative_path']}: {e}")
                continue
        
        return all_findings
    
    async def _apply_fixes(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply automatic fixes"""
        return await self.fixer.apply_fixes(findings)
    
    def _create_git_commit(self, fix_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create git commit with all changes"""
        try:
            # Generate commit message
            commit_message = self.fixer.generate_commit_message(fix_results)
            
            # Stage all modified files
            files = fix_results.get('files_modified', [])
            if files:
                for file_path in files:
                    subprocess.run(['git', 'add', file_path], cwd='/app', check=True)
                
                # Commit
                result = subprocess.run(
                    ['git', 'commit', '-m', commit_message],
                    cwd='/app',
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # Get commit hash
                hash_result = subprocess.run(
                    ['git', 'rev-parse', 'HEAD'],
                    cwd='/app',
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                commit_hash = hash_result.stdout.strip()
                
                logger.info(f"✅ Git commit created: {commit_hash[:8]}")
                
                return {
                    'success': True,
                    'hash': commit_hash,
                    'message': commit_message
                }
        
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Git commit failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"❌ Unexpected error in git commit: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_summary(self, result: Dict[str, Any], language: str) -> str:
        """Generate human-readable summary"""
        if language == 'de':
            summary = f"""🎉 **Auto Code Review Abgeschlossen!**

📊 **Statistiken:**
- Dateien gescannt: {result['files_scanned']}
- Dateien reviewt: {result['files_reviewed']}
- Findings gefunden: {result['total_findings']}
- Fixes angewendet: {result['fixes_applied']}
- Dateien modifiziert: {len(result['files_modified'])}

"""
            if result['fixes_applied'] > 0:
                summary += f"✅ Alle Änderungen wurden committedl!\n"
                summary += f"📝 Commit: {result.get('commit_hash', '')[:8]}\n\n"
                summary += "**Modifizierte Dateien:**\n"
                for file_path in result['files_modified'][:10]:
                    summary += f"- {file_path}\n"
            else:
                summary += "ℹ️ Keine automatischen Fixes verfügbar.\n"
                summary += "Alle gefundenen Issues benötigen manuelle Überprüfung.\n"
        
        else:  # English
            summary = f"""🎉 **Auto Code Review Complete!**

📊 **Statistics:**
- Files scanned: {result['files_scanned']}
- Files reviewed: {result['files_reviewed']}
- Findings found: {result['total_findings']}
- Fixes applied: {result['fixes_applied']}
- Files modified: {len(result['files_modified'])}

"""
            if result['fixes_applied'] > 0:
                summary += f"✅ All changes have been committed!\n"
                summary += f"📝 Commit: {result.get('commit_hash', '')[:8]}\n\n"
                summary += "**Modified files:**\n"
                for file_path in result['files_modified'][:10]:
                    summary += f"- {file_path}\n"
            else:
                summary += "ℹ️ No automatic fixes available.\n"
                summary += "All found issues require manual review.\n"
        
        return summary
    
    def _generate_no_files_message(self, language: str) -> str:
        """Generate message when no files found"""
        if language == 'de':
            return "ℹ️ Keine Code-Dateien zum Review gefunden."
        else:
            return "ℹ️ No code files found for review."
    
    def _generate_error_message(self, error: str, language: str) -> str:
        """Generate error message"""
        if language == 'de':
            return f"❌ Auto Code Review fehlgeschlagen: {error}"
        else:
            return f"❌ Auto code review failed: {error}"


# Global orchestrator instance
auto_review_orchestrator = AutoReviewOrchestrator()
IS_WINDOWS = sys.platform == 'win32'
