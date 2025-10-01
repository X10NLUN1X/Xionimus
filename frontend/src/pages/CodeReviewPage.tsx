import React, { useState } from 'react';
import {
  Box, VStack, Heading, Button, Textarea, Input, Select, FormControl, FormLabel,
  useToast, Spinner, Text, Badge, Accordion, AccordionItem, AccordionButton,
  AccordionPanel, AccordionIcon, Divider
} from '@chakra-ui/react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

export const CodeReviewPage: React.FC = () => {
  const [code, setCode] = useState('');
  const [title, setTitle] = useState('');
  const [language, setLanguage] = useState('python');
  const [reviewScope, setReviewScope] = useState('full');
  const [openaiKey, setOpenaiKey] = useState('');
  const [anthropicKey, setAnthropicKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [review, setReview] = useState<any>(null);
  const toast = useToast();

  const submitReview = async () => {
    if (!code.trim()) {
      toast({ title: 'Error', description: 'Please enter code to review', status: 'error' });
      return;
    }
    
    if (!openaiKey && !anthropicKey) {
      toast({ title: 'Error', description: 'Please provide at least one API key', status: 'error' });
      return;
    }

    setIsLoading(true);
    try {
      const apiKeys: any = {};
      if (openaiKey) apiKeys.openai = openaiKey;
      if (anthropicKey) apiKeys.anthropic = anthropicKey;

      const response = await axios.post(`${API_BASE}/api/code-review/review/submit`, {
        title: title || 'Code Review',
        code,
        language,
        review_scope: reviewScope,
        api_keys: apiKeys
      });

      const reviewId = response.data.review_id;
      
      // Fetch review results
      const reviewResponse = await axios.get(`${API_BASE}/api/code-review/review/${reviewId}`);
      setReview(reviewResponse.data);
      
      toast({
        title: 'Review Complete!',
        description: `Found ${reviewResponse.data.findings.length} issues`,
        status: 'success'
      });
    } catch (error: any) {
      toast({
        title: 'Review Failed',
        description: error.response?.data?.detail || error.message,
        status: 'error'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'red';
      case 'high': return 'orange';
      case 'medium': return 'yellow';
      case 'low': return 'blue';
      default: return 'gray';
    }
  };

  return (
    <Box p={6} maxW="1400px" mx="auto">
      <Heading mb={6}>🔍 Xionimus Code Review System</Heading>
      
      <VStack spacing={6} align="stretch">
        {/* Input Section */}
        <Box bg="white" p={6} borderRadius="lg" shadow="sm">
          <Heading size="md" mb={4}>Submit Code for Review</Heading>
          
          <VStack spacing={4}>
            <FormControl>
              <FormLabel>Review Title</FormLabel>
              <Input 
                placeholder="e.g., Auth Module Review" 
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </FormControl>

            <FormControl>
              <FormLabel>Code to Review</FormLabel>
              <Textarea 
                placeholder="Paste your code here..." 
                value={code}
                onChange={(e) => setCode(e.target.value)}
                rows={15}
                fontFamily="mono"
              />
            </FormControl>

            <Box display="flex" gap={4} w="full">
              <FormControl flex={1}>
                <FormLabel>Language</FormLabel>
                <Select value={language} onChange={(e) => setLanguage(e.target.value)}>
                  <option value="python">Python</option>
                  <option value="javascript">JavaScript</option>
                  <option value="typescript">TypeScript</option>
                  <option value="java">Java</option>
                </Select>
              </FormControl>

              <FormControl flex={1}>
                <FormLabel>Review Scope</FormLabel>
                <Select value={reviewScope} onChange={(e) => setReviewScope(e.target.value)}>
                  <option value="full">Full Review (All 4 Agents)</option>
                  <option value="code_analysis">Code Analysis Only</option>
                  <option value="debug">Debug Only</option>
                  <option value="enhancement">Enhancement Only</option>
                  <option value="test">Test Analysis Only</option>
                </Select>
              </FormControl>
            </Box>

            <FormControl>
              <FormLabel>OpenAI API Key (Optional)</FormLabel>
              <Input 
                type="password"
                placeholder="sk-proj-..." 
                value={openaiKey}
                onChange={(e) => setOpenaiKey(e.target.value)}
              />
            </FormControl>

            <FormControl>
              <FormLabel>Anthropic API Key (Optional)</FormLabel>
              <Input 
                type="password"
                placeholder="sk-ant-..." 
                value={anthropicKey}
                onChange={(e) => setAnthropicKey(e.target.value)}
              />
            </FormControl>

            <Button 
              colorScheme="blue" 
              size="lg" 
              w="full" 
              onClick={submitReview}
              isLoading={isLoading}
              loadingText="Analyzing Code..."
            >
              {isLoading ? <Spinner mr={2} /> : null}
              Start Review
            </Button>
          </VStack>
        </Box>

        {/* Results Section */}
        {review && (
          <Box bg="white" p={6} borderRadius="lg" shadow="sm">
            <Heading size="md" mb={4}>Review Results</Heading>
            
            <Box mb={4} p={4} bg="gray.50" borderRadius="md">
              <Text fontSize="lg" fontWeight="bold">{review.review.title}</Text>
              <Text color="gray.600">Quality Score: {review.review.quality_score || 'N/A'}/100</Text>
              <Text color="gray.600" fontSize="sm">Review Scope: {review.review.review_scope}</Text>
              <Box mt={2} display="flex" gap={2} flexWrap="wrap">
                <Badge colorScheme="red">Critical: {review.review.critical_issues}</Badge>
                <Badge colorScheme="orange">High: {review.review.high_issues}</Badge>
                <Badge colorScheme="yellow">Medium: {review.review.medium_issues}</Badge>
                <Badge colorScheme="blue">Low: {review.review.low_issues}</Badge>
              </Box>
            </Box>

            <Divider my={4} />

            <Accordion allowMultiple>
              {review.findings.map((finding: any, idx: number) => (
                <AccordionItem key={finding.id}>
                  <AccordionButton>
                    <Box flex="1" textAlign="left">
                      <Badge colorScheme={getSeverityColor(finding.severity)} mr={2}>
                        {finding.severity.toUpperCase()}
                      </Badge>
                      <Text as="span" fontWeight="semibold">{finding.title}</Text>
                      {finding.line_number && (
                        <Text as="span" ml={2} fontSize="sm" color="gray.500">
                          Line {finding.line_number}
                        </Text>
                      )}
                    </Box>
                    <AccordionIcon />
                  </AccordionButton>
                  <AccordionPanel>
                    <VStack align="stretch" spacing={3}>
                      <Box>
                        <Text fontWeight="bold" fontSize="sm" color="gray.600">Description:</Text>
                        <Text>{finding.description}</Text>
                      </Box>
                      
                      {finding.recommendation && (
                        <Box>
                          <Text fontWeight="bold" fontSize="sm" color="gray.600">Recommendation:</Text>
                          <Text color="green.600">{finding.recommendation}</Text>
                        </Box>
                      )}
                      
                      {finding.fix_code && (
                        <Box>
                          <Text fontWeight="bold" fontSize="sm" color="gray.600">Suggested Fix:</Text>
                          <Box 
                            as="pre" 
                            p={3} 
                            bg="gray.800" 
                            color="green.300" 
                            borderRadius="md" 
                            overflow="auto"
                            fontSize="sm"
                          >
                            {finding.fix_code}
                          </Box>
                        </Box>
                      )}

                      <Box fontSize="xs" color="gray.500">
                        Agent: {finding.agent_name} | Category: {finding.category}
                      </Box>
                    </VStack>
                  </AccordionPanel>
                </AccordionItem>
              ))}
            </Accordion>

            {review.findings.length === 0 && (
              <Text color="green.600" textAlign="center" py={4}>
                ✅ No issues found! Code looks good.
              </Text>
            )}
          </Box>
        )}
      </VStack>
    </Box>
  );
};
