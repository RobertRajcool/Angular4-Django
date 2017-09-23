import { Component, ViewEncapsulation, OnInit } from '@angular/core';
import { Location } from '@angular/common';

@Component({
  selector: 'app-permission-denied',
  templateUrl: './permission-denied.component.html',
  encapsulation: ViewEncapsulation.None
})
export class PermissionDeniedComponent implements OnInit {

  constructor(private location: Location) { }

  ngOnInit() {
  }

  goBack() {
    this.location.back();
  }
}
