import { Injectable, inject } from '@angular/core';
import { io, Socket } from 'socket.io-client';
import { Observable, Subject } from 'rxjs';

import { Auth } from './auth';
import { ChatMessage } from '../models/chat';

@Injectable({
  providedIn: 'root',
})
export class ChatSocket {
  private auth = inject(Auth);
  private socket: Socket | null = null;

  private newMessageSubject = new Subject<ChatMessage>();
  private unreadCountSubject = new Subject<number>();
  private messagesReadSubject = new Subject<{ companyId: number; readerId: number }>();

  connect(): void {
    if (!this.auth.isAdmin()) {
      return;
    }

    if (this.socket?.connected) {
      return;
    }

    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }

    const token = sessionStorage.getItem('token');
    if (!token) {
      return;
    }

    // URL_BACK="/" (prod vía nginx) → mismo origen. Si no, URL absoluta del backend.
    const rawBack = (window.env?.URL_BACK || '').replace(/\/$/, '');
    const url = rawBack || window.location.origin;

    this.socket = io(url, {
      path: '/socket.io',
      auth: { token },
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: Infinity,
      reconnectionDelay: 1000,
    });

    this.socket.on('new_message', (message: ChatMessage) => {
      this.newMessageSubject.next(message);
    });

    this.socket.on('unread_count', ({ count }: { count: number }) => {
      this.unreadCountSubject.next(count);
    });

    this.socket.on('messages_read', (payload: { companyId: number; readerId: number }) => {
      this.messagesReadSubject.next(payload);
    });
  }

  disconnect(): void {
    this.socket?.disconnect();
    this.socket = null;
  }

  onNewMessage(): Observable<ChatMessage> {
    return this.newMessageSubject.asObservable();
  }

  onUnreadCount(): Observable<number> {
    return this.unreadCountSubject.asObservable();
  }

  onMessagesRead(): Observable<{ companyId: number; readerId: number }> {
    return this.messagesReadSubject.asObservable();
  }
}
