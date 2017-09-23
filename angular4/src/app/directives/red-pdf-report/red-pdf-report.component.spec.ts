import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RedPdfReportComponent } from './red-pdf-report.component';

describe('RedPdfReportComponent', () => {
  let component: RedPdfReportComponent;
  let fixture: ComponentFixture<RedPdfReportComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RedPdfReportComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RedPdfReportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
