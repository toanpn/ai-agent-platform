import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { SendMessageRequest, ChatResponse, ChatHistory } from '../types/chat';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private http = inject(HttpClient);
  private apiUrl = '/api/chat'; // Replace with your actual API URL

  sendMessage(request: SendMessageRequest): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.apiUrl}/message`, request);
  }

  getChatHistory(page: number, pageSize: number): Observable<ChatHistory> {
    return this.http.get<ChatHistory>(`${this.apiUrl}/history?page=${page}&pageSize=${pageSize}`);
  }
}
