import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StructuredInput } from './structured-input';

describe('StructuredInput', () => {
  let component: StructuredInput;
  let fixture: ComponentFixture<StructuredInput>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StructuredInput]
    })
    .compileComponents();

    fixture = TestBed.createComponent(StructuredInput);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
