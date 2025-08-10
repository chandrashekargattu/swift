'use client';

import dynamic from 'next/dynamic';

// Dynamically import Advanced AI Chatbot to avoid SSR issues
const AdvancedChatbot = dynamic(() => import('./AdvancedChatbot'), {
  ssr: false,
  loading: () => null
});

export default function ChatbotWrapper() {
  return <AdvancedChatbot />;
}
