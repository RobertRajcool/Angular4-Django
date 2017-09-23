/* tslint:disable:no-unused-variable */
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';

import { LocalitySelectDirective } from './locality-select.directive';

describe('LocalitySelectDirective', () => {
  let component: LocalitySelectDirective;
  let fixture: ComponentFixture<LocalitySelectDirective>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ LocalitySelectDirective ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LocalitySelectDirective);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
