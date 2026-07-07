import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface UserFriend {
  id: number;
  email: string;
  nombrePersona: string;
  apellidosPersona: string;
  avatar: string;
  role: string;
}

@Injectable({
  providedIn: 'root'
})
export class FriendService {
  private http = inject(HttpClient);
  private apiUrl = environment.urlBack;

  listFriends(): Observable<UserFriend[]> {
    return this.http.get<UserFriend[]>(`${this.apiUrl}/api/friends`);
  }

  addFriend(friendId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/friends`, { friend_id: friendId });
  }

  removeFriend(friendId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/api/friends/${friendId}`);
  }
}
