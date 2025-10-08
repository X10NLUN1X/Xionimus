/**
 * Skip Link Component
 * 
 * Allows keyboard users to skip navigation and go directly to main content
 */

import React from 'react';
import { Box, Link } from '@chakra-ui/react';

interface SkipLinkProps {
  href: string;
  children: React.ReactNode;
}

export const SkipLink: React.FC<SkipLinkProps> = ({ href, children }) => {
  return (
    <Link
      href={href}
      position="absolute"
      left="-9999px"
      top="0"
      zIndex="9999"
      bg="blue.500"
      color="white"
      px={4}
      py={2}
      fontSize="sm"
      fontWeight="bold"
      _focus={{
        left: '10px',
        top: '10px',
        outline: '2px solid',
        outlineColor: 'blue.300',
        outlineOffset: '2px',
      }}
      onClick={(e) => {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target instanceof HTMLElement) {
          target.setAttribute('tabindex', '-1');
          target.focus();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }}
    >
      {children}
    </Link>
  );
};

/**
 * Skip Links Container
 * Multiple skip links for complex layouts
 */
export const SkipLinks: React.FC = () => {
  return (
    <Box
      as="nav"
      aria-label="Skip links"
      position="absolute"
      top={0}
      left={0}
      zIndex={9999}
    >
      <SkipLink href="#main-content">Skip to main content</SkipLink>
      <SkipLink href="#navigation">Skip to navigation</SkipLink>
    </Box>
  );
};

export default SkipLink;
