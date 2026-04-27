const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const chatApi = {
  async sendMessage(message, conversationId = null) {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    return response.json();
  },

  async generateImage(prompt) {
    const response = await fetch(`${API_BASE_URL}/images`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      throw new Error('Failed to generate image');
    }

    return response.json();
  },

  async getHealth() {
    const response = await fetch(`${API_BASE_URL.replace('/api/v1', '')}/health`);
    return response.json();
  }
};
