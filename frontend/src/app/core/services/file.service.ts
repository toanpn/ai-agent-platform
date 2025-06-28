import { Injectable } from '@angular/core';
import { ApiService } from './api.service';
import { Observable } from 'rxjs';
import { AgentFile } from './agent.service';

@Injectable({
  providedIn: 'root'
})
export class FileService {

  constructor(private apiService: ApiService) { }

  uploadFile(agentId: number, file: File): Observable<AgentFile> {
    const formData = new FormData();
    formData.append('file', file);

    return this.apiService.post<AgentFile>(`/file/upload/${agentId}`, formData);
  }

  deleteFile(fileId: number): Observable<any> {
    return this.apiService.delete(`/file/${fileId}`);
  }
} 