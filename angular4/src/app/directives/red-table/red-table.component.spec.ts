/* tslint:disable:no-unused-variable */
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';

import { RedTableComponent } from './red-table.component';

describe('RedTableComponent', () => {
  let component: RedTableComponent;
  let fixture: ComponentFixture<RedTableComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RedTableComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RedTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
