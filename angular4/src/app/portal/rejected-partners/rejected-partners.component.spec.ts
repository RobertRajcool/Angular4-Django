import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RejectedPartnersComponent } from './rejected-partners.component';

describe('RejectedPartnersComponent', () => {
  let component: RejectedPartnersComponent;
  let fixture: ComponentFixture<RejectedPartnersComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RejectedPartnersComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RejectedPartnersComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
