import { Routes } from '@angular/router';
import { Home } from './pages/home/home';
import { TextToChart } from './pages/text-to-chart/text-to-chart';
import { StructuredInput } from './pages/structured-input/structured-input';
import { ImageUpload } from './pages/image-upload/image-upload';

export const routes: Routes = [
  { path: '', component: Home },
  { path: 'text', component: TextToChart },
  { path: 'structured', component: StructuredInput },
  { path: 'image', component: ImageUpload },
  { path: '**', redirectTo: '' }
];