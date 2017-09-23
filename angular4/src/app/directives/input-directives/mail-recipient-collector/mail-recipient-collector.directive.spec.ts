/* tslint:disable:no-unused-variable */
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';

import { MailRecipientCollectorDirective } from './mail-recipient-collector.directive';

describe('MailRecipientCollectorDirective', () => {
  let component: MailRecipientCollectorDirective;
  let fixture: ComponentFixture<MailRecipientCollectorDirective>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MailRecipientCollectorDirective ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MailRecipientCollectorDirective);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
