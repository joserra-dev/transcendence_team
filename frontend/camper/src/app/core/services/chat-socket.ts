import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { io, Socket } from 'socket.io-client';

import { ChatMessage, ChatThread } from '../models/chat';

@Injectable({
  providedIn: 'root',
})
export class ChatSocket {
  private socket: Socket | null = null;
  private readonly newMessageSubject = new Subject<ChatMessage>();
  private readonly threadUpdatedSubject = new Subject<ChatThread>();
  private readonly unreadCountSubject = new Subject<number>();
  private readonly messagesReadSubject = new Subject<{ companyId: number; readerId: number }>();

  connect(): void {
    if (this.socket?.connected || !this.isAdminUser()) {
      return;
    }

    const token = sessionStorage.getItem('token');
    if (!token) {
      return;
    }

    this.socket = io(this.resolveSocketUrl(), {
      path: '/socket.io',
      transports: ['websocket', 'polling'],
      auth: { token },
      reconnection: true,
      reconnectionAttempts: 10,
      reconnectionDelay: 2000,
    });

    this.socket.on('new_message', (message: ChatMessage) => {
      this.newMessageSubject.next(message);
    });

    this.socket.on('thread_updated', (thread: ChatThread) => {
      this.threadUpdatedSubject.next(thread);
    });

    this.socket.on('unread_count', (data: { count: number }) => {
      this.unreadCountSubject.next(data.count);
    });

    this.socket.on('messages_read', (data: { companyId: number; readerId: number }) => {
      this.messagesReadSubject.next(data);
    });
  }

  disconnect(): void {
    this.socket?.disconnect();
    this.socket = null;
  }

  joinThread(companyId: number): void {
    this.socket?.emit('join_thread', { companyId });
  }

  onNewMessage(): Observable<ChatMessage> {
    return this.newMessageSubject.asObservable();
  }

  onThreadUpdated(): Observable<ChatThread> {
    return this.threadUpdatedSubject.asObservable();
  }

  onUnreadCount(): Observable<number> {
    return this.unreadCountSubject.asObservable();
  }

  onMessagesRead(): Observable<{ companyId: number; readerId: number }> {
    return this.messagesReadSubject.asObservable();
  }

  private resolveSocketUrl(): string {
    const urlBack = (window.env?.URL_BACK || '').replace(/\/$/, '');
    if (!urlBack || urlBack === '') {
      return window.location.origin;
    }
    return urlBack;
  }

  private isAdminUser(): boolean {
    const userStr = sessionStorage.getItem('user');
    if (!userStr) {
      return false;
    }

    try {
      const user = JSON.parse(userStr);
      return user.role === 'admin' || user.role === 'super_admin' || user.admin === true;
    } catch {
      return false;
    }
  }
}
