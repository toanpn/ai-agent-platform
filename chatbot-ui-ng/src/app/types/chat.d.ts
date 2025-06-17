export interface SendMessageRequest {
    message: string;
    sessionId?: number;
    agentName?: string;
}

export interface ChatMessage {
    id: number;
    content: string;
    role: 'user' | 'assistant';
    agentName?: string;
    createdAt: Date;
}

export interface ChatSession {
    id: number;
    title?: string;
    isActive: boolean;
    createdAt: Date;
    messages: ChatMessage[];
}

export interface ChatResponse {
    response: string;
    agentName: string;
    sessionId: number;
    timestamp: Date;
}

export interface ChatHistory {
    sessions: ChatSession[];
    totalCount: number;
    page: number;
    pageSize: number;
} 