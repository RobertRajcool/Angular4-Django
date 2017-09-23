import { Component, OnInit, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'app-users',
  encapsulation: ViewEncapsulation.None,
  template: '<router-outlet></router-outlet>',
})
export class UsersComponent implements OnInit {

  constructor() { }

  ngOnInit() {    
  }

}
