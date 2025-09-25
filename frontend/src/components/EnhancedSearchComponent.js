import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Search, Filter, Clock, TrendingUp } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const EnhancedSearchComponent = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchType, setSearchType] = useState('all');
  const [suggestions, setSuggestions] = useState([]);
  const [searchStats, setSearchStats] = useState(null);

  // Load search statistics on mount
  useEffect(() => {
    loadSearchStats();
  }, []);

  // Load search suggestions as user types
  useEffect(() => {
    if (searchQuery.length >= 2) {
      loadSearchSuggestions(searchQuery);
    } else {
      setSuggestions([]);
    }
  }, [searchQuery]);

  const loadSearchStats = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/search/stats`);
      if (response.data.success) {
        setSearchStats(response.data.stats);
      }
    } catch (error) {
      console.error('Failed to load search stats:', error);
    }
  };

  const loadSearchSuggestions = async (query) => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/search/suggestions`, {
        params: { partial_query: query, limit: 5 }
      });
      if (response.data.success) {
        setSuggestions(response.data.suggestions);
      }
    } catch (error) {
      console.error('Failed to load suggestions:', error);
    }
  };

  const performSearch = async (query = searchQuery) => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await axios.get(`${BACKEND_URL}/api/search`, {
        params: { 
          query: query.trim(), 
          type: searchType,
          limit: 50 
        }
      });

      if (response.data.success) {
        setSearchResults(response.data.results);
      }
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchTypeChange = (type) => {
    setSearchType(type);
    if (searchQuery.trim()) {
      performSearch();
    }
  };

  const getTypeIcon = (type) => {
    const icons = {
      'project': '📁',
      'session': '💬', 
      'file': '📄',
      'chat': '🗨️'
    };
    return icons[type] || '📄';
  };

  const getSeverityColor = (score) => {
    if (score >= 80) return 'bg-green-100 text-green-800';
    if (score >= 60) return 'bg-yellow-100 text-yellow-800';
    if (score >= 40) return 'bg-orange-100 text-orange-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Search className="h-5 w-5" />
          🔍 Enhanced Search
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Volltext-Suche durch alle Projekte und Sessions
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Search Input */}
        <div className="relative">
          <Input
            placeholder="Suche nach Code, Projekten, Sessions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && performSearch()}
            className="pr-10"
          />
          <Button 
            onClick={() => performSearch()}
            size="sm" 
            className="absolute right-1 top-1"
            disabled={loading}
          >
            <Search className="h-4 w-4" />
          </Button>
        </div>

        {/* Search Suggestions */}
        {suggestions.length > 0 && (
          <div className="bg-gray-50 p-3 rounded-md">
            <div className="text-sm font-medium mb-2">Vorschläge:</div>
            <div className="flex flex-wrap gap-2">
              {suggestions.map((suggestion, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setSearchQuery(suggestion);
                    performSearch(suggestion);
                  }}
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* Search Type Tabs */}
        <Tabs value={searchType} onValueChange={handleSearchTypeChange}>
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="all">Alle</TabsTrigger>
            <TabsTrigger value="projects">Projekte</TabsTrigger>
            <TabsTrigger value="sessions">Sessions</TabsTrigger>
            <TabsTrigger value="files">Dateien</TabsTrigger>
            <TabsTrigger value="chat">Chat</TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Search Statistics */}
        {searchStats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{searchStats.total_projects}</div>
              <div className="text-sm text-gray-600">Projekte</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{searchStats.total_sessions}</div>
              <div className="text-sm text-gray-600">Sessions</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{searchStats.total_files}</div>
              <div className="text-sm text-gray-600">Dateien</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{searchStats.total_chat_messages}</div>
              <div className="text-sm text-gray-600">Chat Messages</div>
            </div>
          </div>
        )}

        {/* Search Results */}
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <div className="mt-2 text-sm text-gray-600">Suche läuft...</div>
          </div>
        ) : (
          <ScrollArea className="h-96">
            {searchResults.length > 0 ? (
              <div className="space-y-3">
                {searchResults.map((result) => (
                  <Card key={result.id} className="p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-lg">{getTypeIcon(result.type)}</span>
                          <h3 className="font-semibold text-lg">{result.title}</h3>
                          <Badge 
                            variant="outline" 
                            className={getSeverityColor(result.score)}
                          >
                            {result.score.toFixed(1)}% Match
                          </Badge>
                        </div>
                        <p className="text-gray-600 text-sm mb-2">
                          {result.content.length > 200 
                            ? result.content.substring(0, 200) + '...'
                            : result.content
                          }
                        </p>
                        {result.highlighted_content && (
                          <div className="bg-yellow-50 p-2 rounded text-sm">
                            <div dangerouslySetInnerHTML={{ 
                              __html: result.highlighted_content.replace(/\*\*(.*?)\*\*/g, '<mark>$1</mark>') 
                            }} />
                          </div>
                        )}
                        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                          <span>Typ: {result.type}</span>
                          {result.created_at && (
                            <span className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {new Date(result.created_at).toLocaleDateString('de-DE')}
                            </span>
                          )}
                          {result.metadata.language && (
                            <Badge variant="secondary" className="text-xs">
                              {result.metadata.language}
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            ) : searchQuery && !loading ? (
              <div className="text-center py-8 text-gray-500">
                <Search className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Keine Ergebnisse für "{searchQuery}" gefunden.</p>
                <p className="text-sm">Versuchen Sie andere Suchbegriffe.</p>
              </div>
            ) : null}
          </ScrollArea>
        )}

        {/* Results Summary */}
        {searchResults.length > 0 && (
          <div className="flex items-center justify-between text-sm text-gray-600 pt-4 border-t">
            <span>{searchResults.length} Ergebnisse gefunden</span>
            <span>Durchschnittlicher Match: {(searchResults.reduce((sum, r) => sum + r.score, 0) / searchResults.length).toFixed(1)}%</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default EnhancedSearchComponent;