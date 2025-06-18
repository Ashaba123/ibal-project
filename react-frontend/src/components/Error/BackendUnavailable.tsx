import { Box, Container, Heading, Text, VStack, Button, useColorModeValue } from '@chakra-ui/react';
import { FaServer } from 'react-icons/fa';

interface BackendUnavailableProps {
  backendUrl: string;
  error?: string;
}

export const BackendUnavailable = ({ backendUrl, error }: BackendUnavailableProps) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  const handleRetry = () => {
    window.location.reload();
  };

  return (
    <Box minH="100vh" bg="gray.50" py={20}>
      <Container maxW="container.md">
        <VStack
          spacing={8}
          bg={bgColor}
          p={8}
          borderRadius="xl"
          boxShadow="xl"
          textAlign="center"
        >
          <Box
            as={FaServer}
            size="64px"
            color="red.500"
          />
          
          <Heading size="xl" color="red.500">
            Chat Service Unavailable
          </Heading>

          <VStack spacing={4} align="stretch">
            <Text fontSize="lg" color={textColor}>
              We're unable to connect to the chat service at:
            </Text>
            <Box
              bg="gray.100"
              p={4}
              borderRadius="md"
              fontFamily="monospace"
              fontSize="sm"
            >
              {backendUrl}
            </Box>

            <Text fontSize="lg" color={textColor}>
              To start the chat service:
            </Text>
            <Box
              bg="gray.700"
              p={4}
              borderRadius="md"
              color="white"
              fontFamily="monospace"
              fontSize="sm"
            >
              docker-compose up
            </Box>

            {error && (
              <Box
                bg="red.50"
                p={4}
                borderRadius="md"
                color="red.600"
                fontSize="sm"
              >
                Error details: {error}
              </Box>
            )}

            <Button
              colorScheme="blue"
              size="lg"
              onClick={handleRetry}
              mt={4}
            >
              Retry Connection
            </Button>
          </VStack>
        </VStack>
      </Container>
    </Box>
  );
}; 