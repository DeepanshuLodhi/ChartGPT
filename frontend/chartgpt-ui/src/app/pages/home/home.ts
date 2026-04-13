import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-home',
  imports: [RouterLink],
  templateUrl: './home.html',
  styleUrl: './home.css'
})
export class Home {
  features = [
    {
      icon: '💬',
      title: 'Text to Chart',
      description: 'Describe your chart in plain English and get ready-to-use ECharts code instantly.',
      route: '/text',
      label: 'Try Text Input'
    },
    {
      icon: '🎛️',
      title: 'Structured Input',
      description: 'Select chart type, features and data using a guided form interface.',
      route: '/structured',
      label: 'Try Structured Input'
    },
    {
      icon: '🖼️',
      title: 'Image to Chart',
      description: 'Upload a chart image and get the equivalent ECharts configuration code.',
      route: '/image',
      label: 'Try Image Upload'
    }
  ];
}