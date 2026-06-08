import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { User } from '../models/user';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:5000/api/users';

  /*
  Obtiene los datos del usuario logueado.
  */
  getMe(): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/me`);
  }

   /*
  Actualizar los datos del usuario logueado.
  */
  updateProfile(userData: any): Observable<string> {
    return this.http.put(`${this.apiUrl}/update`, userData, {
      responseType: 'text' 
    });
  }
}