import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ChartResponse {
  javascript: string;
  typescript: string;
  retrieved_context?: string[];
  description?: string;
}

@Injectable({
  providedIn: 'root'
})
export class ChartService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  generateFromText(prompt: string): Observable<ChartResponse> {
    return this.http.post<ChartResponse>(`${this.apiUrl}/generate/text`, { prompt });
  }

  generateFromStructured(chartType: string, features: string[], data: any): Observable<ChartResponse> {
    return this.http.post<ChartResponse>(`${this.apiUrl}/generate/structured`, {
      chart_type: chartType,
      features,
      data
    });
  }

  generateFromImage(file: File): Observable<ChartResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<ChartResponse>(`${this.apiUrl}/image/upload`, formData);
  }
}