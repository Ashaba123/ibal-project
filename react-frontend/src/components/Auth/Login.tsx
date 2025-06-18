import { Box, Button, Heading, Text, VStack, useToast, Input, FormControl, FormLabel, FormErrorMessage } from '@chakra-ui/react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService, healthService } from '../../services/api';

export const Login = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    if (authService.isAuthenticated()) {
      navigate('/');
    }
  }, [navigate]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // First check if backend is available
      await healthService.checkHealth();
      
      // Attempt to login
      const response = await authService.login(username, password);
      console.log('Login successful:', response);
      navigate('/');
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to login');
      toast({
        title: 'Login Error',
        description: error instanceof Error ? error.message : 'Failed to login',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box
      minH="100vh"
      display="flex"
      alignItems="center"
      justifyContent="center"
      bg="gray.50"
    >
      <VStack
        as="form"
        onSubmit={handleLogin}
        spacing={8}
        p={8}
        bg="white"
        borderRadius="lg"
        boxShadow="lg"
        maxW="md"
        w="full"
      >
        <Heading size="lg">Welcome to IBAL Chat</Heading>
        <Text textAlign="center" color="gray.600">
          Please login to start chatting
        </Text>

        <FormControl isInvalid={!!error}>
          <FormLabel>Username</FormLabel>
          <Input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter your username"
          />
        </FormControl>

        <FormControl isInvalid={!!error}>
          <FormLabel>Password</FormLabel>
          <Box position="relative">
            <Input
              id="password"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              pr="4.5rem"
            />
            <Button
              type="button"
              className="password-toggle"
              onClick={() => setShowPassword((prev) => !prev)}
              position="absolute"
              right="0.5rem"
              top="50%"
              transform="translateY(-50%)"
              size="sm"
              variant="ghost"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  setShowPassword((prev) => !prev);
                }
              }}
            >
              {showPassword ? 'Hide' : 'Show'}
            </Button>
          </Box>
          {error && <FormErrorMessage>{error}</FormErrorMessage>}
        </FormControl>

        <Button
          type="submit"
          colorScheme="blue"
          size="lg"
          w="full"
          isLoading={isLoading}
        >
          Login
        </Button>
      </VStack>
    </Box>
  );
}; 