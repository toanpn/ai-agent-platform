export interface LoginRequest {
    email: string;
    password?: string;
}

export interface AuthResponse {
    token: string;
    expiresAt: Date;
    user: User;
}

export interface User {
    id: number;
    email: string;
    firstName?: string;
    lastName?: string;
    department?: string;
    isActive: boolean;
    createdAt: Date;
} 