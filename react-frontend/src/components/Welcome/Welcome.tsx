import { Box, Button, Container, Heading, Text, VStack, useColorModeValue } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';

interface WelcomeProps {
  onGetStarted: () => void;
}

export const Welcome = ({ onGetStarted }: WelcomeProps) => {
  const navigate = useNavigate();
  const bgColor = useColorModeValue('white', 'gray.800');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  const handleGetStarted = () => {
    onGetStarted();
    navigate('/login');
  };

  return (
    <Box minH="100vh" bg="gray.50">
      <Container maxW="container.xl" py={20}>
        <VStack
          spacing={8}
          bg={bgColor}
          p={8}
          borderRadius="xl"
          boxShadow="xl"
          textAlign="center"
        >
          <Heading
            as="h1"
            size="2xl"
            bgGradient="linear(to-r, blue.400, blue.600)"
            bgClip="text"
            fontWeight="extrabold"
          >
            Welcome to IBAL Chat
          </Heading>
          
          <Text fontSize="xl" color={textColor} maxW="2xl">
            Your intelligent learning assistant. 
            Get personalized help, answers to your questions, and guidance on your learning journey.
          </Text>

          <VStack spacing={4} w="full" maxW="md">
            <Button
              size="lg"
              colorScheme="blue"
              w="full"
              onClick={handleGetStarted}
              _hover={{
                transform: 'translateY(-2px)',
                boxShadow: 'lg',
              }}
            >
              Get Started
            </Button>
            
            <Text fontSize="sm" color={textColor}>
              Start your learning journey with IBAL Chat
            </Text>
          </VStack>
        </VStack>
      </Container>
    </Box>
  );
}; 