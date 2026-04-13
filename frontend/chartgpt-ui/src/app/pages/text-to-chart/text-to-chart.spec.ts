import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TextToChart } from './text-to-chart';

describe('TextToChart', () => {
  let component: TextToChart;
  let fixture: ComponentFixture<TextToChart>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TextToChart]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TextToChart);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
