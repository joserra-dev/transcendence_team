import { Component, ElementRef, OnDestroy, OnInit, ViewChild, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { Subscription } from 'rxjs';

import { Chat } from '../../../core/services/chat';
import { ChatSocket } from '../../../core/services/chat-socket';
import { Auth } from '../../../core/services/auth';
import { ChatMessage, ChatThread } from '../../../core/models/chat';

@Component({
  selector: 'app-admin-chat',
  imports: [CommonModule, FormsModule, RouterLink, TranslateModule],
  templateUrl: './admin-chat.html',
  styleUrl: './admin-chat.scss',
})
export class AdminChat implements OnInit, OnDestroy {
  @ViewChild('messagesContainer') messagesContainer?: ElementRef<HTMLElement>;

  private chatService = inject(Chat);
  private chatSocket = inject(ChatSocket);
  private authService = inject(Auth);

  threads: ChatThread[] = [];
  messages: ChatMessage[] = [];
  selectedCompanyId: number | null = null;
  newMessage = '';
  isLoadingThreads = true;
  isLoadingMessages = false;
  isSending = false;
  errorMessage = '';
  isSuperAdmin = false;
  backLink = '/admin/dashboard';
  private socketSubs: Subscription[] = [];
  private currentUserId: number | null = null;

  ngOnInit() {
    this.isSuperAdmin = this.authService.isSuperAdmin();
    this.backLink = this.isSuperAdmin ? '/admin/companies' : '/admin/dashboard';
    this.currentUserId = this.authService.getUser()?.id ?? null;
    this.loadThreads();
    this.chatSocket.connect();
    this.socketSubs.push(
      this.chatSocket.onNewMessage().subscribe((message) => this.handleIncomingMessage(message)),
      this.chatSocket.onMessagesRead().subscribe((payload) => this.handleMessagesRead(payload)),
    );
  }

  ngOnDestroy() {
    this.socketSubs.forEach((sub) => sub.unsubscribe());
  }

  get selectedThread(): ChatThread | undefined {
    return this.threads.find((t) => t.companyId === this.selectedCompanyId);
  }

  loadThreads() {
    this.isLoadingThreads = true;
    this.errorMessage = '';

    this.chatService.getThreads().subscribe({
      next: (threads) => {
        this.threads = threads;
        this.isLoadingThreads = false;

        if (!this.selectedCompanyId && threads.length > 0) {
          const withUnread = threads.find((t) => t.unreadCount > 0);
          this.selectThread((withUnread ?? threads[0]).companyId);
        } else if (this.selectedCompanyId) {
          this.loadMessages(this.selectedCompanyId);
        }
      },
      error: () => {
        this.errorMessage = 'ADMIN_CHAT.ERRORS.LOAD_THREADS';
        this.isLoadingThreads = false;
      },
    });
  }

  selectThread(companyId: number) {
    if (this.selectedCompanyId === companyId && this.messages.length > 0) {
      return;
    }
    this.selectedCompanyId = companyId;
    this.loadMessages(companyId);
  }

  loadMessages(companyId: number) {
    this.isLoadingMessages = true;
    this.errorMessage = '';

    this.chatService.getMessages(companyId).subscribe({
      next: (messages) => {
        this.messages = messages;
        this.isLoadingMessages = false;
        this.chatService.markAsRead(companyId).subscribe({
          next: () => {
            const thread = this.threads.find((t) => t.companyId === companyId);
            if (thread) {
              thread.unreadCount = 0;
            }
          },
        });
        this.scrollToBottom();
      },
      error: () => {
        this.errorMessage = 'ADMIN_CHAT.ERRORS.LOAD_MESSAGES';
        this.isLoadingMessages = false;
      },
    });
  }

  sendMessage() {
    const content = this.newMessage.trim();
    if (!content || !this.selectedCompanyId || this.isSending) {
      return;
    }

    this.isSending = true;
    this.chatService.sendMessage(this.selectedCompanyId, content).subscribe({
      next: (message) => {
        this.appendMessageIfNew(message);
        this.newMessage = '';
        this.isSending = false;
        this.updateThreadPreview(message);
        this.scrollToBottom();
      },
      error: () => {
        this.errorMessage = 'ADMIN_CHAT.ERRORS.SEND';
        this.isSending = false;
      },
    });
  }

  onKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  isOwnMessage(message: ChatMessage): boolean {
    return message.senderId === this.currentUserId;
  }

  formatTime(isoDate: string | null): string {
    if (!isoDate) {
      return '';
    }
    const date = new Date(isoDate);
    return date.toLocaleString(undefined, {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  private handleIncomingMessage(message: ChatMessage) {
    this.updateThreadPreview(message);

    const thread = this.threads.find((t) => t.companyId === message.companyId);
    if (thread && message.companyId !== this.selectedCompanyId && message.senderId !== this.currentUserId) {
      thread.unreadCount += 1;
    }

    if (message.companyId !== this.selectedCompanyId) {
      return;
    }

    const isNew = this.appendMessageIfNew(message);
    if (!isNew) {
      return;
    }

    if (message.senderId !== this.currentUserId) {
      this.chatService.markAsRead(message.companyId).subscribe({
        next: () => {
          if (thread) {
            thread.unreadCount = 0;
          }
        },
      });
    }

    this.scrollToBottom();
  }

  private handleMessagesRead(payload: { companyId: number; readerId: number }) {
    if (payload.companyId !== this.selectedCompanyId || payload.readerId === this.currentUserId) {
      return;
    }

    this.messages = this.messages.map((message) =>
      message.senderId === this.currentUserId ? { ...message, isRead: true } : message,
    );
  }

  private appendMessageIfNew(message: ChatMessage): boolean {
    if (this.messages.some((existing) => existing.id === message.id)) {
      return false;
    }
    this.messages = [...this.messages, message];
    return true;
  }

  private updateThreadPreview(message: ChatMessage) {
    const thread = this.threads.find((t) => t.companyId === message.companyId);
    if (thread) {
      thread.lastMessage = message.content;
      thread.lastMessageAt = message.createdAt;
    }
  }

  private scrollToBottom() {
    setTimeout(() => {
      const el = this.messagesContainer?.nativeElement;
      if (el) {
        el.scrollTop = el.scrollHeight;
      }
    }, 50);
  }
}
