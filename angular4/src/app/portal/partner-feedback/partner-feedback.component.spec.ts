import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PartnerFeedbackComponent } from './partner-feedback.component';

describe('PartnerFeedbackComponent', () => {
  let component: PartnerFeedbackComponent;
  let fixture: ComponentFixture<PartnerFeedbackComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PartnerFeedbackComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PartnerFeedbackComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
