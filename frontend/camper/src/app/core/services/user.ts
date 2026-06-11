import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { User } from '../models/user';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private http = inject(HttpClient);

  private apiUrl = `${window.env.URL_BACK}/api/users`;

  getMe(): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/me`);
  }

  updateProfile(userData: any): Observable<string> {
    return this.http.put(
      `${this.apiUrl}/update`,
      userData,
      { responseType: 'text' }
    );
  }
}