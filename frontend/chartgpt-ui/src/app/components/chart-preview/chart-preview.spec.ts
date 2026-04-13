import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChartPreview } from './chart-preview';

describe('ChartPreview', () => {
  let component: ChartPreview;
  let fixture: ComponentFixture<ChartPreview>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChartPreview]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChartPreview);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
