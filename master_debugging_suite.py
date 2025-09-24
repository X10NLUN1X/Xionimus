#!/usr/bin/env python3
"""
Master Debugging Suite for XIONIMUS AI
Complete debugging orchestrator that runs all debugging tools
"""

import asyncio
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
import time

class MasterDebuggingSuite:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.results = {}
        
    def run_complete_debugging_suite(self):
        """Run all debugging tools in sequence"""
        print("🎯 XIONIMUS AI - MASTER DEBUGGING SUITE")
        print("=" * 70)
        print(f"🕐 Master debugging started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        success = True
        
        # Phase 1: Complete System Debugger
        print("🔧 PHASE 1: COMPLETE SYSTEM DEBUGGING")
        print("-" * 50)
        success &= self.run_complete_system_debugger()
        
        # Phase 2: System Health Monitoring
        print("\n🏥 PHASE 2: SYSTEM HEALTH MONITORING")
        print("-" * 50)
        success &= self.run_system_health_monitor()
        
        # Phase 3: Automated System Testing
        print("\n🧪 PHASE 3: AUTOMATED SYSTEM TESTING")
        print("-" * 50)
        success &= self.run_automated_system_tester()
        
        # Phase 4: Legacy Debugging Tools
        print("\n🔍 PHASE 4: LEGACY DEBUGGING VALIDATION")
        print("-" * 50)
        success &= self.run_legacy_debugging_tools()
        
        # Phase 5: Generate Master Report
        print("\n📊 PHASE 5: MASTER REPORT GENERATION")
        print("-" * 50)
        self.generate_master_report()
        
        # Phase 6: Generate Recommendations
        print("\n💡 PHASE 6: FINAL RECOMMENDATIONS")
        print("-" * 50)
        self.generate_final_recommendations()
        
        return success
        
    def run_complete_system_debugger(self):
        """Run the complete system debugger"""
        try:
            result = subprocess.run([sys.executable, "complete_system_debugger.py"], 
                                  capture_output=True, text=True, cwd=self.root_dir)
            if result.returncode == 0:
                print("   ✅ Complete system debugging finished successfully")
                self.results['complete_system_debugger'] = {
                    'status': 'success',
                    'output': result.stdout
                }
                return True
            else:
                print(f"   ❌ Complete system debugging failed: {result.stderr}")
                self.results['complete_system_debugger'] = {
                    'status': 'failed', 
                    'error': result.stderr
                }
                return False
        except Exception as e:
            print(f"   ❌ Failed to run complete system debugger: {e}")
            return False
            
    def run_system_health_monitor(self):
        """Run the system health monitor"""
        try:
            result = subprocess.run([sys.executable, "system_health_monitor.py"],
                                  capture_output=True, text=True, cwd=self.root_dir)
            if result.returncode == 0:
                print("   ✅ System health monitoring completed")
                self.results['system_health_monitor'] = {
                    'status': 'success',
                    'output': result.stdout
                }
                
                # Load health report if available
                health_report = self.root_dir / "SYSTEM_HEALTH_REPORT.json"
                if health_report.exists():
                    with open(health_report) as f:
                        self.results['system_health_data'] = json.load(f)
                        
                return True
            else:
                print(f"   ❌ System health monitoring failed: {result.stderr}")
                self.results['system_health_monitor'] = {
                    'status': 'failed',
                    'error': result.stderr
                }
                return False
        except Exception as e:
            print(f"   ❌ Failed to run system health monitor: {e}")
            return False
            
    def run_automated_system_tester(self):
        """Run the automated system tester"""
        try:
            result = subprocess.run([sys.executable, "automated_system_tester.py"],
                                  capture_output=True, text=True, cwd=self.root_dir)
            if result.returncode == 0:
                print("   ✅ Automated system testing completed")
                self.results['automated_system_tester'] = {
                    'status': 'success',
                    'output': result.stdout
                }
                
                # Load test report if available
                test_report = self.root_dir / "AUTOMATED_TEST_REPORT.json"
                if test_report.exists():
                    with open(test_report) as f:
                        self.results['automated_test_data'] = json.load(f)
                        
                return True
            else:
                print(f"   ❌ Automated system testing failed: {result.stderr}")
                self.results['automated_system_tester'] = {
                    'status': 'failed',
                    'error': result.stderr
                }
                return False
        except Exception as e:
            print(f"   ❌ Failed to run automated system tester: {e}")
            return False
            
    def run_legacy_debugging_tools(self):
        """Run legacy debugging tools for completeness"""
        try:
            # Run comprehensive_debug.py
            result = subprocess.run([sys.executable, "comprehensive_debug.py"],
                                  capture_output=True, text=True, cwd=self.root_dir)
            if result.returncode == 0:
                print("   ✅ Legacy comprehensive debugging completed")
                self.results['legacy_comprehensive_debug'] = {
                    'status': 'success',
                    'output': result.stdout
                }
            else:
                print(f"   ⚠️  Legacy comprehensive debugging had issues")
                
            # Run validate_fixes.py if available
            validate_fixes = self.root_dir / "validate_fixes.py"
            if validate_fixes.exists():
                result = subprocess.run([sys.executable, "validate_fixes.py"],
                                      capture_output=True, text=True, cwd=self.root_dir)
                if result.returncode == 0:
                    print("   ✅ Fix validation completed")
                    self.results['validate_fixes'] = {
                        'status': 'success',
                        'output': result.stdout
                    }
                else:
                    print("   ⚠️  Fix validation had issues")
                    
            return True
        except Exception as e:
            print(f"   ❌ Failed to run legacy debugging tools: {e}")
            return False
            
    def generate_master_report(self):
        """Generate master debugging report"""
        print("   📋 Generating comprehensive master report...")
        
        # Compile all results
        master_report = {
            'timestamp': datetime.now().isoformat(),
            'debugging_session_id': f"debug_{int(time.time())}",
            'tools_executed': list(self.results.keys()),
            'results': self.results,
            'summary': self.generate_summary(),
            'overall_status': self.calculate_overall_status(),
            'critical_findings': self.extract_critical_findings(),
            'recommendations': self.extract_recommendations()
        }
        
        # Save master report
        master_report_file = self.root_dir / "MASTER_DEBUGGING_REPORT.json"
        with open(master_report_file, 'w') as f:
            json.dump(master_report, f, indent=2)
            
        print(f"   📄 Master report saved to: {master_report_file}")
        
        # Generate markdown summary
        self.generate_markdown_master_report(master_report)
        
        return master_report
        
    def generate_summary(self):
        """Generate summary of all debugging results"""
        summary = {
            'total_tools_run': len(self.results),
            'successful_tools': len([r for r in self.results.values() if r.get('status') == 'success']),
            'failed_tools': len([r for r in self.results.values() if r.get('status') == 'failed']),
        }
        
        # Add system health score if available
        if 'system_health_data' in self.results:
            summary['system_health_score'] = self.results['system_health_data'].get('score', 'unknown')
            summary['system_health_status'] = self.results['system_health_data'].get('status', 'unknown')
            
        # Add test success rate if available
        if 'automated_test_data' in self.results:
            summary['test_success_rate'] = self.results['automated_test_data'].get('success_rate', 'unknown')
            
        return summary
        
    def calculate_overall_status(self):
        """Calculate overall debugging status"""
        successful_tools = len([r for r in self.results.values() if r.get('status') == 'success'])
        total_tools = len(self.results)
        
        if total_tools == 0:
            return "UNKNOWN"
        
        success_rate = successful_tools / total_tools
        
        if success_rate >= 0.9:
            return "EXCELLENT"
        elif success_rate >= 0.75:
            return "GOOD" 
        elif success_rate >= 0.5:
            return "FAIR"
        else:
            return "POOR"
            
    def extract_critical_findings(self):
        """Extract critical findings from all debugging tools"""
        findings = []
        
        # From system health
        if 'system_health_data' in self.results:
            health_data = self.results['system_health_data']
            if health_data.get('score', 100) < 75:
                findings.append(f"System health score low: {health_data.get('score')}/100")
            for issue in health_data.get('issues', []):
                findings.append(f"Health issue: {issue}")
                
        # From automated tests
        if 'automated_test_data' in self.results:
            test_data = self.results['automated_test_data']
            success_rate = test_data.get('success_rate', 100)
            if success_rate < 90:
                findings.append(f"Test success rate below 90%: {success_rate:.1f}%")
                
        return findings
        
    def extract_recommendations(self):
        """Extract recommendations from all tools"""
        recommendations = []
        
        # Standard recommendations
        recommendations.extend([
            "Ensure all Python dependencies are installed: pip install -r backend/requirements.txt",
            "Install frontend dependencies: cd frontend && npm install",
            "Configure API keys in backend/.env file for full AI functionality",
            "Start backend server: cd backend && python server.py",
            "Start frontend: cd frontend && npm start",
            "Test system functionality using provided debugging tools"
        ])
        
        # Conditional recommendations
        if 'system_health_data' in self.results:
            health_data = self.results['system_health_data']
            if "Missing node_modules" in str(health_data.get('issues', [])):
                recommendations.append("PRIORITY: Install frontend dependencies (npm install)")
            if "Missing .env file" in str(health_data.get('issues', [])):
                recommendations.append("PRIORITY: Create and configure .env file")
                
        return recommendations
        
    def generate_markdown_master_report(self, master_report):
        """Generate markdown master report"""
        markdown_file = self.root_dir / "MASTER_DEBUGGING_SUMMARY.md"
        
        markdown_content = f"""# 🎯 XIONIMUS AI - Master Debugging Report

**Generated:** {master_report['timestamp']}  
**Session ID:** {master_report['debugging_session_id']}  
**Overall Status:** **{master_report['overall_status']}**

## 📊 Executive Summary

- **Tools Executed:** {master_report['summary']['total_tools_run']}
- **Successful:** {master_report['summary']['successful_tools']}
- **Failed:** {master_report['summary']['failed_tools']}
"""

        if 'system_health_score' in master_report['summary']:
            markdown_content += f"- **System Health Score:** {master_report['summary']['system_health_score']}/100\n"
            
        if 'test_success_rate' in master_report['summary']:
            markdown_content += f"- **Test Success Rate:** {master_report['summary']['test_success_rate']:.1f}%\n"

        markdown_content += "\n## 🔧 Tools Executed\n\n"
        
        for tool_name, result in master_report['results'].items():
            if isinstance(result, dict) and 'status' in result:
                status_icon = "✅" if result['status'] == 'success' else "❌"
                markdown_content += f"- {status_icon} **{tool_name.replace('_', ' ').title()}**\n"
                
        if master_report['critical_findings']:
            markdown_content += "\n## 🚨 Critical Findings\n\n"
            for finding in master_report['critical_findings']:
                markdown_content += f"- ⚠️  {finding}\n"
        else:
            markdown_content += "\n## ✅ No Critical Issues Found!\n\n"
            
        markdown_content += "\n## 💡 Recommendations\n\n"
        for i, rec in enumerate(master_report['recommendations'], 1):
            markdown_content += f"{i}. {rec}\n"
            
        markdown_content += """
## 📁 Generated Files

- `MASTER_DEBUGGING_REPORT.json` - Complete technical report
- `MASTER_DEBUGGING_SUMMARY.md` - This summary (you are reading it)  
- `COMPLETE_DEBUGGING_SUMMARY.md` - System debugger results
- `SYSTEM_HEALTH_REPORT.json` - System health analysis
- `AUTOMATED_TEST_REPORT.json` - Automated test results

## 🎯 Conclusion

The master debugging suite has completed a comprehensive analysis of the XIONIMUS AI system. Review the findings above and follow the recommendations to ensure optimal system performance.

---
*Generated by XIONIMUS AI Master Debugging Suite*
"""
        
        markdown_file.write_text(markdown_content)
        print(f"   📄 Markdown summary saved to: {markdown_file}")
        
    def generate_final_recommendations(self):
        """Generate final recommendations and next steps"""
        print("   🎯 Analyzing all results for final recommendations...")
        
        # Determine system readiness
        overall_status = self.calculate_overall_status()
        health_score = 100
        test_success = 100
        
        if 'system_health_data' in self.results:
            health_score = self.results['system_health_data'].get('score', 100)
            
        if 'automated_test_data' in self.results:
            test_success = self.results['automated_test_data'].get('success_rate', 100)
            
        print(f"   📊 Overall Status: {overall_status}")
        print(f"   🏥 System Health: {health_score}/100")
        print(f"   🧪 Test Success: {test_success:.1f}%")
        
        # Generate priority recommendations
        if overall_status in ["EXCELLENT", "GOOD"] and health_score >= 80 and test_success >= 85:
            print("\n   🎉 SYSTEM READY FOR USE!")
            print("   💡 Priority actions:")
            print("      1. Configure API keys for full AI functionality")
            print("      2. Install frontend dependencies if needed")
            print("      3. Start both backend and frontend servers")
            print("      4. Test AI features with real API keys")
        else:
            print("\n   ⚠️  SYSTEM REQUIRES ATTENTION")
            print("   🔧 Critical actions needed:")
            if health_score < 80:
                print("      • Address system health issues")
            if test_success < 85:
                print("      • Fix failing system tests")
            print("      • Review detailed reports for specific issues")
            
        print("\n   📋 Complete debugging analysis finished!")


def main():
    """Main master debugging function"""
    suite = MasterDebuggingSuite()
    success = suite.run_complete_debugging_suite()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 MASTER DEBUGGING SUITE COMPLETED SUCCESSFULLY!")
    else:
        print("⚠️  MASTER DEBUGGING SUITE COMPLETED WITH SOME ISSUES")
    print("📋 Check generated reports for comprehensive analysis")
    print("=" * 70)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)