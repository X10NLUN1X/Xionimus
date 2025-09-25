import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  FileText, 
  CheckCircle, 
  AlertTriangle, 
  XCircle, 
  Info, 
  TrendingUp, 
  Shield, 
  Zap,
  BookOpen,
  Target,
  Award,
  ThumbsUp
} from 'lucide-react';
import axios from 'axios';
import Editor from '@monaco-editor/react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const CodeReviewComponent = () => {
  const [sourceCode, setSourceCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [filePath, setFilePath] = useState('');
  const [loading, setLoading] = useState(false);
  const [reviewResult, setReviewResult] = useState(null);

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

  const performCodeReview = async () => {
    if (!sourceCode.trim()) {
      alert('Bitte geben Sie den Quellcode ein');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${BACKEND_URL}/api/code-review`, {
        code: sourceCode,
        language,
        file_path: filePath || undefined,
        context: {
          project_name: 'Code Review',
          review_type: 'comprehensive'
        }
      });

      if (response.data.success) {
        setReviewResult(response.data.review);
      }
    } catch (error) {
      console.error('Code review failed:', error);
      alert('Fehler bei der Code-Review: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const getSeverityIcon = (severity) => {
    const icons = {
      'critical': <XCircle className="h-4 w-4 text-red-600" />,
      'major': <AlertTriangle className="h-4 w-4 text-orange-600" />,
      'minor': <Info className="h-4 w-4 text-blue-600" />,
      'info': <CheckCircle className="h-4 w-4 text-green-600" />
    };
    return icons[severity] || <Info className="h-4 w-4 text-gray-600" />;
  };

  const getSeverityColor = (severity) => {
    const colors = {
      'critical': 'bg-red-100 text-red-800 border-red-200',
      'major': 'bg-orange-100 text-orange-800 border-orange-200',
      'minor': 'bg-blue-100 text-blue-800 border-blue-200',
      'info': 'bg-green-100 text-green-800 border-green-200'
    };
    return colors[severity] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getGradeColor = (grade) => {
    if (grade.startsWith('A')) return 'text-green-600 bg-green-100';
    if (grade.startsWith('B')) return 'text-blue-600 bg-blue-100';
    if (grade.startsWith('C')) return 'text-yellow-600 bg-yellow-100';
    if (grade.startsWith('D')) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  const getScoreColor = (score) => {
    if (score >= 85) return 'text-green-600';
    if (score >= 70) return 'text-blue-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getCategoryIcon = (category) => {
    const icons = {
      'security': <Shield className="h-4 w-4" />,
      'performance': <Zap className="h-4 w-4" />,
      'maintainability': <BookOpen className="h-4 w-4" />,
      'style': <Target className="h-4 w-4" />,
      'bug': <XCircle className="h-4 w-4" />
    };
    return icons[category] || <Info className="h-4 w-4" />;
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          📝 Code Review AI
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Intelligente Code-Review mit Verbesserungsvorschlägen
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {!reviewResult ? (
          <>
            {/* Input Section */}
            <div className="space-y-4">
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
                  <label className="text-sm font-medium mb-2 block">Dateipfad (optional)</label>
                  <input
                    type="text"
                    placeholder="z.B. src/main.py"
                    value={filePath}
                    onChange={(e) => setFilePath(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Quellcode</label>
                <div className="border rounded-md overflow-hidden">
                  <Editor
                    height="400px"
                    language={language}
                    value={sourceCode}
                    onChange={(value) => setSourceCode(value || '')}
                    theme="vs-dark"
                    options={{
                      minimap: { enabled: false },
                      scrollBeyondLastLine: false,
                      fontSize: 14,
                      lineNumbers: 'on',
                      renderWhitespace: 'selection'
                    }}
                  />
                </div>
              </div>

              <Button 
                onClick={performCodeReview} 
                disabled={loading || !sourceCode.trim()}
                className="w-full"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Code wird analysiert...
                  </>
                ) : (
                  <>
                    <FileText className="h-4 w-4 mr-2" />
                    Code Review starten
                  </>
                )}
              </Button>
            </div>
          </>
        ) : (
          <>
            {/* Review Results */}
            <Tabs defaultValue="overview" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="overview">Übersicht</TabsTrigger>
                <TabsTrigger value="issues">Probleme</TabsTrigger>
                <TabsTrigger value="metrics">Metriken</TabsTrigger>
                <TabsTrigger value="suggestions">Vorschläge</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-6">
                {/* Overall Score */}
                <Card className="p-6">
                  <div className="text-center">
                    <div className={`text-4xl font-bold mb-2 ${getScoreColor(reviewResult.overall_score)}`}>
                      {reviewResult.overall_score.toFixed(1)}
                    </div>
                    <div className={`inline-flex px-3 py-1 rounded-full text-lg font-semibold ${getGradeColor(reviewResult.grade)}`}>
                      {reviewResult.grade}
                    </div>
                    <div className="text-sm text-gray-600 mt-2">
                      Code Quality Score
                    </div>
                  </div>
                  <Progress value={reviewResult.overall_score} className="mt-4 h-3" />
                </Card>

                {/* Quick Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Card className="p-4 text-center">
                    <div className="text-2xl font-bold text-red-600">
                      {reviewResult.issues.filter(i => i.severity === 'critical').length}
                    </div>
                    <div className="text-sm text-gray-600">Kritisch</div>
                  </Card>
                  <Card className="p-4 text-center">
                    <div className="text-2xl font-bold text-orange-600">
                      {reviewResult.issues.filter(i => i.severity === 'major').length}
                    </div>
                    <div className="text-sm text-gray-600">Wichtig</div>
                  </Card>
                  <Card className="p-4 text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {reviewResult.issues.filter(i => i.severity === 'minor').length}
                    </div>
                    <div className="text-sm text-gray-600">Gering</div>
                  </Card>
                  <Card className="p-4 text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {reviewResult.positive_aspects.length}
                    </div>
                    <div className="text-sm text-gray-600">Positiv</div>
                  </Card>
                </div>

                {/* Summary */}
                <Card className="p-4">
                  <h3 className="text-lg font-semibold mb-3">Zusammenfassung</h3>
                  <div className="prose prose-sm max-w-none">
                    <div dangerouslySetInnerHTML={{ 
                      __html: reviewResult.summary.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') 
                    }} />
                  </div>
                </Card>

                {/* Positive Aspects */}
                {reviewResult.positive_aspects.length > 0 && (
                  <Card className="p-4">
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <ThumbsUp className="h-5 w-5 text-green-600" />
                      Positive Aspekte
                    </h3>
                    <div className="space-y-2">
                      {reviewResult.positive_aspects.map((aspect, index) => (
                        <div key={index} className="flex items-start gap-2 p-2 bg-green-50 rounded">
                          <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                          <span className="text-sm">{aspect}</span>
                        </div>
                      ))}
                    </div>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="issues" className="space-y-4">
                <ScrollArea className="h-96">
                  {reviewResult.issues.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <Award className="h-12 w-12 mx-auto mb-4 text-green-500" />
                      <p>Keine Probleme gefunden! 🎉</p>
                      <p className="text-sm">Ihr Code entspricht den Best Practices.</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {reviewResult.issues.map((issue, index) => (
                        <Card key={index} className={`p-4 border-l-4 ${getSeverityColor(issue.severity)}`}>
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              {getSeverityIcon(issue.severity)}
                              <h4 className="font-semibold">{issue.title}</h4>
                            </div>
                            <div className="flex items-center gap-2">
                              <Badge variant="outline" className="text-xs">
                                {getCategoryIcon(issue.category)}
                                <span className="ml-1">{issue.category}</span>
                              </Badge>
                              <Badge className={getSeverityColor(issue.severity)}>
                                {issue.severity}
                              </Badge>
                            </div>
                          </div>
                          
                          <p className="text-sm text-gray-700 mb-3">{issue.description}</p>
                          
                          <div className="bg-blue-50 p-3 rounded mb-3">
                            <div className="text-sm font-medium text-blue-800 mb-1">💡 Verbesserungsvorschlag:</div>
                            <div className="text-sm text-blue-700">{issue.suggestion}</div>
                          </div>
                          
                          {issue.example_fix && (
                            <div className="bg-gray-50 p-3 rounded">
                              <div className="text-sm font-medium text-gray-800 mb-1">🔧 Beispiel-Fix:</div>
                              <pre className="text-xs font-mono text-gray-700 overflow-x-auto">
                                {issue.example_fix}
                              </pre>
                            </div>
                          )}
                          
                          <div className="flex items-center justify-between mt-3 text-xs text-gray-500">
                            {issue.line_number && (
                              <span>Zeile {issue.line_number}</span>
                            )}
                            <span>Vertrauen: {(issue.confidence * 100).toFixed(0)}%</span>
                          </div>
                        </Card>
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </TabsContent>

              <TabsContent value="metrics" className="space-y-4">
                <div className="grid grid-cols-2 gap-6">
                  {/* Code Metrics */}
                  <Card className="p-4">
                    <h3 className="text-lg font-semibold mb-4">Code Metriken</h3>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Komplexität</span>
                          <span>{reviewResult.metrics.complexity}</span>
                        </div>
                        <div className="text-xs text-gray-500">
                          {reviewResult.metrics.complexity <= 10 ? 'Niedrig' : 
                           reviewResult.metrics.complexity <= 20 ? 'Mittel' : 'Hoch'}
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Wartbarkeitsindex</span>
                          <span>{reviewResult.metrics.maintainability_index.toFixed(1)}</span>
                        </div>
                        <Progress value={reviewResult.metrics.maintainability_index} className="h-2" />
                      </div>
                      
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Code-Duplikation</span>
                          <span>{reviewResult.metrics.code_duplication.toFixed(1)}%</span>
                        </div>
                        <Progress value={reviewResult.metrics.code_duplication} className="h-2" />
                      </div>
                      
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Dokumentation</span>
                          <span>{reviewResult.metrics.documentation_coverage.toFixed(1)}%</span>
                        </div>
                        <Progress value={reviewResult.metrics.documentation_coverage} className="h-2" />
                      </div>
                    </div>
                  </Card>

                  {/* Quality Scores */}
                  <Card className="p-4">
                    <h3 className="text-lg font-semibold mb-4">Qualitäts-Scores</h3>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="flex items-center gap-1">
                            <Shield className="h-4 w-4" />
                            Sicherheit
                          </span>
                          <span>{reviewResult.metrics.security_score.toFixed(1)}</span>
                        </div>
                        <Progress value={reviewResult.metrics.security_score} className="h-2" />
                      </div>
                      
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="flex items-center gap-1">
                            <Zap className="h-4 w-4" />
                            Performance
                          </span>
                          <span>{reviewResult.metrics.performance_score.toFixed(1)}</span>
                        </div>
                        <Progress value={reviewResult.metrics.performance_score} className="h-2" />
                      </div>
                      
                      <div className="pt-4 border-t">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-gray-800">
                            {reviewResult.metrics.lines_of_code}
                          </div>
                          <div className="text-sm text-gray-600">Zeilen Code</div>
                        </div>
                      </div>
                    </div>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="suggestions" className="space-y-4">
                <Card className="p-4">
                  <h3 className="text-lg font-semibold mb-4">Verbesserungsvorschläge</h3>
                  {reviewResult.suggestions.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-500" />
                      <p>Keine weiteren Verbesserungen erforderlich! 🎉</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {reviewResult.suggestions.map((suggestion, index) => (
                        <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                          <div className="flex-shrink-0 mt-1">
                            <div className="w-6 h-6 bg-blue-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
                              {index + 1}
                            </div>
                          </div>
                          <div className="flex-1 text-sm">{suggestion}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </Card>
              </TabsContent>
            </Tabs>

            {/* Action Buttons */}
            <div className="flex gap-2 pt-4 border-t">
              <Button 
                variant="outline" 
                onClick={() => setReviewResult(null)}
                className="flex-1"
              >
                Neue Review
              </Button>
              <Button 
                onClick={performCodeReview} 
                disabled={loading}
                className="flex-1"
              >
                Erneut analysieren
              </Button>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default CodeReviewComponent;