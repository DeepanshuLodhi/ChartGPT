import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-code-output',
  imports: [],
  templateUrl: './code-output.html',
  styleUrl: './code-output.css'
})
export class CodeOutput {
  @Input() javascript = '';
  @Input() typescript = '';

  activeTab: 'javascript' | 'typescript' = 'javascript';
  copied = false;

  get activeCode(): string {
    return this.activeTab === 'javascript' ? this.javascript : this.typescript;
  }

  copyCode() {
    navigator.clipboard.writeText(this.activeCode).then(() => {
      this.copied = true;
      setTimeout(() => this.copied = false, 2000);
    });
  }
}