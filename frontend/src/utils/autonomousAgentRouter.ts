/**
 * Autonomous Agent Router
 * Intelligently detects which agent should handle the user's message
 * Similar to Emergent's autonomous agent selection
 */

import { AgentType } from '../services/agentService';

interface AgentDetectionResult {
  agent: AgentType | null;
  confidence: number; // 0-1
  reason: string;
}

/**
 * Detect keywords and patterns in user message
 */
const detectKeywords = (message: string, keywords: string[]): number => {
  const lowerMessage = message.toLowerCase();
  let score = 0;
  
  for (const keyword of keywords) {
    if (lowerMessage.includes(keyword.toLowerCase())) {
      score += 1;
    }
  }
  
  return score / keywords.length;
};

/**
 * Check if message contains code
 */
const containsCode = (message: string): boolean => {
  // Check for code blocks
  if (message.includes('```')) return true;
  
  // Check for common code patterns
  const codePatterns = [
    /def\s+\w+\s*\(/,  // Python function
    /function\s+\w+\s*\(/,  // JavaScript function
    /class\s+\w+/,  // Class definition
    /import\s+\w+/,  // Import statement
    /from\s+\w+\s+import/,  // Python import
    /const\s+\w+\s*=/,  // Const declaration
    /let\s+\w+\s*=/,  // Let declaration
    /var\s+\w+\s*=/,  // Var declaration
  ];
  
  return codePatterns.some(pattern => pattern.test(message));
};

/**
 * Check if message contains error/exception
 */
const containsError = (message: string): boolean => {
  const errorPatterns = [
    /error:/i,
    /exception:/i,
    /traceback/i,
    /stack trace/i,
    /\w+Error:/,  // NameError, TypeError, etc.
    /failed/i,
    /not working/i,
    /bug/i,
    /issue/i,
  ];
  
  return errorPatterns.some(pattern => pattern.test(message));
};

/**
 * Autonomous agent detection
 * Returns the best agent to handle the message
 */
export const detectAgent = (message: string): AgentDetectionResult => {
  const scores: { agent: AgentType; score: number; reason: string }[] = [];
  
  // Research Agent Detection
  const researchKeywords = [
    'research', 'find', 'search', 'what is', 'tell me about', 
    'explain', 'information', 'learn', 'discover', 'investigate',
    'latest', 'trends', 'news', 'compare', 'difference between'
  ];
  const researchScore = detectKeywords(message, researchKeywords);
  if (researchScore > 0 && !containsCode(message)) {
    scores.push({
      agent: 'research',
      score: researchScore * 0.9,
      reason: 'Message appears to be a research/information query'
    });
  }
  
  // Code Review Agent Detection
  const codeReviewKeywords = [
    'review', 'check', 'improve', 'feedback', 'suggestions',
    'best practices', 'code quality', 'refactor', 'optimize'
  ];
  const codeReviewScore = detectKeywords(message, codeReviewKeywords);
  if (containsCode(message) && codeReviewScore > 0) {
    scores.push({
      agent: 'code_review',
      score: (codeReviewScore * 0.5 + 0.5) * 0.95,
      reason: 'Message contains code and review-related keywords'
    });
  }
  
  // Testing Agent Detection
  const testingKeywords = [
    'test', 'unit test', 'testing', 'pytest', 'jest',
    'test case', 'test coverage', 'write tests'
  ];
  const testingScore = detectKeywords(message, testingKeywords);
  if (testingScore > 0 && containsCode(message)) {
    scores.push({
      agent: 'testing',
      score: (testingScore * 0.6 + 0.4) * 0.9,
      reason: 'Message requests test generation for code'
    });
  }
  
  // Documentation Agent Detection
  const docKeywords = [
    'document', 'documentation', 'docs', 'docstring',
    'comment', 'readme', 'api docs', 'explain code'
  ];
  const docScore = detectKeywords(message, docKeywords);
  if (docScore > 0 && containsCode(message)) {
    scores.push({
      agent: 'documentation',
      score: (docScore * 0.5 + 0.5) * 0.85,
      reason: 'Message requests documentation for code'
    });
  }
  
  // Debugging Agent Detection
  const debugKeywords = [
    'debug', 'fix', 'error', 'broken', 'not working',
    'exception', 'crash', 'fails', 'problem'
  ];
  const debugScore = detectKeywords(message, debugKeywords);
  const hasError = containsError(message);
  if (debugScore > 0 || hasError) {
    scores.push({
      agent: 'debugging',
      score: (debugScore * 0.4 + (hasError ? 0.6 : 0.4)) * 0.95,
      reason: hasError 
        ? 'Message contains error/exception that needs debugging'
        : 'Message requests debugging assistance'
    });
  }
  
  // Security Agent Detection
  const securityKeywords = [
    'security', 'vulnerability', 'secure', 'sql injection',
    'xss', 'csrf', 'authentication', 'authorization',
    'exploit', 'attack', 'penetration', 'audit'
  ];
  const securityScore = detectKeywords(message, securityKeywords);
  if (securityScore > 0 && containsCode(message)) {
    scores.push({
      agent: 'security',
      score: (securityScore * 0.6 + 0.4) * 0.9,
      reason: 'Message requests security analysis of code'
    });
  }
  
  // Performance Agent Detection
  const perfKeywords = [
    'performance', 'optimize', 'slow', 'fast', 'speed',
    'efficiency', 'memory', 'cpu', 'bottleneck', 'profiling'
  ];
  const perfScore = detectKeywords(message, perfKeywords);
  if (perfScore > 0 && containsCode(message)) {
    scores.push({
      agent: 'performance',
      score: (perfScore * 0.6 + 0.4) * 0.85,
      reason: 'Message requests performance optimization'
    });
  }
  
  // Fork Agent Detection
  const forkKeywords = [
    'fork', 'repository', 'repo', 'github', 'clone',
    'branch', 'git', 'version control'
  ];
  const forkScore = detectKeywords(message, forkKeywords);
  if (forkScore > 0.3) {
    scores.push({
      agent: 'fork',
      score: forkScore * 0.8,
      reason: 'Message requests repository/GitHub operations'
    });
  }
  
  // Sort by score and return best match
  scores.sort((a, b) => b.score - a.score);
  
  if (scores.length > 0 && scores[0].score > 0.4) {
    return {
      agent: scores[0].agent,
      confidence: scores[0].score,
      reason: scores[0].reason
    };
  }
  
  // No confident match - return null for regular chat
  return {
    agent: null,
    confidence: 0,
    reason: 'No specific agent pattern detected - using regular chat'
  };
};

/**
 * Get a user-friendly name for the agent
 */
export const getAgentDisplayName = (agent: AgentType): string => {
  const names: Record<AgentType, string> = {
    research: 'Research Agent',
    code_review: 'Code Review Agent',
    testing: 'Testing Agent',
    documentation: 'Documentation Agent',
    debugging: 'Debugging Agent',
    security: 'Security Agent',
    performance: 'Performance Agent',
    fork: 'Fork Agent',
  };
  
  return names[agent];
};

/**
 * Should we show the autonomous detection to user?
 */
export const shouldShowDetection = (confidence: number): boolean => {
  return confidence > 0.6;  // Only show if we're fairly confident
};
