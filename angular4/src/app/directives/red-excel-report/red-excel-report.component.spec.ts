import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RedExcelReportComponent } from './red-excel-report.component';

describe('RedExcelReportComponent', () => {
  let component: RedExcelReportComponent;
  let fixture: ComponentFixture<RedExcelReportComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RedExcelReportComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RedExcelReportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
