import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { NgxEchartsDirective } from 'ngx-echarts';

@Component({
  selector: 'app-chart-preview',
  imports: [NgxEchartsDirective],
  templateUrl: './chart-preview.html',
  styleUrl: './chart-preview.css'
})
export class ChartPreview implements OnChanges {
  @Input() jsCode = '';

  chartOption: any = null;
  error = '';

  ngOnChanges(changes: SimpleChanges) {
    if (changes['jsCode'] && this.jsCode) {
      this.parseAndRender();
    }
  }

  parseAndRender() {
    this.error = '';
    this.chartOption = null;

    try {
      const cleaned = this.jsCode
        .replace(/const\s+option\s*=\s*/, '')
        .replace(/;$/, '')
        .trim();

      const option = new Function(`return ${cleaned}`)();
      this.chartOption = option;
    } catch (e) {
      this.error = 'Could not render preview. The generated code may need manual adjustments.';
    }
  }
}