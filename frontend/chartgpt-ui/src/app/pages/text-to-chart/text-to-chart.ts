import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ChartService, ChartResponse } from '../../services/chart';
import { CodeOutput } from '../../components/code-output/code-output';
import { ChartPreview } from '../../components/chart-preview/chart-preview';

@Component({
  selector: 'app-text-to-chart',
  imports: [FormsModule, CodeOutput, ChartPreview],
  templateUrl: './text-to-chart.html',
  styleUrl: './text-to-chart.css'
})
export class TextToChart {
  prompt = '';
  loading = false;
  error = '';
  result: ChartResponse | null = null;

  examples = [
    'Bar chart showing monthly sales for Jan to Jun with tooltip and gradient colors',
    'Line chart with smooth curves showing temperature over 7 days with legend',
    'Pie chart showing market share of 5 companies with labels and tooltip',
    'Scatter chart showing correlation between height and weight of 10 people',
    'Stacked bar chart showing quarterly revenue by product category'
  ];

  constructor(private chartService: ChartService) {}

  generate() {
    if (!this.prompt.trim()) return;
    this.loading = true;
    this.error = '';
    this.result = null;

    this.chartService.generateFromText(this.prompt).subscribe({
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

  useExample(example: string) {
    this.prompt = example;
  }
}