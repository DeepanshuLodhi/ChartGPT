import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ChartService, ChartResponse } from '../../services/chart';
import { CodeOutput } from '../../components/code-output/code-output';
import { ChartPreview } from '../../components/chart-preview/chart-preview';

@Component({
  selector: 'app-structured-input',
  imports: [FormsModule, CodeOutput, ChartPreview],
  templateUrl: './structured-input.html',
  styleUrl: './structured-input.css'
})
export class StructuredInput {
  chartTypes = ['bar', 'line', 'pie', 'scatter', 'radar', 'funnel', 'gauge', 'heatmap', 'candlestick'];
  availableFeatures = ['tooltip', 'legend', 'grid', 'dataZoom', 'toolbox', 'markLine', 'markPoint', 'visualMap'];

  selectedChartType = 'bar';
  selectedFeatures: string[] = ['tooltip', 'legend'];
  dataInput = '';
  loading = false;
  error = '';
  result: ChartResponse | null = null;

  constructor(private chartService: ChartService) {}

  toggleFeature(feature: string) {
    const index = this.selectedFeatures.indexOf(feature);
    if (index === -1) {
      this.selectedFeatures.push(feature);
    } else {
      this.selectedFeatures.splice(index, 1);
    }
  }

  isSelected(feature: string): boolean {
    return this.selectedFeatures.includes(feature);
  }

  generate() {
    this.loading = true;
    this.error = '';
    this.result = null;

    let parsedData = {};
    if (this.dataInput.trim()) {
      try {
        parsedData = JSON.parse(this.dataInput);
      } catch {
        this.error = 'Invalid JSON in data field. Please check your input.';
        this.loading = false;
        return;
      }
    }

    this.chartService.generateFromStructured(
      this.selectedChartType,
      this.selectedFeatures,
      parsedData
    ).subscribe({
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
}