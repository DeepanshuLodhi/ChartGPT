import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CodeOutput } from './code-output';

describe('CodeOutput', () => {
  let component: CodeOutput;
  let fixture: ComponentFixture<CodeOutput>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CodeOutput]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CodeOutput);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
