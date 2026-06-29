export interface ChatThread {
  companyId: number;
  companyName: string;
  adminName: string | null;
  lastMessage: string | null;
  lastMessageAt: string | null;
  unreadCount: number;
}

export interface ChatMessage {
  id: number;
  companyId: number;
  senderId: number;
  senderName: string | null;
  content: string;
  isRead: boolean;
  createdAt: string;
}
