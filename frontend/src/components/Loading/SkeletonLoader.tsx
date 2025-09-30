import React from 'react'
import {
  Box,
  Skeleton,
  SkeletonText,
  VStack,
  HStack,
  Card,
  CardBody
} from '@chakra-ui/react'

interface SkeletonLoaderProps {
  type?: 'chat' | 'file-list' | 'workspace' | 'card'
  count?: number
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  type = 'card',
  count = 3
}) => {
  const renderChatSkeleton = () => (
    <VStack spacing={6} align="stretch">
      {Array.from({ length: count }).map((_, i) => (
        <Card key={i}>
          <CardBody>
            <HStack justify="space-between" mb={3}>
              <Skeleton height="20px" width="100px" />
              <Skeleton height="20px" width="60px" />
            </HStack>
            <SkeletonText noOfLines={3} spacing={2} />
          </CardBody>
        </Card>
      ))}
    </VStack>
  )

  const renderFileListSkeleton = () => (
    <VStack spacing={3} align="stretch">
      {Array.from({ length: count }).map((_, i) => (
        <HStack key={i} p={3} borderWidth="1px" borderRadius="md">
          <Skeleton height="40px" width="40px" borderRadius="md" />
          <VStack flex={1} align="start" spacing={2}>
            <Skeleton height="16px" width="60%" />
            <Skeleton height="12px" width="40%" />
          </VStack>
          <HStack spacing={2}>
            <Skeleton height="32px" width="32px" borderRadius="md" />
            <Skeleton height="32px" width="32px" borderRadius="md" />
          </HStack>
        </HStack>
      ))}
    </VStack>
  )

  const renderWorkspaceSkeleton = () => (
    <HStack spacing={0} h="100%" align="stretch">
      <Box w="300px" p={4} borderRightWidth="1px">
        <VStack spacing={2} align="stretch">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} height="32px" borderRadius="md" />
          ))}
        </VStack>
      </Box>
      <Box flex={1} p={4}>
        <VStack spacing={4} align="stretch">
          <Skeleton height="40px" />
          <SkeletonText noOfLines={15} spacing={4} />
        </VStack>
      </Box>
    </HStack>
  )

  const renderCardSkeleton = () => (
    <VStack spacing={4} align="stretch">
      {Array.from({ length: count }).map((_, i) => (
        <Card key={i}>
          <CardBody>
            <VStack align="stretch" spacing={3}>
              <Skeleton height="24px" width="50%" />
              <SkeletonText noOfLines={2} spacing={2} />
              <HStack spacing={3}>
                <Skeleton height="32px" width="80px" />
                <Skeleton height="32px" width="80px" />
              </HStack>
            </VStack>
          </CardBody>
        </Card>
      ))}
    </VStack>
  )

  switch (type) {
    case 'chat':
      return renderChatSkeleton()
    case 'file-list':
      return renderFileListSkeleton()
    case 'workspace':
      return renderWorkspaceSkeleton()
    default:
      return renderCardSkeleton()
  }
}