import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Progress } from './ui/progress';
import { 
  Zap, 
  Play, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Code, 
  FileText,
  Clock,
  Target
} from 'lucide-react';
import axios from 'axios';
import Editor from '@monaco-editor/react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const AutoTestingComponent = () => {
  const [sourceCode, setSourceCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [framework, setFramework] = useState('');
  const [testTypes, setTestTypes] = useState(['unit']);
  const [coverageTarget, setCoverageTarget] = useState(80);
  const [loading, setLoading] = useState(false);
  const [testSuite, setTestSuite] = useState(null);
  const [testResults, setTestResults] = useState(null);
  const [activeTab, setActiveTab] = useState('generate');

  const supportedLanguages = [
    { value: 'python', label: 'Python' },
    { value: 'javascript', label: 'JavaScript' },
    { value: 'typescript', label: 'TypeScript' },
    { value: 'java', label: 'Java' },
    { value: 'ruby', label: 'Ruby' },
    { value: 'go', label: 'Go' },
    { value: 'rust', label: 'Rust' },
    { value: 'csharp', label: 'C#' }
  ];

  const testFrameworks = {
    python: ['pytest', 'unittest'],
    javascript: ['jest', 'mocha'],
    typescript: ['jest', 'mocha'],
    java: ['junit'],
    ruby: ['rspec'],
    go: ['testing'],
    rust: ['cargo-test'],
    csharp: ['nunit', 'xunit']
  };

  const generateTests = async () => {
    if (!sourceCode.trim()) {
      alert('Bitte geben Sie den Quellcode ein');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${BACKEND_URL}/api/auto-test/generate`, {
        code: sourceCode,
        language,
        framework: framework || undefined,
        test_types: testTypes,
        coverage_target: coverageTarget
      });

      if (response.data.success) {
        setTestSuite(response.data.test_suite);
        setActiveTab('review');
      }
    } catch (error) {
      console.error('Test generation failed:', error);
      alert('Fehler bei der Test-Generierung: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const executeTests = async () => {
    if (!testSuite) return;

    setLoading(true);
    try {
      const response = await axios.post(`${BACKEND_URL}/api/auto-test/execute`, {
        test_suite: testSuite
      });

      if (response.data.success) {
        setTestResults(response.data);
        setActiveTab('results');
      }
    } catch (error) {
      console.error('Test execution failed:', error);
      alert('Fehler bei der Test-Ausführung: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    const icons = {
      'passed': <CheckCircle className="h-4 w-4 text-green-600" />,
      'failed': <XCircle className="h-4 w-4 text-red-600" />,
      'error': <AlertCircle className="h-4 w-4 text-orange-600" />,
      'skipped': <Clock className="h-4 w-4 text-gray-600" />
    };
    return icons[status] || <AlertCircle className="h-4 w-4 text-gray-600" />;
  };

  const getStatusColor = (status) => {
    const colors = {
      'passed': 'bg-green-100 text-green-800',
      'failed': 'bg-red-100 text-red-800',
      'error': 'bg-orange-100 text-orange-800',
      'skipped': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Zap className="h-5 w-5" />
          🤖 Auto-Testing
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Automatische Test-Generierung und -Ausführung
        </p>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="generate">Code eingeben</TabsTrigger>
            <TabsTrigger value="review" disabled={!testSuite}>Tests überprüfen</TabsTrigger>
            <TabsTrigger value="execute" disabled={!testSuite}>Ausführung</TabsTrigger>
            <TabsTrigger value="results" disabled={!testResults}>Ergebnisse</TabsTrigger>
          </TabsList>

          <TabsContent value="generate" className="space-y-4">
            {/* Language Selection */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Programmiersprache</label>
                <Select value={language} onValueChange={setLanguage}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {supportedLanguages.map(lang => (
                      <SelectItem key={lang.value} value={lang.value}>
                        {lang.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Test Framework</label>
                <Select value={framework} onValueChange={setFramework}>
                  <SelectTrigger>
                    <SelectValue placeholder="Auto-detect" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Auto-detect</SelectItem>
                    {(testFrameworks[language] || []).map(fw => (
                      <SelectItem key={fw} value={fw}>
                        {fw}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Coverage Target */}
            <div>
              <label className="text-sm font-medium mb-2 block">
                Coverage-Ziel: {coverageTarget}%
              </label>
              <input
                type="range"
                min="50"
                max="100"
                value={coverageTarget}
                onChange={(e) => setCoverageTarget(Number(e.target.value))}
                className="w-full"
              />
            </div>

            {/* Test Types */}
            <div>
              <label className="text-sm font-medium mb-2 block">Test-Typen</label>
              <div className="flex gap-2 flex-wrap">
                {['unit', 'integration', 'e2e'].map(type => (
                  <Button
                    key={type}
                    variant={testTypes.includes(type) ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => {
                      setTestTypes(prev => 
                        prev.includes(type) 
                          ? prev.filter(t => t !== type)
                          : [...prev, type]
                      );
                    }}
                  >
                    {type}
                  </Button>
                ))}
              </div>
            </div>

            {/* Code Editor */}
            <div>
              <label className="text-sm font-medium mb-2 block">Quellcode</label>
              <div className="border rounded-md overflow-hidden">
                <Editor
                  height="300px"
                  language={language}
                  value={sourceCode}
                  onChange={(value) => setSourceCode(value || '')}
                  theme="vs-dark"
                  options={{
                    minimap: { enabled: false },
                    scrollBeyondLastLine: false,
                    fontSize: 14
                  }}
                />
              </div>
            </div>

            {/* Generate Button */}
            <Button 
              onClick={generateTests} 
              disabled={loading || !sourceCode.trim()}
              className="w-full"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Tests generieren...
                </>
              ) : (
                <>
                  <Code className="h-4 w-4 mr-2" />
                  Tests generieren
                </>
              )}
            </Button>
          </TabsContent>

          <TabsContent value="review" className="space-y-4">
            {testSuite && (
              <>
                {/* Test Suite Info */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{testSuite.test_count}</div>
                    <div className="text-sm text-gray-600">Tests</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-green-600">{testSuite.language}</div>
                    <div className="text-sm text-gray-600">Sprache</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-purple-600">{testSuite.framework}</div>
                    <div className="text-sm text-gray-600">Framework</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-orange-600">{testSuite.dependencies.length}</div>
                    <div className="text-sm text-gray-600">Dependencies</div>
                  </div>
                </div>

                {/* Generated Tests */}
                <div>
                  <h3 className="text-lg font-semibold mb-3">Generierte Tests</h3>
                  <ScrollArea className="h-64">
                    <div className="space-y-3">
                      {testSuite.test_cases.map((testCase, index) => (
                        <Card key={index} className="p-3">
                          <div className="flex items-start justify-between mb-2">
                            <h4 className="font-medium">{testCase.name}</h4>
                            <Badge variant="outline">{testCase.type}</Badge>
                          </div>
                          <p className="text-sm text-gray-600 mb-2">{testCase.description}</p>
                          <div className="bg-gray-50 p-2 rounded text-xs font-mono">
                            <pre className="whitespace-pre-wrap">
                              {testCase.test_code.split('\n').slice(0, 3).join('\n')}
                              {testCase.test_code.split('\n').length > 3 && '\n...'}
                            </pre>
                          </div>
                        </Card>
                      ))}
                    </div>
                  </ScrollArea>
                </div>

                {/* Execute Tests Button */}
                <Button onClick={executeTests} disabled={loading} className="w-full">
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Tests ausführen...
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Tests ausführen
                    </>
                  )}
                </Button>
              </>
            )}
          </TabsContent>

          <TabsContent value="execute" className="space-y-4">
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <div className="mt-2 text-sm text-gray-600">Tests werden ausgeführt...</div>
            </div>
          </TabsContent>

          <TabsContent value="results" className="space-y-4">
            {testResults && (
              <>
                {/* Results Summary */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4 p-4 bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{testResults.summary.total}</div>
                    <div className="text-sm text-gray-600">Gesamt</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{testResults.summary.passed}</div>
                    <div className="text-sm text-gray-600">Bestanden</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">{testResults.summary.failed}</div>
                    <div className="text-sm text-gray-600">Fehlgeschlagen</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-600">{testResults.summary.errors}</div>
                    <div className="text-sm text-gray-600">Fehler</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">{testResults.summary.pass_rate.toFixed(1)}%</div>
                    <div className="text-sm text-gray-600">Erfolgsrate</div>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Test Erfolg</span>
                    <span>{testResults.summary.pass_rate.toFixed(1)}%</span>
                  </div>
                  <Progress value={testResults.summary.pass_rate} className="h-2" />
                </div>

                {/* Individual Test Results */}
                <div>
                  <h3 className="text-lg font-semibold mb-3">Test Ergebnisse</h3>
                  <ScrollArea className="h-64">
                    <div className="space-y-2">
                      {testResults.results.map((result, index) => (
                        <Card key={index} className="p-3">
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              {getStatusIcon(result.status)}
                              <h4 className="font-medium">{result.test_name}</h4>
                            </div>
                            <div className="flex items-center gap-2">
                              <Badge className={getStatusColor(result.status)}>
                                {result.status}
                              </Badge>
                              <span className="text-xs text-gray-500">
                                {result.execution_time.toFixed(2)}s
                              </span>
                            </div>
                          </div>
                          
                          {result.output && (
                            <div className="bg-gray-50 p-2 rounded text-xs font-mono mt-2">
                              <pre className="whitespace-pre-wrap">{result.output}</pre>
                            </div>
                          )}
                          
                          {result.error_message && (
                            <div className="bg-red-50 p-2 rounded text-xs font-mono mt-2">
                              <pre className="whitespace-pre-wrap text-red-800">{result.error_message}</pre>
                            </div>
                          )}
                        </Card>
                      ))}
                    </div>
                  </ScrollArea>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    onClick={() => setActiveTab('generate')}
                    className="flex-1"
                  >
                    Neuen Test erstellen
                  </Button>
                  <Button 
                    onClick={executeTests} 
                    disabled={loading}
                    className="flex-1"
                  >
                    Tests wiederholen
                  </Button>
                </div>
              </>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default AutoTestingComponent;