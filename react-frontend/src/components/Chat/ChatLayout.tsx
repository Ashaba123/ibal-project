import { Box, Flex, Button, useToast } from '@chakra-ui/react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChatWindow } from './ChatWindow';
import { authService, chatService } from '../../services/api';
import { ChatSession } from '../../types';

export const ChatLayout = () => {
  const [session, setSession] = useState<ChatSession | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();
  const toast = useToast();

  useEffect(() => {
    const initializeChat = async () => {
      try {
        // Get or create a chat session
        const sessions = await chatService.getSessions();
        if (sessions.length > 0) {
          setSession(sessions[0]);
        } else {
          const newSession = await chatService.createSession();
          setSession(newSession);
        }
      } catch (error) {
        console.error('Error initializing chat:', error);
        toast({
          title: 'Error initializing chat',
          description: 'Please try again',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
      } finally {
        setIsLoading(false);
      }
    };

    initializeChat();
  }, [toast]);

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" h="100vh">
        Loading chat...
      </Box>
    );
  }

  if (!session) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" h="100vh">
        Error: No chat session available
      </Box>
    );
  }

  return (
    <Flex direction="column" h="100vh">
      <Box
        bg="blue.500"
        color="white"
        p={4}
        display="flex"
        justifyContent="space-between"
        alignItems="center"
      >
        <Box>IBAL Chat</Box>
        <Button
          variant="ghost"
          color="white"
          _hover={{ bg: 'blue.600' }}
          onClick={handleLogout}
        >
          Logout
        </Button>
      </Box>
      <Flex flex="1" justifyContent="center" alignItems="center" bg="gray.100">
        <Box w="100%" maxW="400px" boxShadow="lg" borderRadius="lg" bg="white" p={4}>
          <ChatWindow sessionId={session.id} />
        </Box>
      </Flex>
    </Flex>
  );
}; 