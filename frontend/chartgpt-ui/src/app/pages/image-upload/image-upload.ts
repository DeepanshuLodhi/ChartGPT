import { Component } from '@angular/core';
import { ChartService, ChartResponse } from '../../services/chart';
import { CodeOutput } from '../../components/code-output/code-output';
import { ChartPreview } from '../../components/chart-preview/chart-preview';

@Component({
  selector: 'app-image-upload',
  imports: [CodeOutput, ChartPreview],
  templateUrl: './image-upload.html',
  styleUrl: './image-upload.css'
})
export class ImageUpload {
  selectedFile: File | null = null;
  previewUrl: string | null = null;
  loading = false;
  error = '';
  result: ChartResponse | null = null;
  dragOver = false;

  constructor(private chartService: ChartService) {}

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.setFile(input.files[0]);
    }
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.dragOver = true;
  }

  onDragLeave() {
    this.dragOver = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.dragOver = false;
    if (event.dataTransfer?.files[0]) {
      this.setFile(event.dataTransfer.files[0]);
    }
  }

  setFile(file: File) {
    const allowed = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
    if (!allowed.includes(file.type)) {
      this.error = 'Only JPEG, PNG, WEBP and GIF images are supported.';
      return;
    }
    this.selectedFile = file;
    this.error = '';
    this.result = null;
    const reader = new FileReader();
    reader.onload = (e) => {
      this.previewUrl = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }

  generate() {
    if (!this.selectedFile) return;
    this.loading = true;
    this.error = '';
    this.result = null;

    this.chartService.generateFromImage(this.selectedFile).subscribe({
      next: (res) => {
        this.result = res;
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.detail || 'Something went wrong. Please try again.';
        this.loading = false;
      }
    });
  }

  clearFile() {
    this.selectedFile = null;
    this.previewUrl = null;
    this.result = null;
    this.error = '';
  }
}