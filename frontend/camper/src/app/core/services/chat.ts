import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { ChatMessage, ChatThread } from '../models/chat';

@Injectable({
  providedIn: 'root',
})
export class Chat {
  private http = inject(HttpClient);

  private apiUrl = `${window.env.URL_BACK}/api/chat`;

  getUnreadCount(): Observable<{ count: number }> {
    return this.http.get<{ count: number }>(`${this.apiUrl}/unread-count`);
  }

  getThreads(): Observable<ChatThread[]> {
    return this.http.get<ChatThread[]>(`${this.apiUrl}/threads`);
  }

  getMessages(companyId: number): Observable<ChatMessage[]> {
    return this.http.get<ChatMessage[]>(`${this.apiUrl}/threads/${companyId}/messages`);
  }

  sendMessage(companyId: number, content: string): Observable<ChatMessage> {
    return this.http.post<ChatMessage>(`${this.apiUrl}/threads/${companyId}/messages`, { content });
  }

  markAsRead(companyId: number): Observable<{ mensaje: string }> {
    return this.http.post<{ mensaje: string }>(`${this.apiUrl}/threads/${companyId}/read`, {});
  }
}
