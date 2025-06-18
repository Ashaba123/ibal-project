import React, { useState, useEffect, useRef } from 'react';
import { Box, VStack, Input, Button, Text, useToast } from '@chakra-ui/react';
import { ChatMessage } from '../../types';
import { chatService } from '../../services/api';
import { websocketService } from '../../services/websocket';
import { WebSocketService } from '../../services/websocket';

interface ChatWindowProps {
  sessionId: string;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ sessionId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const wsRef = useRef<WebSocketService | null>(null);
  const toast = useToast();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      wsRef.current = new WebSocketService(token);
      wsRef.current.connect();

      // Subscribe to messages
      const unsubscribe = wsRef.current.onMessage((message) => {
        setMessages(prev => [...prev, message]);
        if (message.type === 'loading' && message.status === 'completed') {
          setIsLoading(false);
        }
      });

      return () => {
        unsubscribe();
        wsRef.current?.disconnect();
      };
    }
  }, []);

  const handleSend = () => {
    if (!input.trim()) return;

    setIsLoading(true);
    wsRef.current?.sendMessage(input);
    setInput('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box
      h="100vh"
      display="flex"
      flexDirection="column"
      bg="gray.50"
      p={4}
    >
      <VStack
        flex={1}
        spacing={4}
        overflowY="auto"
        bg="white"
        p={4}
        borderRadius="lg"
        boxShadow="sm"
      >
        {messages.map((message, index) => (
          <Box
            key={index}
            alignSelf={message.is_user_message ? 'flex-end' : 'flex-start'}
            bg={message.is_user_message ? 'blue.500' : 'gray.200'}
            color={message.is_user_message ? 'white' : 'black'}
            p={3}
            borderRadius="lg"
            maxW="70%"
          >
            <Text>{message.content}</Text>
          </Box>
        ))}
        {isLoading && (
          <Box alignSelf="flex-start" p={3}>
            <Text color="gray.500">AI is typing...</Text>
          </Box>
        )}
      </VStack>

      <Box mt={4} display="flex" gap={2}>
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          disabled={isLoading}
        />
        <Button
          colorScheme="blue"
          onClick={handleSend}
          isLoading={isLoading}
          disabled={!input.trim()}
        >
          Send
        </Button>
      </Box>
    </Box>
  );
}; 